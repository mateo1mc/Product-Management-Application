import os
import subprocess
import pandas as pd
import tkinter as tk

def search_product():
    query = entry.get().strip()  # Get the user input from the entry field
    query_lower = query.lower()
    
    result_name = data[data['ProductName'].str.lower() == query_lower]
    
    result_barcode = pd.DataFrame()
    if query.isdigit():
        barcode_query = int(query)
        result_barcode = data[data['Barcode'] == barcode_query]
    
    result = pd.concat([result_name, result_barcode]).drop_duplicates()
    
    if not result.empty:
        product_name_var.set(result['ProductName'].values[0])
        price_var.set(result['Price'].values[0])
        quantity_var.set(1)
        update_total()
        
        # Clear the search bar after displaying the result
        entry.delete(0, tk.END)
    else:
        product_name_var.set("PRODUKTI NUK U GJEND.")
        price_var.set(0)
        total_var.set(0)


def update_total():
    total_price = sum(item['Total Price'] for item in buy_list)
    total_var.set(total_price)

def add_to_buy_list():
    product_name = product_name_var.get()
    price_per_unit = price_var.get()
    quantity = quantity_var.get()
    
    # Check if the product details are valid before adding to the list
    if product_name and price_per_unit > 0 and quantity > 0:
        total_price = quantity * price_per_unit
        
        buy_list.append({
            'Product Name': product_name,
            'Quantity': quantity,
            'Price Per Unit': price_per_unit,
            'Total Price': total_price
        })
        
        update_buy_list()
        update_total()
    else:
        # Notify the user that the product details are invalid or empty
        print("Invalid product details. Please ensure all fields are filled correctly.")


def delete_item(item_index):
    del buy_list[item_index]
    update_buy_list()
    update_total()

def clear_buy_list():
    buy_list.clear()
    update_buy_list()
    update_total()

def update_buy_list():
    for widget in buy_list_frame.winfo_children():
        widget.destroy()
    
    for index, item in enumerate(buy_list):
        label_text = f"{item['Product Name']} -- {item['Quantity']} x {item['Price Per Unit']:.0f} == {item['Total Price']:.0f}"
        item_label = tk.Label(buy_list_frame, text=label_text, font=("Arial", 18))
        item_label.grid(row=index, column=0, sticky="W")
        
        delete_button = tk.Button(
            buy_list_frame,
            text="FSHI",
            command=lambda index=index: delete_item(index),
            bg="red",
            fg="white"
        )
        delete_button.grid(row=index, column=1, padx=5, pady=5)


# Get the directory path where the script is located
script_dir = os.path.dirname(__file__) if "__file__" in locals() else os.getcwd()

# Construct the full path to your CSV file
csv_file_path = os.path.join(script_dir, 'products.csv')

# Read the data from the CSV file
data = pd.read_csv(csv_file_path)

# Create the main window
root = tk.Tk()
root.title("SHITJA E PRODUKTEVE")
root.state('zoomed')  # Maximizes the window

# Variables for product details, quantity, total, and buy list
product_name_var = tk.StringVar()
price_var = tk.DoubleVar()
quantity_var = tk.IntVar(value=1)
total_var = tk.DoubleVar()
buy_list = []

# Create and place GUI elements
label = tk.Label(root, text="SHKRUAJ EMRIN E PRODUKTIT OSE BARCODE-in:", font=("Arial", 20))
label.pack()

entry = tk.Entry(root, width=40, font=("Arial", 15))
def search_on_enter(event):
    search_product()

entry.bind("<Return>", search_on_enter)
entry.pack()


