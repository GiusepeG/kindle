import os
import argparse
from pynput import mouse
import pyautogui
import time
import tkinter as tk
from tkinter import simpledialog
import shutil
import easyocr
import google.generativeai as genai
import sys

# --- Directory Configuration ---
# Centralized configuration for all required directories.
# Using a dictionary to make it easy to manage and access paths.
DIR_CONFIG = {
    "config": "config",
    "screenshots": "screenshots",
    "chapter_markers": "chapter_markers",
    "ocr_output": "ocr_output",
    "final_text": "final_corrected_text",
    "mouse_coords_file": os.path.join("config", "mouse_clicks.txt"),
}

def create_directories():
    """
    Creates all the necessary directories if they don't already exist.
    """
    print("Creating necessary directories...")
    for key, path in DIR_CONFIG.items():
        # The 'mouse_coords_file' is a file, not a directory, so we skip it.
        if key != "mouse_coords_file":
            try:
                os.makedirs(path, exist_ok=True)
                print(f"  - Directory '{path}' is ready.")
            except OSError as e:
                print(f"Error creating directory {path}: {e}")
                # Depending on the desired error handling, you might want to exit.
                # For now, just printing the error.

# --- Step 1: Mouse Configuration ---
def configure_mouse():
    """
    Captures 10 mouse clicks to define screen regions for screenshots.
    The coordinates are saved to the file specified in DIR_CONFIG.
    """
    print("--- Mouse Configuration (10 Clicks) ---")
    print("This script will guide you to capture 10 mouse clicks.")

    click_coordinates = []

    instructions = [
        # Left Column Clicks
        "LEFT column, TOP-LEFT corner:", "LEFT column, TOP-RIGHT corner:",
        "LEFT column, BOTTOM-LEFT corner:", "LEFT column, BOTTOM-RIGHT corner:",
        # Right Column Clicks
        "RIGHT column, TOP-LEFT corner:", "RIGHT column, TOP-RIGHT corner:",
        "RIGHT column, BOTTOM-LEFT corner:", "RIGHT column, BOTTOM-RIGHT corner:",
        # Navigation Buttons
        "PREVIOUS page button:", "NEXT page button:"
    ]

    click_count = 0

    def on_click(x, y, button, pressed):
        nonlocal click_count
        if pressed:
            click_coordinates.append((x, y))
            print(f"> Click {click_count + 1}/{len(instructions)} registered at ({x}, {y}).")
            click_count += 1
            if click_count < len(instructions):
                print(f"\n{click_count + 1}. {instructions[click_count]}")
            else:
                print("\nAll coordinates captured. Saving to file...")
                return False

    # Display first instruction
    print(f"1. {instructions[0]}")

    with mouse.Listener(on_click=on_click) as listener:
        listener.join()

    # Save coordinates
    coords_file = DIR_CONFIG['mouse_coords_file']
    try:
        with open(coords_file, 'w') as f:
            for x, y in click_coordinates:
                f.write(f"{x},{y}\n")
        print(f"Coordinates saved to '{coords_file}'.")
    except IOError as e:
        print(f"Error saving coordinates to file: {e}")


# --- Step 2: Screenshot Capture ---
def capture_screenshots():
    """
    Takes screenshots of two columns on the screen and saves them.
    """
    coords_file = DIR_CONFIG['mouse_coords_file']
    if not os.path.exists(coords_file):
        print(f"Coordinates file not found at '{coords_file}'.")
        response = input("Would you like to run the mouse configuration now? (y/n): ").lower()
        if response == 'y':
            configure_mouse()
        else:
            print("Screenshot capture cancelled.")
            return

    try:
        with open(coords_file, 'r') as f:
            lines = f.readlines()
            coords = [tuple(map(int, line.strip().split(','))) for line in lines]
        if len(coords) < 10:
            print(f"Error: Expected 10 coordinates, but found {len(coords)}.")
            return
    except (IOError, ValueError) as e:
        print(f"Error reading or parsing coordinates file: {e}")
        return

    num_pages = _get_number_of_pages_from_user()
    if not num_pages:
        print("Operation cancelled by user.")
        return

    screenshots_folder = DIR_CONFIG['screenshots']
    _clear_folder(screenshots_folder)

    print("\nYou have 5 seconds to switch to your reader window...")
    time.sleep(5)

    _take_screenshots_for_pages(coords, num_pages, screenshots_folder)
    print("\nNext step: Divide screenshots by chapter.")

