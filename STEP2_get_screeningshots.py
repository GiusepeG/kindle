

import pyautogui
import time
import os
import tkinter as tk
from tkinter import simpledialog

# --- Configuration ---
SCREENSHOTS_FOLDER = 'screenshots'
COORDS_FILENAME = 'STEP1_mouse_config/mouse_clicks_two_columns.txt'

def clear_screenshots_folder(folder):
    """Deletes all files in the specified folder."""
    print(f"Clearing the '{folder}' directory...")
    if not os.path.exists(folder):
        os.makedirs(folder)
        print(f"Created directory: '{folder}'")
        return

    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')
    print("Directory cleared.")

def get_number_of_pages():
    """Shows an input box to ask the user for the number of pages to process."""
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    # Bring the dialog to the front
    root.attributes("-topmost", True)
    num_pages = simpledialog.askinteger("Input", "How many times to click the 'Next Page' button?", parent=root, minvalue=1)
    root.destroy()
    return num_pages

def read_coordinates(log_file):
    """Reads the 10 coordinates from the log file."""
    print(f"Reading coordinates from '{log_file}'...")
    with open(log_file, 'r') as file:
        lines = file.readlines()
        # Convert lines to tuples of integers
        coordinates = [tuple(map(int, line.strip().split(','))) for line in lines]
    if len(coordinates) < 10:
        print(f"Error: Expected 10 coordinates, but found {len(coordinates)}.")
        return None
    print("Coordinates read successfully.")
    return coordinates

def get_bounding_box(four_points):
    """Calculates the bounding box (left, top, width, height) from four corner points."""
    x_coords = [p[0] for p in four_points]
    y_coords = [p[1] for p in four_points]
    left = min(x_coords)
    top = min(y_coords)
    width = max(x_coords) - left
    height = max(y_coords) - top
    return (left, top, width, height)

def take_screenshots_two_columns(coordinates, num_pages, folder):
    """Takes screenshots of two columns and advances the page."""
    # Define regions from the 10 coordinates
    left_col_region = get_bounding_box(coordinates[0:4])
    right_col_region = get_bounding_box(coordinates[4:8])
    # prev_button = coordinates[8] # Not used in this script, but available
    next_button = coordinates[9]

    print("\nStarting screenshot process...")
    print(f"Left column region: {left_col_region}")
    print(f"Right column region: {right_col_region}")
    print(f"Next button at: {next_button}")

    # Start with an initial screenshot number
    screenshot_number = 1

    for i in range(num_pages):
        print(f"\nProcessing page {i + 1}/{num_pages}...")

        # Take screenshot of the left column
        print(f"  - Capturing left column...")
        filename_left = f"{folder}/page_{str(screenshot_number).zfill(4)}.png"
        pyautogui.screenshot(filename_left, region=left_col_region)
        print(f"    Saved as {filename_left}")
        screenshot_number += 1

        # Take screenshot of the right column
        print(f"  - Capturing right column...")
        filename_right = f"{folder}/page_{str(screenshot_number).zfill(4)}.png"
        pyautogui.screenshot(filename_right, region=right_col_region)
        print(f"    Saved as {filename_right}")
        screenshot_number += 1

        # Click the "next" button if it's not the last page
        if i < num_pages - 1:
            print("  - Clicking 'Next Page' button.")
            pyautogui.click(next_button)
            # Wait for the page to load
            time.sleep(1.5)  # Adjust this delay as necessary

    print("\nScreenshot process completed.")

# --- Main Execution ---
if __name__ == "__main__":
    clear_screenshots_folder(SCREENSHOTS_FOLDER)
    
    num_pages = get_number_of_pages()
    if not num_pages:
        print("Operation cancelled by user.")
    else:
        coordinates = read_coordinates(COORDS_FILENAME)
        if coordinates:
            # Give the user a moment to switch to the correct window
            print("\nYou have 5 seconds to switch to your reader window...")
            time.sleep(5)
            
            take_screenshots_two_columns(coordinates, num_pages, SCREENSHOTS_FOLDER)
            
            print("\nNext step: Run the OCR script to extract text from the images.")

