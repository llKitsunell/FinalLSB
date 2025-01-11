import csv
import os
import json
import random
import string
from tkinter import filedialog, messagebox, Toplevel, Checkbutton, BooleanVar, Label, Button, ttk 
import tkinter as tk
from cryptography.fernet import Fernet
from PIL import Image, ImageTk  # Import for image processing and display

# Generate and save encryption key
key = Fernet.generate_key()
with open("encryption_key.key", "wb") as key_file:
    key_file.write(key)
cipher = Fernet(key)

# Generate random passwords for students
def generate_passwords(num_students, length=8):
    return [''.join(random.choices(string.ascii_letters + string.digits, k=length)) for _ in range(num_students)]

# Convert message to binary
def message_to_binary(message):
    if isinstance(message, (dict, list)):
        message = json.dumps(message)
    encrypted_message = cipher.encrypt(message.encode()).decode('utf-8')
    return ''.join(format(ord(char), '08b') for char in encrypted_message)

# def csv_to_binary(csv_file_path):
#     global fieldnames  # Use the global variable

#     # Define the output file path
#     output_csv_file_path = './source/csvforlsb'
#     output_directory = os.path.dirname(output_csv_file_path)

#     # Ensure the 'source' directory exists
#     if not os.path.exists(output_directory):
#         os.makedirs(output_directory)

#     binary_data = ""
#     passwords = []

#     with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
#         preview_rows = list(csv.reader(csvfile))  # Read all rows for preview

#         # Skip rows before the selected header row
#         header_row_index = None
#         for i, row in enumerate(preview_rows):
#             if row == fieldnames:  # Match with the selected header row
#                 header_row_index = i
#                 break

#         if header_row_index is None:
#             raise ValueError("Header row not found in the CSV file.")

#         # Use rows starting from the header row
#         valid_rows = preview_rows[header_row_index + 1:]  # Rows after the header
#         valid_rows = [','.join(row) for row in valid_rows]  # Keep as comma-separated

#         reader = csv.DictReader(valid_rows, fieldnames=fieldnames)

#         # Add 'password' to fieldnames
#         fieldnames.append('password')

#         rows = list(reader)
#         passwords = generate_passwords(len(rows))  # Generate passwords for each row

#         # Update rows with passwords
#         for i, row in enumerate(rows):
#             row['password'] = passwords[i]

#         # Save updated rows to a new CSV file
#         with open(output_csv_file_path, mode='w', newline='', encoding='utf-8') as output_csv:
#             writer = csv.DictWriter(output_csv, fieldnames=fieldnames)
#             writer.writeheader()
#             writer.writerows(rows)

#         # Generate binary data from the updated rows
#         for row in rows:
#             row_json = json.dumps(row)
#             encrypted_data = cipher.encrypt(row_json.encode()).decode('utf-8')
#             binary_data += ''.join(format(ord(char), '08b') for char in encrypted_data) + '00001010'  # Binary newline

#     return binary_data, passwords

