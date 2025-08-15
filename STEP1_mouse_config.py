from pynput import mouse
import os

# This script captures mouse clicks to define precise areas for a two-column layout.
# The coordinates will be used by another script to automate screenshots.

# The name of the file where coordinates will be saved
COORDS_FILENAME = "config/mouse_clicks_two_columns.txt"

# List to store the click coordinates
click_coordinates = []

# Instructions for the user, corresponding to each of the 10 clicks
instructions = [
    # Left Column Clicks (4)
    "LEFT column, TOP-LEFT corner:",
    "LEFT column, TOP-RIGHT corner:",
    "LEFT column, BOTTOM-LEFT corner:",
    "LEFT column, BOTTOM-RIGHT corner:",
    # Right Column Clicks (4)
    "RIGHT column, TOP-LEFT corner:",
    "RIGHT column, TOP-RIGHT corner:",
    "RIGHT column, BOTTOM-LEFT corner:",
    "RIGHT column, BOTTOM-RIGHT corner:",
    # Navigation Button Clicks (2)
    "PREVIOUS page button:",
    "NEXT page button:"
]

# Counter for the clicks
click_count = 0

def on_click(x, y, button, pressed):
    """Callback function to handle mouse clicks."""
    global click_count
    if pressed:
        # Store the coordinates
        click_coordinates.append((x, y))
        print(f"> Click {click_count + 1}/{len(instructions)} registered at ({x}, {y}).")
        
        click_count += 1
        
        if click_count < len(instructions):
            # Print the next instruction
            print(f"\n{click_count + 1}. {instructions[click_count]}")
        else:
            # All clicks have been registered, stop the listener
            print("\nAll coordinates have been captured. Saving to file...")
            return False # Stop the listener

def save_coordinates_to_file(coordinates, filename):
    """Saves the captured coordinates to a text file."""
    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    # Clear the file before writing
    with open(filename, 'w') as f:
        for (x, y) in coordinates:
            f.write(f"{x},{y}\n")
    print(f"Coordinates successfully saved to '{filename}'.")

# Main part of the script
if __name__ == "__main__":
    print("--- Two-Column Layout Setup (10 Clicks) ---")
    print(f"This script will guide you to capture {len(instructions)} mouse clicks to define the reading area.")
    print(f"The coordinates will be saved to '{COORDS_FILENAME}'.")
    print("-" * 45)
    
    # Display the first instruction
    print(f"1. {instructions[0]}")

    # Set up the listener for mouse clicks
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()

    # Save the collected coordinates to the file
    save_coordinates_to_file(click_coordinates, COORDS_FILENAME)
    
    print("-" * 45)
    print("Setup complete. You can now run the 'app_two_columns.py' script.")