def _get_number_of_pages_from_user():
    """Shows an input box to ask for the number of pages."""
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    num_pages = simpledialog.askinteger("Input", "How many times to click 'Next Page'?", parent=root, minvalue=1)
    root.destroy()
    return num_pages

def _clear_folder(folder):
    """Deletes all files in the specified folder."""
    print(f"Clearing the '{folder}' directory...")
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        if os.path.isfile(file_path):
            os.unlink(file_path)

def _take_screenshots_for_pages(coords, num_pages, folder):
    """Takes screenshots of two columns and advances pages."""
    left_col_region = _get_bounding_box(coords[0:4])
    right_col_region = _get_bounding_box(coords[4:8])
    next_button = coords[9]

    screenshot_num = 1
    for i in range(num_pages):
        print(f"\nProcessing page {i + 1}/{num_pages}...")

        # Left column
        left_filename = os.path.join(folder, f"page_{str(screenshot_num).zfill(4)}.png")
        pyautogui.screenshot(left_filename, region=left_col_region)
        print(f"  - Saved {left_filename}")
        screenshot_num += 1

        # Right column
        right_filename = os.path.join(folder, f"page_{str(screenshot_num).zfill(4)}.png")
        pyautogui.screenshot(right_filename, region=right_col_region)
        print(f"  - Saved {right_filename}")
        screenshot_num += 1

        if i < num_pages - 1:
            pyautogui.click(next_button)
            time.sleep(1.5)

def _get_bounding_box(points):
    """Calculates the bounding box from four points."""
    x_coords = [p[0] for p in points]
    y_coords = [p[1] for p in points]
    left = min(x_coords)
    top = min(y_coords)
    width = max(x_coords) - left
    height = max(y_coords) - top
    return (left, top, width, height)


# --- Step 3: Divide Screenshots by Chapter ---
def divide_screenshots_by_chapter():
    """
    Organizes screenshots into chapter subfolders based on marker files.
    """
    screenshots_dir = DIR_CONFIG['screenshots']
    markers_dir = DIR_CONFIG['chapter_markers']
    dest_dir = os.path.join(DIR_CONFIG['screenshots'], 'chapters') # Store chapters inside screenshots folder

    print("--- Manual Step: Chapter Division ---")
    print(f"Please copy the first screenshot of each chapter into the '{markers_dir}' folder.")
    input("Press Enter to continue once you have placed the marker files...")

    if not os.listdir(markers_dir):
        print(f"No marker files found in '{markers_dir}'. Aborting division.")
        return

    all_screenshots = sorted([f for f in os.listdir(screenshots_dir) if f.endswith('.png')])
    chapter_markers = sorted([f for f in os.listdir(markers_dir) if f.endswith('.png')])

    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    for i, marker in enumerate(chapter_markers):
        chapter_num = i + 1
        chapter_folder = os.path.join(dest_dir, f"{chapter_num:02d}")
        os.makedirs(chapter_folder, exist_ok=True)

        try:
            start_index = all_screenshots.index(marker)
        except ValueError:
            print(f"Warning: Marker '{marker}' not found in screenshots. Skipping.")
            continue

        end_index = len(all_screenshots)
        if i + 1 < len(chapter_markers):
            next_marker = chapter_markers[i+1]
            try:
                end_index = all_screenshots.index(next_marker)
            except ValueError:
                print(f"Warning: Next marker '{next_marker}' not found. Chapter will run to the end.")

        chapter_files = all_screenshots[start_index:end_index]

        print(f"Copying {len(chapter_files)} files for Chapter {chapter_num:02d}...")
        for filename in chapter_files:
            shutil.copy2(os.path.join(screenshots_dir, filename), os.path.join(chapter_folder, filename))

    print("\nChapter division complete. Next step: Perform OCR.")


