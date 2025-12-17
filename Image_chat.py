import os
import faiss
import torch
import pandas as pd
from PIL import Image
from torchvision import transforms
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import subprocess
import json

# -------------------------------
# CONFIG
# -------------------------------
CSV_PATH = r"C:\Users\hr150\Downloads\Minor Project\dataset\captions\captions_v5.csv"
EMB_PATH = "embeddings.index"
MODEL_NAME = "clip-ViT-B-32"     # or "clip-ViT-L-14"
VISION_LLM = "qwen3-vl:2b"      # ollama vision model
TEXT_LLM = "llama3.2:1b"              # ollama text model
TOP_K = 5

# -------------------------------
# LOAD CLIP MODEL
# -------------------------------
print("Loading CLIP model...")
clip_model = SentenceTransformer(MODEL_NAME)
preprocess = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor()
])

# -------------------------------
# LOAD DATA
# -------------------------------
df = pd.read_csv(CSV_PATH)

image_paths = df["image_path"].tolist()
captions = df["caption"].tolist()

# -------------------------------
# BUILD / LOAD VECTOR STORE
# -------------------------------
if os.path.exists(EMB_PATH):
    print("Loading FAISS index...")
    index = faiss.read_index(EMB_PATH)
else:
    print("Building FAISS index...")

    # Generate embeddings
    embeddings = []
    for img_path in tqdm(image_paths):
        try:
            img = Image.open(img_path).convert("RGB")
            emb = clip_model.encode(img, convert_to_numpy=True)
            embeddings.append(emb)
        except:
            embeddings.append([0]*512)  # fallback

    embeddings = torch.tensor(embeddings).numpy()

    # Create FAISS index
    d = embeddings.shape[1]
    index = faiss.IndexFlatL2(d)
    index.add(embeddings)

    # Save index
    faiss.write_index(index, EMB_PATH)
    print("Embeddings saved.")

# -------------------------------
# FUNCTION — Vision Caption via OLLAMA
# -------------------------------
def ollama_vision_caption(image_path):
    prompt = "Describe this image in one detailed biology-focused sentence."

    result = subprocess.run(
    ["ollama", "run", VISION_LLM],
    input=json.dumps({
        "prompt": prompt,
        "images": [image_path]
    }),
    text=True,
    encoding="utf-8",
    errors="ignore",
    capture_output=True)

    return result.stdout.strip()

# -------------------------------
# FUNCTION — LLM Explanation via OLLAMA
# -------------------------------
def ollama_generate_explanation(context):
    result = subprocess.run(
    f"ollama run {TEXT_LLM}",
    input=context,
    text=True,
    encoding="utf-8",
    errors="ignore",
    shell=True,
    capture_output=True
)


    return result.stdout.strip()

# -------------------------------
# MAIN INFERENCE PIPELINE
# -------------------------------
def explain_image(user_image):

    # Step 1: Embed the user image
    print("\nEmbedding user image...")
    img = Image.open(user_image).convert("RGB")
    user_emb = clip_model.encode(img, convert_to_numpy=True)

    # Step 2: Retrieve top-K similar images
    print("Retrieving similar images...")
    D, I = index.search(user_emb.reshape(1, -1), TOP_K)

    retrieved_info = []
    for idx in I[0]:
        retrieved_info.append({
            "image_path": image_paths[idx],
            "caption": captions[idx]
        })

    # Step 3: Vision caption using Ollama
    print("Generating vision caption...")
    vision_caption = ollama_vision_caption(user_image)

    # Step 4: Build RAG prompt
    rag_context = f"""
You are an expert Biology Tutor AI.

A user uploaded an image.

### Vision Model Caption:
{vision_caption}

### Retrieved Knowledge from Biology Database:
"""

    for item in retrieved_info:
        rag_context += f"- {item['caption']}\n"

    rag_context += """

### Task:
Explain the image in accurate biological terms.
Do NOT hallucinate. Use ONLY the retrieved knowledge + visual caption.

Output a clear explanation.
"""

    # Step 5: Generate final explanation
    print("Generating final explanation...")
    final_output = ollama_generate_explanation(rag_context)

    return {
        "vision_caption": vision_caption,
        "retrieved": retrieved_info,
        "explanation": final_output
    }


# -------------------------------
# RUN TEST
# -------------------------------
if __name__ == "__main__":
    test_img = r"C:\Users\hr150\Downloads\Minor Project\dataset\images\Class_12_Figure 8.8.png"    # change to your test image

    out = explain_image(test_img)

    print("\n\n===== FINAL OUTPUT =====")
    print("Vision Caption:", out["vision_caption"])
    print("\nRetrieved Captions:")
    for r in out["retrieved"]:
        print("-", r["caption"])
    print("\nFinal Explanation:")
    print(out["explanation"])
