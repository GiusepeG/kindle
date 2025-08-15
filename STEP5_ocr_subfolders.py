import easyocr
import os
import sys

# Add the path to the script's directory to sys.path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

# Create an OCR reader instance
# The model is downloaded to ~/.EasyOCR/
reader = easyocr.Reader(['en'])  # Assuming the text is in English; change 'en' to the appropriate language code as needed

# Base folder containing the chapter subdirectories
base_folder = 'STEP4_screenshots_divided_by_chapters'

# Output folder for the text files
output_folder = 'STEP5_ocr'
os.makedirs(output_folder, exist_ok=True)

print(f"Processing subdirectories in: {base_folder}")

# Iterate over each item in the base folder
for item_name in sorted(os.listdir(base_folder)):
    item_path = os.path.join(base_folder, item_name)

    # Check if the item is a directory
    if os.path.isdir(item_path):
        subfolder_path = item_path
        print(f"--- Processing folder: {subfolder_path} ---")

        # Path for the output text file, named after the subfolder
        output_file_path = os.path.join(output_folder, f"{item_name}.txt")
        
        # Initialize an empty string to hold all the extracted text for the current subfolder
        extracted_text = ''

        # Get a sorted list of image files
        try:
            image_files = sorted([f for f in os.listdir(subfolder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))])
        except FileNotFoundError:
            print(f"Error: Subdirectory not found: {subfolder_path}")
            continue

        if not image_files:
            print(f"No image files found in {subfolder_path}")
            continue

        # Iterate over each image file in the subfolder
        for filename in image_files:
            file_path = os.path.join(subfolder_path, filename)
            print(f"  - Reading image: {filename}")
            
            try:
                # Perform OCR on the image file
                result = reader.readtext(file_path)
                
                # Extract text from the OCR result and append it to the extracted_text string
                for detection in result:
                    text = detection[1]  # The text content is at index 1
                    extracted_text += text + ' '
                
                # Add a newline to separate text from different images
                extracted_text += '\n'

            except Exception as e:
                print(f"    Error processing file {filename}: {e}")
        
        # Save the extracted text to the output text file for the current subfolder
        if extracted_text.strip():
            print(f"  - Saving extracted text to: {output_file_path}")
            try:
                with open(output_file_path, 'w', encoding='utf-8') as file:
                    file.write(extracted_text.strip())
            except IOError as e:
                print(f"    Error writing to file {output_file_path}: {e}")
        else:
            print(f"  - No text was extracted from the images in {subfolder_path}")

print("\nText extraction for all subfolders completed.")
