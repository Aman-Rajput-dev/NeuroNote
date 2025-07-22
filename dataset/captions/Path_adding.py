import pandas as pd
import os
import re

image_folder = r"C:\Users\student\Desktop\202418003\Minor Project\Class 12\dataset\images"

df = pd.read_csv(r"C:\Users\student\Desktop\202418003\Minor Project\Class 12\dataset\captions\captions_v3.csv",encoding='ISO-8859-1')

# Function to extract chapter and figure numbers (supports suffixes like 'a', 'b')
def sort_key(filename):
    match = re.search(r'Figure\s+(\d+)\.(\d+)([a-z]*)', filename, re.IGNORECASE)
    if match:
        chapter = int(match.group(1))              # e.g., 1
        figure = int(match.group(2))               # e.g., 12
        suffix = match.group(3).lower()            # e.g., 'a', or ''
        suffix_val = sum((ord(c) - ord('a') + 1) * (0.001 ** (i + 1)) for i, c in enumerate(suffix))
        return (chapter, figure + suffix_val)
    return (float('inf'), float('inf'))  # Push unmatched to the end

# List all image files
image_files = [f for f in os.listdir(image_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

# Sort using the new key
sorted_files = sorted(image_files, key=sort_key)

# Join with folder path
sorted_image_paths = [os.path.join(image_folder, f) for f in sorted_files]

# Print sorted paths
for path in sorted_image_paths:
    print(path)

df["image_path"] = sorted_image_paths
df.to_csv(".captions_v4.csv")