def csv_to_binary(csv_file_path):
    global fieldnames  # Use the global variable

    # Define the output file path with the correct extension
    output_csv_file_path = './source/csvforlsb.csv'
    output_directory = os.path.dirname(output_csv_file_path)

    # Ensure the 'source' directory exists
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    binary_data = ""
    passwords = []

    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        preview_rows = list(csv.reader(csvfile))  # Read all rows for preview

        # Skip rows before the selected header row
        header_row_index = None
        for i, row in enumerate(preview_rows):
            if row == fieldnames:  # Match with the selected header row
                header_row_index = i
                break

        if header_row_index is None:
            raise ValueError("Header row not found in the CSV file.")

        # Use rows starting from the header row
        valid_rows = preview_rows[header_row_index + 1:]  # Rows after the header
        valid_rows = [','.join(row) for row in valid_rows]  # Keep as comma-separated

        reader = csv.DictReader(valid_rows, fieldnames=fieldnames)

        # Add 'password' to fieldnames
        fieldnames.append('password')

        rows = list(reader)
        passwords = generate_passwords(len(rows))  # Generate passwords for each row

        # Update rows with passwords
        for i, row in enumerate(rows):
            row['password'] = passwords[i]

        # Save updated rows to a new CSV file
        with open(output_csv_file_path, mode='w', newline='', encoding='utf-8') as output_csv:
            writer = csv.DictWriter(output_csv, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        # Generate binary data from the updated rows
        for row in rows:
            row_json = json.dumps(row)
            encrypted_data = cipher.encrypt(row_json.encode()).decode('utf-8')
            binary_data += ''.join(format(ord(char), '08b') for char in encrypted_data) + '00001010'  # Binary newline

    return binary_data, passwords

# Embed binary message in the image
def hide_message(image_path, message, output_image):
    img = Image.open(image_path)
    img = img.convert("RGB")
    binary_message = message + '1111111111111110'  # End signal
    pixels = img.load()
    width, height = img.size
    binary_index = 0
    for y in range(height):
        for x in range(width):
            if binary_index < len(binary_message):
                r, g, b = pixels[x, y]
                r = (r & ~1) | int(binary_message[binary_index])
                binary_index += 1
                if binary_index < len(binary_message):
                    g = (g & ~1) | int(binary_message[binary_index])
                    binary_index += 1
                if binary_index < len(binary_message):
                    b = (b & ~1) | int(binary_message[binary_index])
                    binary_index += 1
                pixels[x, y] = (r, g, b)
    img.save(output_image)

    # Hide CSV and passwords in the image
def hide_csv(image_path, csv_file_path, output_image):
    binary_data, passwords = csv_to_binary(csv_file_path)
    hide_message(image_path, binary_data, output_image)
    messagebox.showinfo("Success", "Data hidden in image at "+ output_image)

def select_idfield():
    # Open a new window for field selection
    field_window = Toplevel(root)
    field_window.title("Select Field for Student ID")
    field_window.configure(bg="#2b2b2b")  # Set background to dark gray

    # Create a frame with a scrollbar
    canvas = tk.Canvas(field_window, bg="#2b2b2b", highlightthickness=0)
    scroll_y = tk.Scrollbar(field_window, orient="vertical", command=canvas.yview, bg="#2b2b2b")
    frame = tk.Frame(canvas, bg="#2b2b2b")

    frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=frame, anchor="nw")
    canvas.configure(yscrollcommand=scroll_y.set)

    canvas.pack(side="left", fill="both", expand=True)
    scroll_y.pack(side="right", fill="y")

    # Variable to store the selected field
    selected_field = tk.StringVar(value=None)  # Default to no selection

    label = Label(frame, text="Select a field for student ID:", bg="#2b2b2b", fg="white", font=("Arial", 12))
    label.pack(pady=10)

    # Create a radiobutton for each field in the CSV file
    for field in fieldnames:
        tk.Radiobutton(
            frame,
            text=field,
            variable=selected_field,
            value=field,
            bg="#2b2b2b",
            fg="white",
            font=("Arial", 10),
            selectcolor="#3c3f41",
            activeforeground="white"
        ).pack(anchor="w", padx=20)

    # Function to save the selected field to studentid_config.json
    def save_selected_studentid():
        if selected_field.get():  # Check if a field was selected
            with open("studentid_config.json", "w") as config_file:
                json.dump({"student_id": selected_field.get()}, config_file)
            messagebox.showinfo("Saved", "Field selection saved successfully.")
            field_window.destroy()
            select_fields()  # Proceed to the next step
        else:
            messagebox.showerror("Error", "Please select a field for the student ID.")

    # Add a save button at the bottom
    save_button = Button(
        frame, text="Save", command=save_selected_studentid,
        bg="#5c5f61", fg="white", font=("Arial", 10), activebackground="#7c7f81"
    )
    save_button.pack(pady=20)