# - - - SUGGESTIONS - - - 
def update_suggestions(event):
    query = entry.get().strip().lower()
    
    # Initialize the variable outside the if block
    barcode_suggestion = pd.DataFrame()
    
    # Filter the data for suggestions based on the initial letters
    initial_suggestions = data[data['ProductName'].str.lower().str.startswith(query)]
    
    # Filter the data for suggestions based on any occurrence of the query in the name
    other_suggestions = data[data['ProductName'].str.lower().str.contains(query)]
    
    # Filter suggestions based on barcode if the query is a digit
    if query.isdigit():
        barcode_query = int(query)
        barcode_suggestion = data[data['Barcode'] == barcode_query]
        # Check for full barcode match
        if not barcode_suggestion.empty:
            product_name = barcode_suggestion.iloc[0]['ProductName']
            suggestion_list.insert(tk.END, product_name)
            # Clear the "PRODUKTI QE KERKONI NUK EGZISTON" entry
            suggestion_list.delete(0)  # Assuming it's the first entry
        suggestions = pd.concat([initial_suggestions, other_suggestions]).drop_duplicates()
    else:
        suggestions = pd.concat([initial_suggestions, other_suggestions]).drop_duplicates()
    
    # Check if a product name is found based on the barcode search
    if not barcode_suggestion.empty:
        return  # Exit the function if barcode suggestion is found
    
    # Clear previous suggestions if barcode suggestion was already inserted
    if suggestions.empty and not barcode_suggestion.empty:
        return
    
    # Clear previous suggestions
    suggestion_list.delete(0, tk.END)
    
    # Display new suggestions or "PRODUKTI QE KERKONI NUK EGZISTON" if there are no suggestions
    if suggestions.empty:
        suggestion_list.insert(tk.END, "PRODUKTI QE KERKONI NUK EGZISTON")
        suggestion_list.itemconfig(tk.END, {'fg': 'red'})
    else:
        for product in suggestions['ProductName']:
            suggestion_list.insert(tk.END, product)


# Define the function to handle single-click selection from the suggestion list
def on_suggestion_select(event):
    selected_suggestion = suggestion_list.get(suggestion_list.nearest(event.y))
    entry.delete(0, tk.END)
    entry.insert(tk.END, selected_suggestion)
    search_product()

# Create a listbox for suggestions
suggestion_list = tk.Listbox(root, width=40, height=3, font=("Arial", 14))
suggestion_list.pack()

# Bind events to update suggestions and handle selection
entry.bind("<KeyRelease>", update_suggestions)
suggestion_list.bind("<Double-Button-1>", on_suggestion_select)
suggestion_list.bind("<Button-1>", on_suggestion_select)  # Add this line for single-click selection


# Create a frame to hold the product details
product_details_frame = tk.Frame(root)
product_details_frame.pack()
# Label to display the Product Name variable
product_name_display = tk.Label(product_details_frame, textvariable=product_name_var, font=("Arial", 14))
product_name_display.grid(row=0, column=1)
# Label for Price
price_label = tk.Label(product_details_frame, text=" --- ", font=("Arial", 14))
price_label.grid(row=0, column=2)
# Label to display the Price variable
price_display = tk.Label(product_details_frame, textvariable=price_var, font=("Arial", 15))
price_display.grid(row=0, column=3)
price_display.config(fg="red")


# - - - SASIA - - -
quantity_label = tk.Label(root, text="SASIA(cope):", font=("Arial", 14))
quantity_label.pack()
# Create a validation function to allow only numbers
def validate_quantity_input(new_value):
    return new_value.isdigit() or new_value == ""

# Register the validation function for the entry widget
validate_qty_input = root.register(validate_quantity_input)
quantity_entry = tk.Entry(root, textvariable=quantity_var, width=10, font=("Arial", 14), validate="key", validatecommand=(validate_qty_input, "%P"))
quantity_entry.pack()


# - - - ADD TO CART - - -
add_to_list_button = tk.Button(root, text="SHTO NE SHPORTE", command=add_to_buy_list, font=("Arial", 15))
add_to_list_button.pack(pady=10)

# Adding a bigger Total Price label below the product list
total_label = tk.Label(root, text="TOTALI:", font=("Arial", 18))
total_label.pack()

def update_total_display():
    total_display.config(text=f"{total_var.get():.0f}")
    
total_var.trace("w", lambda *args: update_total_display())
total_display = tk.Label(root, text=f"{total_var.get():.0f}", font=("Arial", 20))
total_display.pack()
total_display.config(fg="red")


# - - - CLEAR ALL BUTTON - - -
clear_button = tk.Button(root, text="FSHIJ TE GJITHA", command=clear_buy_list, font=("Arial", 15))
clear_button.pack(pady=10)


# - - - OPEN CSV BUTTON - - -
def open_csv_file():
    subprocess.run(['start', csv_file_path], shell=True)

open_csv_button = tk.Button(root, text="Open CSV", command=open_csv_file, font=("Arial", 15))
open_csv_button.pack(side=tk.BOTTOM, pady=20)


# - - - CHOISED PRODUCT - - -
buy_list_frame = tk.Frame(root)
buy_list_frame.pack()

root.mainloop()
