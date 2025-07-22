import streamlit as st
import os
import pandas as pd
from datetime import datetime

# LangChain + HuggingFace + Ollama Imports
from langchain.chains import RetrievalQA
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

# User-defined modules
from greet_module import get_greeting, gradient_text_html
from ImageGenModule import image_generator
from Stream_Md import stream_markdown
from RAG_pipeline import parse_folder, split_docs_with_metadata, create_vectorstore, load_llama_ollama
from Model_Prompt import system_prompt
from db_utils import insert_note_to_db, fetch_filtered_notes


# --- SETUP: RAG Pipeline ---
raw_docs = parse_folder(r"C:\Users\student\Desktop\202418003\Minor Project\Class 12\UI\pages\Text_test")
split_docs = split_docs_with_metadata(raw_docs)
vectorstore = create_vectorstore(split_docs)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# Embeddings for image captions
df = pd.read_csv(r"C:\Users\student\Desktop\202418003\Minor Project\Class 12\dataset\captions\captions_v2.csv", encoding='latin-1')
embedder = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
captions = df['captions'].tolist()
caption_embeddings = embedder.embed_documents(captions)

# Load LLM
llm = load_llama_ollama()

# Prompt Template
prompt_template = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(system_prompt),
    HumanMessagePromptTemplate.from_template(
        "Use the following textbook content to answer the student's question.\n\n"
        "{context}\n\n"
        "Question: {question}"
    )
])

# QA Chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    return_source_documents=True,
    chain_type_kwargs={"prompt": prompt_template},
    chain_type="stuff"
)


def response_generator(query):
    result = qa_chain(query)
    answer = result['result']
    source = result['source_documents']
    return answer, source


# --- MAIN APP ---
def main():
    st.set_page_config(page_title="NeuroNote", page_icon=":books:", layout="wide")
    st.markdown(gradient_text_html, unsafe_allow_html=True)
    st.title(get_greeting())
    st.header("How can I help you today with your studies?")

    # Sidebar
    st.sidebar.title("📌 Quick Access")
    page = st.sidebar.selectbox("Select a page:", ["Home", "Chat History", "Formula"])

    # Dummy images (used on first load)
    dummy_images = [
        r"C:\Users\student\Desktop\202418003\Minor Project\Class 12\UI\Class_12_Figure 1.1.jpg",
        r"C:\Users\student\Desktop\202418003\Minor Project\Class 12\UI\Class_12_Figure 1.2.jpg",
        r"C:\Users\student\Desktop\202418003\Minor Project\Class 12\UI\Class_12_Figure 1.3.jpg"
    ]
    if "img_list" not in st.session_state:
        st.session_state.img_list = dummy_images

    # --- PAGE LOGIC ---
    if page == "Home":
        prompt = st.chat_input("What is up?")
        col1, col2 = st.columns(2)

        with col1:
            messages = st.container()

            if prompt:
                messages.chat_message("user").write(prompt)
                response, source = response_generator(prompt)
                query_embedding = embedder.embed_query(response)

                # Generate image list
                st.session_state.img_list = image_generator(df, query_embedding, caption_embeddings)

                source_str = ""
                for doc in source:
                    page_info = f"➡️ Page {doc.metadata['page_number']} from {doc.metadata['source']}\n"
                    excerpt = f"Excerpt: {doc.page_content[:100]}...\n\n"
                    source_str += page_info + excerpt

                final_str = f"🧠 Answer\n\n\n {response} \n\n\n 📄 Sources \n\n\n {source_str}"

                # Stream markdown gradually
                messages.chat_message("assistant").markdown(" ")
                stream_markdown(final_str, delay=0.5)

                # Insert into DB
                insert_success = insert_note_to_db(prompt, response, source_str, st.session_state.img_list)
                if insert_success:
                    st.success("✅ Saved to your study notes!")
                else:
                    st.error("⚠️ Failed to save the note.")

        with col2:
            cols = st.columns(len(st.session_state.img_list))
            st.button('Add to Note', use_container_width=True, type='primary', help='Adds the question/answer pair to the notes app')
            for col, img_url in zip(cols, st.session_state.img_list):
                with col:
                    st.image(img_url, caption=os.path.basename(img_url))

    elif page == "Chat History":
        st.subheader("📚 Your Study Notes")

        # Sidebar Filters
        st.sidebar.markdown("### 🔍 Filter Your Notes")
        keyword = st.sidebar.text_input("Search by keyword")
        start_date = st.sidebar.date_input("Start date")
        end_date = st.sidebar.date_input("End date")

        start_dt = datetime.combine(start_date, datetime.min.time()) if start_date else None
        end_dt = datetime.combine(end_date, datetime.max.time()) if end_date else None

        notes = fetch_filtered_notes(start_dt, end_dt, keyword)

        if not notes:
            st.info("No notes found for the selected filters.")
        else:
            for idx, (prompt, response, source, img_list, timestamp) in enumerate(notes):
                with st.expander(f"📝 Note {idx+1} — {timestamp.strftime('%Y-%m-%d')} — {prompt}"):
                    st.markdown(f"**🧠 Question:** {prompt}")
                    st.markdown(f"**✅ Answer:** {response}")
                    st.markdown(f"**📄 Sources:**\n\n{source}")
                    if img_list:
                        st.markdown("**🖼️ Related Images:**")
                        img_cols = st.columns(len(img_list))
                        for col, img_path in zip(img_cols, img_list):
                            with col:
                                st.image(img_path, use_container_width=True)

    elif page == "Formula":
        st.info("🧮 Formula page coming soon! (Placeholder)")

if __name__ == "__main__":
    main()