def select_fields():
    field_window = Toplevel(root)
    field_window.title("Select Fields to Display")
    field_window.configure(bg="#2b2b2b")  # Set background to dark gray

    canvas = tk.Canvas(field_window, bg="#2b2b2b", highlightthickness=0)
    scroll_y = tk.Scrollbar(field_window, orient="vertical", command=canvas.yview, bg="#2b2b2b")
    frame = tk.Frame(canvas, bg="#2b2b2b")

    frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=frame, anchor="nw")
    canvas.configure(yscrollcommand=scroll_y.set)

    canvas.pack(side="left", fill="both", expand=True)
    scroll_y.pack(side="right", fill="y")

    field_vars = {}
    Label(frame, text="Select fields to display:", bg="#2b2b2b", fg="white", font=("Arial", 12)).pack(pady=10)

    for i, field in enumerate(fieldnames):
        var = BooleanVar(value=False)
        checkbox = Checkbutton(
            frame, text=field, variable=var,
            bg="#2b2b2b", fg="white", font=("Arial", 10),
            selectcolor="#5c5f61", activeforeground="white"
        )
        checkbox.pack(anchor="w", padx=20)
        field_vars[field] = var

    def save_selected_fields():
        selected_fields = [field for field, var in field_vars.items() if var.get()]
        with open("display_config.json", "w") as config_file:
            json.dump({"fields_to_display": selected_fields}, config_file)
        messagebox.showinfo("Saved", "Field selection saved successfully.")
        field_window.destroy()

    def select_all_fields():
        for var in field_vars.values():
            var.set(True)
        field_window.update()

    Button(frame, text="Display All", command=select_all_fields, bg="#5c5f61", fg="white", font=("Arial", 10), activebackground="#7c7f81").pack(pady=10)
    Button(frame, text="Save", command=save_selected_fields, bg="#5c5f61", fg="white", font=("Arial", 10), activebackground="#7c7f81").pack(pady=10)


def select_csv():
    global csv_path, fieldnames
    csv_path = filedialog.askopenfilename(title="Select CSV File", filetypes=[("CSV Files", "*.csv")])
    if csv_path:
        csv_label.config(text=os.path.basename(csv_path))
        select_header_row(csv_path)
    else:
        csv_label.config(text="No CSV File Selected")

def select_header_row(csv_file_path):
    header_window = Toplevel(root)
    header_window.title("Select Header Row")
    header_window.geometry("800x600")  # Wider window
    header_window.configure(bg="#2b2b2b")  # Dark gray background

    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        preview_rows = list(csv.reader(csvfile))
    
    if not preview_rows:
        messagebox.showerror("Error", "CSV is empty or unreadable.")
        header_window.destroy()
        return

    # Title label
    title_label = Label(
        header_window,
        text="Select the header row:",
        bg="#2b2b2b",
        fg="white",
        font=("Arial", 14, "bold")
    )
    title_label.pack(pady=20)

    # Frame for listbox and scrollbar
    listbox_frame = tk.Frame(header_window, bg="#2b2b2b", padx=20, pady=20, relief="groove", bd=2)
    listbox_frame.pack()

    # Scrollbar for listbox
    scrollbar = tk.Scrollbar(listbox_frame, orient="vertical")
    listbox = tk.Listbox(
        listbox_frame,
        selectmode='single',
        height=15,
        width=70,
        bg="#3c3f41",
        fg="white",
        font=("Arial", 10),
        highlightthickness=0,
        yscrollcommand=scrollbar.set
    )
    scrollbar.config(command=listbox.yview)
    scrollbar.pack(side="right", fill="y")
    listbox.pack(side="left", fill="both", expand=True)

    # Populate listbox
    for i, row in enumerate(preview_rows):
        listbox.insert(tk.END, f"Row {i + 1}: {', '.join(row)}")

    # Confirm button with hover effect
    def on_enter(e):
        confirm_button.config(bg="#7c7f81")

    def on_leave(e):
        confirm_button.config(bg="#5c5f61")

    def confirm_header():
        try:
            selected_index = listbox.curselection()[0]
            global fieldnames
            fieldnames = preview_rows[selected_index]
            messagebox.showinfo("Success", f"Row {selected_index + 1} selected as header.")
            header_window.destroy()
            select_idfield()
        except IndexError:
            messagebox.showerror("Error", "Select a row before confirming.")

    confirm_button = Button(
        header_window,
        text="Confirm",
        command=confirm_header,
        bg="#5c5f61",
        fg="white",
        font=("Arial", 12),
        activebackground="#7c7f81"
    )
    confirm_button.pack(pady=20)

    # Add hover effect
    confirm_button.bind("<Enter>", on_enter)
    confirm_button.bind("<Leave>", on_leave)


