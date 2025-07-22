import os
import csv
import pandas as pd

def extract_filenames_to_csv(directory_path, output_csv):
    # Get list of files in the directory
    try:
        files = os.listdir(directory_path)
    except FileNotFoundError:
        print(f"Error: Directory '{directory_path}' not found.")
        return
    except PermissionError:
        print(f"Error: Permission denied for directory '{directory_path}'.")
        return

    # Filter out directories, keep only files
    filenames = [f for f in files if os.path.isfile(os.path.join(directory_path, f))]
    df =  pd.DataFrame(filenames,columns=["image"])
    print(df)
    df.to_csv("captions.csv",index=False)


# Example usage
if __name__ == "__main__":
    # Specify the directory to scan (modify this path as needed)
    directory = r"C:\Users\student\Desktop\202418003\Minor Project\Class 12\dataset\images"  # Current directory
    output_file = "filenames.csv"
    extract_filenames_to_csv(directory, output_file)