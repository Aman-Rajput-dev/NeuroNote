import streamlit as st
from langchain.chains import RetrievalQA
import os
import pandas as pd
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate


#User Defined modules
from greet_module import get_greeting
from greet_module import gradient_text_html
from ImageGenModule import image_generator
from Stream_Md import stream_markdown
from RAG_pipeline import parse_folder,split_docs_with_metadata,create_vectorstore,load_llama_ollama
from Model_Prompt import system_prompt

# Streamed response emulator
def response_generator(query):
    """
    Generates a response from the QA chain based on the provided query.

    Parameters:
        query (str): The user input or question to be passed to the QA chain.

    Returns:
        str: The generated response obtained from the QA chain's output.
    """
    result = qa_chain(query)
    answer = result['result']
    source = result['source_documents']
    return answer,source



# RAG Pipeline Call
raw_docs = parse_folder(r"C:\Users\student\Desktop\202418003\Minor Project\Class 12\UI\pages\Text_test")
split_docs = split_docs_with_metadata(raw_docs)
vectorstore = create_vectorstore(split_docs)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

#Embeddings for captions
df = pd.read_csv(r"C:\Users\student\Desktop\202418003\Minor Project\Class 12\dataset\captions\captions_v2.csv", encoding='latin-1')  # Assumes 'image_name' and 'caption' columns
embedder = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

captions = df['captions'].tolist() # Step 3: Convert all captions to embeddings
caption_embeddings = embedder.embed_documents(captions)
img_list = []

llm = load_llama_ollama()

#Creating a prompt template using the system_prompt 
prompt_template = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(system_prompt),
    HumanMessagePromptTemplate.from_template("Use the following textbook content to answer the student's question.\n\n"
    "{context}\n\n"
    "Question: {question}"
)
])

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    return_source_documents=True,
    chain_type_kwargs={"prompt": prompt_template},
    chain_type="stuff"
)



def main():
    # Set up dummy images
    dummy_images = [
        r"C:\Users\student\Desktop\202418003\Minor Project\Class 12\UI\Class_12_Figure 1.1.jpg",
        r"C:\Users\student\Desktop\202418003\Minor Project\Class 12\UI\Class_12_Figure 1.2.jpg",
        r"C:\Users\student\Desktop\202418003\Minor Project\Class 12\UI\Class_12_Figure 1.3.jpg"
    ]
    # Initialize session state
    if "img_list" not in st.session_state:
        st.session_state.img_list = dummy_images



    st.set_page_config(page_title="NeuroNote",
                        page_icon=":books:",
                        layout="wide"
    )

    st.markdown(gradient_text_html, unsafe_allow_html=True)
    st.title(get_greeting())
    st.header("How can I help you today with your studies?")
    st.sidebar.title("📌 Quick Access")
    page = st.sidebar.selectbox("Select a page:", ["Home", "Chat History", "Formula"])
    
    prompt = st.chat_input("What is up?")


    col1, col2 = st.columns(2)

    with col1:

        messages = st.container()
        if prompt:
            messages.chat_message("user").write(prompt)
            response,source = response_generator(prompt)
            query_embedding = embedder.embed_query(response)

            # Generate new images and update session state
            st.session_state.img_list = image_generator(df, query_embedding, caption_embeddings)

            source_str = ""
            for doc in source:

                page_info = f"➡️ Page {doc.metadata['page_number']} from {doc.metadata['source']}\n"
                excerpt = f"Excerpt: {doc.page_content[:100]}...\n\n"
                source_str += page_info + excerpt

            final_str = f"🧠 Answer\n\n\n {response} \n\n\n 📄 Sources \n\n\n {source_str}"

            # Stream markdown gradually
            messages.chat_message("assistant").markdown(" ")  # Optional empty init
            stream_markdown(final_str, delay=0.5)  # Customize delay if needed            

            # Insert to PostgreSQL here
            from db_utils import insert_note_to_db
            insert_success = insert_note_to_db(prompt, response, source_str, st.session_state.img_list)
            if insert_success:
                st.success("✅ Saved to your study notes!")
            else:
                st.error("⚠️ Failed to save the note.")

        
        

    with col2:
        
        
        cols = st.columns(len(st.session_state.img_list)) # Creates one column per image
        st.button('Add to Note',use_container_width=True,type='primary',help='Adds the question/answer pair to the notes app')
        # Display images horizontally
        for col, img_url in zip(cols, st.session_state.img_list):
            with col:
                st.image(img_url, caption=os.path.basename(img_url)
                         
        
)
            

if __name__ == "__main__":
    main()