def select_image():
    global image_path, image_preview_label, image_preview
    image_path = filedialog.askopenfilename(title="Select Image", filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
    image_label.config(text=os.path.basename(image_path) if image_path else "No Image Selected")

def hide_data():
    if not image_path or not csv_path:
        messagebox.showerror("Error", "Select both an image and a CSV file.")
        return
    image_dir, image_file = os.path.split(image_path)
    file_name, file_extension = os.path.splitext(image_file)
    output_image = os.path.join(image_dir, f"{file_name}_hidden{file_extension}")
    try:
        hide_csv(image_path, csv_path, output_image)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to hide data: {str(e)}")

# Main GUI
root = tk.Tk()
root.title("Teacher - Encrypt Scores")

# Apply dark theme styles to the main window
root.configure(bg="#2c2c2c")  # Dark background color

# Create a frame to hold all widgets and center it
frame = tk.Frame(root, bg="#2c2c2c")  # Frame with same background as root
frame.pack(expand=True)  # Center the frame in the middle of the window

image_preview_label = None  # Global variable for the image preview

# Function to select an image and show its preview
def select_image():
    global image_path, image_preview_label, image_preview  # Use global for persistent image reference

    image_path = filedialog.askopenfilename(title="Select Image", filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
    if image_path:
        image_label.config(text=os.path.basename(image_path))  # Update label with the image name
        
        # Open the selected image and resize it for preview
        img = Image.open(image_path)
        img.thumbnail((200, 200))  # Resize the image to fit in the preview area
        
        # Convert image to PhotoImage for Tkinter
        image_preview = ImageTk.PhotoImage(img)
        
        # If a preview label already exists, update it
        if image_preview_label:
            image_preview_label.config(image=image_preview)
        else:
            # Create a new label for the image preview with border
            preview_frame = tk.Frame(frame, bg="#444444", relief="ridge", bd=2)  # Frame with border for image preview
            preview_frame.pack(pady=10)

            image_preview_label = tk.Label(preview_frame, image=image_preview, bg="#2c2c2c")
            image_preview_label.pack()

            # Add "Image Preview" text below the image
            preview_text_label = tk.Label(
                frame,
                text="Image Preview",
                bg="#2c2c2c",
                fg="#ffffff",
                font=("Helvetica", 10, "italic")
            )
            preview_text_label.pack()
    else:
        image_label.config(text="No Image Selected")  # Reset label if no image is selected

# Buttons and labels within the frame
tk.Button(
    frame,
    text="Select Image",
    command=select_image,
    bg="#444444",  # Dark gray button background
    fg="#ffffff",  # White text
    activebackground="#555555",  # Slightly lighter gray when active
    activeforeground="#ffffff",  # White text when active
    relief="flat",  # Flat button style for modern look
    font=("Helvetica", 10, "bold")  # Bold font
).pack(pady=10)

image_label = tk.Label(
    frame,
    text="No Image Selected",
    bg="#2c2c2c",  # Match main window background
    fg="#ffffff"  # White text
)
image_label.pack(pady=5)

tk.Button(
    frame,
    text="Select CSV File",
    command=select_csv,  # Call the `select_csv` function
    bg="#444444",
    fg="#ffffff",
    activebackground="#555555",
    activeforeground="#ffffff",
    relief="flat",
    font=("Helvetica", 10, "bold")
).pack(pady=10)

csv_label = tk.Label(
    frame,
    text="No CSV File Selected",
    bg="#2c2c2c",
    fg="#ffffff"
)
csv_label.pack(pady=5)

tk.Button(
    frame,
    text="Hide CSV in Image",
    command=hide_data,  # Call the `hide_data` function
    bg="#444444",
    fg="#ffffff",
    activebackground="#555555",
    activeforeground="#ffffff",
    relief="flat",
    font=("Helvetica", 10, "bold")
).pack(pady=10)

root.mainloop()