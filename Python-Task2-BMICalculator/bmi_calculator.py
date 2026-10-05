import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt


DB_NAME = "bmi_records.db"


# ---------------- DATABASE ----------------

def create_database():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bmi_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                weight REAL NOT NULL,
                height REAL NOT NULL,
                bmi REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL
            )
        """)

        conn.commit()
        conn.close()

    except sqlite3.Error as error:
        messagebox.showerror("Database Error", f"Could not create database:\n{error}")


def save_record(username, weight, height, bmi, category):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO bmi_records
            (username, weight, height, bmi, category, date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            username,
            weight,
            height,
            bmi,
            category,
            datetime.now().strftime("%Y-%m-%d %H:%M")
        ))

        conn.commit()
        conn.close()

    except sqlite3.Error as error:
        messagebox.showerror("Database Error", f"Could not save record:\n{error}")


# ---------------- BMI CALCULATION ----------------

def calculate_bmi():
    username = name_entry.get().strip()
    weight_text = weight_entry.get().strip()
    height_text = height_entry.get().strip()

    if not username:
        messagebox.showerror("Invalid Input", "Please enter a user name.")
        return

    try:
        weight = float(weight_text)
        height = float(height_text)

        if weight <= 0 or height <= 0:
            raise ValueError

    except ValueError:
        messagebox.showerror(
            "Invalid Input",
            "Please enter positive numeric values for weight and height."
        )
        return

    bmi = weight / (height ** 2)

    if bmi < 18.5:
        category = "Underweight"
        result_color = "blue"
    elif bmi < 25:
        category = "Normal"
        result_color = "green"
    elif bmi < 30:
        category = "Overweight"
        result_color = "orange"
    else:
        category = "Obese"
        result_color = "red"

    result_label.config(
        text=f"BMI: {bmi:.2f}\nCategory: {category}",
        foreground=result_color
    )

    save_record(username, weight, height, bmi, category)

    load_history()


# ---------------- HISTORY ----------------

def load_history():
    for item in history_table.get_children():
        history_table.delete(item)

    username = name_entry.get().strip()

    if not username:
        return

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT weight, height, bmi, category, date
            FROM bmi_records
            WHERE username = ?
            ORDER BY id DESC
        """, (username,))

        records = cursor.fetchall()
        conn.close()

        for record in records:
            history_table.insert("", "end", values=record)

    except sqlite3.Error as error:
        messagebox.showerror(
            "Database Error",
            f"Could not load records:\n{error}"
        )


# ---------------- GRAPH ----------------

def show_graph():
    username = name_entry.get().strip()

    if not username:
        messagebox.showerror("Input Error", "Please enter a user name.")
        return

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT date, bmi
            FROM bmi_records
            WHERE username = ?
            ORDER BY id
        """, (username,))

        records = cursor.fetchall()
        conn.close()

        if not records:
            messagebox.showinfo(
                "No Records",
                "No BMI records found for this user."
            )
            return

        dates = [record[0] for record in records]
        bmi_values = [record[1] for record in records]

        plt.figure(figsize=(8, 5))
        plt.plot(dates, bmi_values, marker="o")
        plt.axhline(18.5, linestyle="--", label="18.5")
        plt.axhline(25, linestyle="--", label="25")
        plt.axhline(30, linestyle="--", label="30")

        plt.title(f"BMI Trend - {username}")
        plt.xlabel("Date")
        plt.ylabel("BMI")
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()
        plt.show()

    except sqlite3.Error as error:
        messagebox.showerror(
            "Database Error",
            f"Could not read records:\n{error}"
        )


# ---------------- GUI ----------------

root = tk.Tk()
root.title("BMI Calculator")
root.geometry("700x650")
root.resizable(False, False)

create_database()

title_label = ttk.Label(
    root,
    text="BMI Calculator",
    font=("Arial", 22, "bold")
)
title_label.pack(pady=15)

input_frame = ttk.Frame(root)
input_frame.pack(pady=10)

ttk.Label(input_frame, text="User Name:").grid(
    row=0, column=0, padx=10, pady=8, sticky="w"
)

name_entry = ttk.Entry(input_frame, width=30)
name_entry.grid(row=0, column=1, padx=10, pady=8)

ttk.Label(input_frame, text="Weight (kg):").grid(
    row=1, column=0, padx=10, pady=8, sticky="w"
)

weight_entry = ttk.Entry(input_frame, width=30)
weight_entry.grid(row=1, column=1, padx=10, pady=8)

ttk.Label(input_frame, text="Height (m):").grid(
    row=2, column=0, padx=10, pady=8, sticky="w"
)

height_entry = ttk.Entry(input_frame, width=30)
height_entry.grid(row=2, column=1, padx=10, pady=8)

calculate_button = ttk.Button(
    root,
    text="Calculate BMI",
    command=calculate_bmi
)
calculate_button.pack(pady=10)

result_label = ttk.Label(
    root,
    text="Enter your details",
    font=("Arial", 16, "bold")
)
result_label.pack(pady=10)

history_title = ttk.Label(
    root,
    text="BMI History",
    font=("Arial", 14, "bold")
)
history_title.pack(pady=5)

columns = ("Weight", "Height", "BMI", "Category", "Date")

history_table = ttk.Treeview(
    root,
    columns=columns,
    show="headings",
    height=8
)

for column in columns:
    history_table.heading(column, text=column)
    history_table.column(column, width=110)

history_table.pack(pady=10)

button_frame = ttk.Frame(root)
button_frame.pack(pady=10)

ttk.Button(
    button_frame,
    text="Refresh History",
    command=load_history
).grid(row=0, column=0, padx=10)

ttk.Button(
    button_frame,
    text="Show BMI Trend",
    command=show_graph
).grid(row=0, column=1, padx=10)

root.mainloop()