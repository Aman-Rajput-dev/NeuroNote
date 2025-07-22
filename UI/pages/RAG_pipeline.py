import os
import re
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaLLM



# 1. Parse OCR text from "Text/" folder
def parse_folder(folder_path):
    """
    Parses all .txt files in the specified folder and extracts OCR content.

    The function reads each .txt file in the given folder, extracts text between 
    <CONTENT_FROM_OCR> tags that are associated with <PAGE> numbers, and returns 
    a list of Document objects containing the extracted text and metadata.

    Each Document includes:
        - page_content (str): The stripped OCR text.
        - metadata (dict): Contains the page number and the source file name.

    Parameters:
        folder_path (str): The path to the folder containing .txt files to parse.

    Returns:
        list: A list of Document objects with extracted page content and metadata.
    """
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
    """
    Splits a list of Document objects into smaller chunks while preserving metadata.

    This function uses a RecursiveCharacterTextSplitter to divide the content of 
    each Document into smaller overlapping text chunks. The metadata from the 
    original document is retained for each chunk.

    Parameters:
        docs (list): A list of Document objects to be split. Each Document should 
                     have 'page_content' and 'metadata' attributes.

    Returns:
        list: A list of new Document objects, each containing a chunk of text and 
              the original metadata.
    """
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
    """
    Creates a FAISS vector store from a list of Document objects using sentence embeddings.

    This function uses the HuggingFace embedding model 'all-MiniLM-L6-v2' to compute 
    dense vector representations of the input documents. It then indexes these embeddings 
    using FAISS for efficient similarity search.

    Parameters:
        docs (list): A list of Document objects to be embedded and indexed.

    Returns:
        FAISS: A FAISS vector store containing the embedded documents.
    """
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return FAISS.from_documents(docs, embedding_model)



# 4. Load local LLaMA 3.2 model from Ollama
def load_llama_ollama():
    """
    Loads the LLaMA model using the Ollama interface.

    This function initializes and returns an instance of the LLaMA 3.2 model
    using the Ollama backend. The model name must match the name available 
    locally (as listed by the `ollama list` command).

    Returns:
        OllamaLLM: An instance of the LLaMA model ready for inference via Ollama.
    """
    return OllamaLLM(model="llama3.2:1b")