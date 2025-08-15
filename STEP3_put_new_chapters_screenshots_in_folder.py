
import os

# --- Configuration ---
NEW_CHAPTERS_FOLDER = 'STEP3_new_chapters_screenshots'

def main():
    """
    Main function to check for new chapter screenshots and guide the user.
    """
    print("--- Step 4: Manual Intervention for New Chapters ---")
    print("\nThis script checks for screenshots of new chapter pages.")
    print("You need to manually copy the first page of each new chapter into a specific folder.")

    # Create the folder if it doesn't exist
    if not os.path.exists(NEW_CHAPTERS_FOLDER):
        os.makedirs(NEW_CHAPTERS_FOLDER)
        print(f"Created directory: '{NEW_CHAPTERS_FOLDER}'")

    print(f"\nPlease perform the following steps:")
    print(f"1. Open the 'STEP2_get_screenshots' folder.")
    print(f"2. Identify the screenshot corresponding to the FIRST page of each NEW chapter.")
    print(f"3. Copy these specific screenshots.")
    print(f"4. Paste them into the '{NEW_CHAPTERS_FOLDER}' folder.")
    
    print("\nOnce you have copied all the necessary screenshots, you can proceed to the next step.")
    print("Next step: Run 'STEP5_divide_screenshots_by_chapters.py' to organize the book.")

if __name__ == "__main__":
    main()
