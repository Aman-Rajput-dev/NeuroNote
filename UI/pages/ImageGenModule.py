import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from langchain_huggingface import HuggingFaceEmbeddings
import os
import random

def image_generator(df,query_embedding,caption_embeddings):
    # Step 5: Calculate cosine similarity
    similarities = cosine_similarity([query_embedding], caption_embeddings)[0]

    # Step 6: Get top 3 most similar captions
    top_indices = similarities.argsort()[-3:][::-1]
    top_images = df.iloc[top_indices]['image'].tolist()
    top_captions = df.iloc[top_indices]['captions'].tolist()

    # Define base directory for images
    image_base_dir = r"C:\Users\student\Desktop\202418003\Minor Project\Class 12\dataset\images"

    # Get full paths and print them
    print("\nTop 3 matched image paths:")
    image_paths = []
    for img_name in top_images:
        full_path = os.path.join(image_base_dir, img_name)
        image_paths.append(full_path)
        print(full_path)

    return image_paths