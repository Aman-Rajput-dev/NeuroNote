import os

# Specify the path to the directory
directory = r'C:\Users\student\Desktop\202418003\Minor Project\Class 12\dataset\images'  # Change this to your directory path

# Loop through all files in the directory
for filename in os.listdir(directory):
    if filename.lower().endswith(('.jpg', '.png')):
        # Construct the new file name
        new_filename = "Class_12_" + filename

        # Get the full path of the old and new file names
        old_file = os.path.join(directory, filename)
        new_file = os.path.join(directory, new_filename)

        # Rename the file
        os.rename(old_file, new_file)

print("Renaming completed.")
