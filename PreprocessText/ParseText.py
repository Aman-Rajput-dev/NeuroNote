import os
import re
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain_community.llms import Ollama  # for llama3.2

# 1. Parse OCR text from "Text/" folder
def parse_folder(folder_path):
    docs = []
    for file in os.listdir(folder_path):
        if file.endswith(".txt"):
            with open(os.path.join(folder_path, file), "r", encoding="utf-8") as f:
                content = f.read()
                matches = re.findall(r"<PAGE(\d+)>\s*<CONTENT_FROM_OCR>(.*?)</CONTENT_FROM_OCR>", content, re.DOTALL)
                for page_num, text in matches:
                    docs.append(Document(
                        page_content=text.strip(),
                        metadata={"page_number": int(page_num), "source": file}
                    ))
    return docs

# 2. Split into chunks with metadata
def split_docs_with_metadata(docs):
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    all_chunks = []
    for doc in docs:
        chunks = splitter.split_text(doc.page_content)
        for chunk in chunks:
            all_chunks.append(Document(
                page_content=chunk,
                metadata=doc.metadata
            ))
    return all_chunks

# 3. Create vector store using local embeddings
def create_vectorstore(docs):
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return FAISS.from_documents(docs, embedding_model)

# 4. Load local LLaMA 3.2 model from Ollama
def load_llama_ollama():
    return Ollama(model="llama3.2")  # Must match the local model name in `ollama list`

# 5. Main RAG flow
def main():
    print("🔍 Loading documents...")
    raw_docs = parse_folder("PreprocessText\Text_test")
    split_docs = split_docs_with_metadata(raw_docs)
    vectorstore = create_vectorstore(split_docs)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    llm = load_llama_ollama()

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,
        chain_type="stuff"
    )

    while True:
        query = input("\n🔎 Ask a question (or type 'exit'): ")
        if query.lower() == "exit":
            break

        result = qa_chain(query)
        print("\n🧠 Answer:\n", result['result'])

        print("\n📄 Sources:")
        for doc in result['source_documents']:
            print(f"➡️ Page {doc.metadata['page_number']} from {doc.metadata['source']}")
            print(f"Excerpt: {doc.page_content}...\n")

if __name__ == "__main__":
    main()
