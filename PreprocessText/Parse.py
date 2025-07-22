import os
import re
from langchain.schema import Document


def parse_folder(folder_path):
    all_docs = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            with open(os.path.join(folder_path, filename), 'r', encoding='utf-8') as f:
                text = f.read()
                # Extract page and content
                matches = re.findall(r"<PAGE(\d+)>\s*<CONTENT_FROM_OCR>(.*?)</CONTENT_FROM_OCR>", text, re.DOTALL)
                for page_number, content in matches:
                    all_docs.append(Document(
                        page_content=content.strip(),
                        metadata={"page_number": int(page_number), "source": filename}
                    ))
    return all_docs
 
ls = parse_folder("PreprocessText\Text_test")
print(ls)