# --- Step 4: OCR Processing ---
def perform_ocr():
    """
    Performs OCR on all images in the chapter subfolders.
    """
    print("--- OCR Processing ---")
    chapters_dir = os.path.join(DIR_CONFIG['screenshots'], 'chapters')
    ocr_output_dir = DIR_CONFIG['ocr_output']

    if not os.path.exists(chapters_dir) or not os.listdir(chapters_dir):
        print(f"Chapters directory '{chapters_dir}' is empty or does not exist.")
        print("Please run the 'divide' step first.")
        return

    # Initialize EasyOCR reader
    try:
        reader = easyocr.Reader(['en']) # Specify language(s)
    except Exception as e:
        print(f"Error initializing EasyOCR: {e}")
        print("Please ensure you have the necessary models downloaded and dependencies installed.")
        return

    for chapter_folder in sorted(os.listdir(chapters_dir)):
        chapter_path = os.path.join(chapters_dir, chapter_folder)
        if not os.path.isdir(chapter_path):
            continue

        print(f"Processing Chapter: {chapter_folder}")

        image_files = sorted([f for f in os.listdir(chapter_path) if f.lower().endswith(('.png', '.jpg'))])
        full_text = ""

        for image_file in image_files:
            image_path = os.path.join(chapter_path, image_file)
            print(f"  - Reading: {image_file}")
            try:
                result = reader.readtext(image_path)
                text = ' '.join([item[1] for item in result])
                full_text += text + "\n"
            except Exception as e:
                print(f"    Error during OCR on {image_file}: {e}")

        output_filename = os.path.join(ocr_output_dir, f"{chapter_folder}.txt")
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(full_text)
        print(f"  - Saved OCR text to {output_filename}")

    print("\nOCR processing complete. Next step: Correct text with AI.")


# --- Step 5: AI-Powered Text Correction ---
def correct_text_with_ai():
    """
    Corrects the text from OCR using the Gemini API.
    """
    print("--- AI Text Correction ---")

    try:
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            print("Error: GOOGLE_API_KEY environment variable not set.")
            sys.exit(1)
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
    except Exception as e:
        print(f"Error initializing Gemini: {e}")
        return

    ocr_output_dir = DIR_CONFIG['ocr_output']
    final_text_dir = DIR_CONFIG['final_text']

    if not os.path.exists(ocr_output_dir) or not os.listdir(ocr_output_dir):
        print(f"OCR output directory '{ocr_output_dir}' is empty. Please run 'ocr' step first.")
        return

    for txt_file in sorted(os.listdir(ocr_output_dir)):
        if not txt_file.endswith('.txt'):
            continue

        file_path = os.path.join(ocr_output_dir, txt_file)
        print(f"Processing: {txt_file}")

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        prompt = (
            "Correct the grammar, spelling, and punctuation of this OCR-extracted text. "
            "Organize it into coherent paragraphs and apply basic formatting. "
            "The output should only be the corrected text, with no additional commentary.\n\n"
            f'"""{content}"""'
        )

        try:
            response = model.generate_content(prompt)
            corrected_text = response.text
        except Exception as e:
            print(f"  - Error calling Gemini API for {txt_file}: {e}")
            corrected_text = f"--- ERROR PROCESSING FILE ---\n\n{content}"

        output_filename = os.path.join(final_text_dir, txt_file)
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(corrected_text)
        print(f"  - Saved corrected text to {output_filename}")

    print("\nAI correction process complete.")


# --- Main execution block (will be expanded later) ---
if __name__ == "__main__":
    # Ensure all directories exist before doing anything else.
    create_directories()

    parser = argparse.ArgumentParser(description="A tool to process screenshots with OCR and AI correction.")
    parser.add_argument(
        "step",
        choices=["all", "configure", "capture", "divide", "ocr", "correct"],
        help="The step to execute."
    )

    args = parser.parse_args()

    print(f"Executing step: {args.step}")

    # The logic for each step will be added here.
    if args.step == "all":
        print("Running the full pipeline...")
        capture_screenshots()
        divide_screenshots_by_chapter()
        perform_ocr()
        correct_text_with_ai()
        print("\nFull pipeline finished successfully!")
    elif args.step == "configure":
        configure_mouse()
    elif args.step == "capture":
        capture_screenshots()
    elif args.step == "divide":
        divide_screenshots_by_chapter()
    elif args.step == "ocr":
        perform_ocr()
    elif args.step == "correct":
        correct_text_with_ai()

    print("\nScript finished.")
