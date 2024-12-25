import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3

# Database setup
DB_FILE = "bank_records.db"

def setup_database():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                account_number TEXT PRIMARY KEY,
                holder_name TEXT NOT NULL,
                account_type TEXT CHECK(account_type IN ('S', 'C')),
                balance INTEGER NOT NULL CHECK(balance BETWEEN 0 AND 1000000)
            )
        """)
        conn.commit()

# Initialize the database
setup_database()

# Create GUI
class BankSystemApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Banking Record System")
        self.root.geometry("800x600")
        
        # Set background color for the root window
        self.root.config(bg="#f0f0f0")  # Light gray background

        # UI Frames
        self.create_widgets()

    def create_widgets(self):
        # Title
        tk.Label(self.root, text="Banking Record System", font=("Arial", 16, "bold"), bg="#f0f0f0").pack(pady=10)

        # Buttons Frame
        btn_frame = tk.Frame(self.root, bg="#f0f0f0")
        btn_frame.pack(pady=20)

        buttons = [
            ("Create Account", self.create_account),
            ("Modify Account", self.modify_account),
            ("Balance Inquiry", self.balance_inquiry),
            ("Deposit", self.deposit_money),
            ("Withdraw", self.withdraw_money),
            ("View All Accounts", self.view_all_accounts),
            ("Delete Account", self.delete_account),
            ("Exit Program", self.exit_program),
        ]

        for text, command in buttons:
            tk.Button(btn_frame, text=text, width=20, command=command, bg="#3498db", fg="#ffffff", activebackground="#2980b9").pack(pady=5)

        # Table for displaying accounts
        self.table_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.table_frame.pack(fill="both", expand=True)

        columns = ("Account Number", "Name", "Type", "Balance")
        self.account_table = ttk.Treeview(self.table_frame, columns=columns, show="headings")
        for col in columns:
            self.account_table.heading(col, text=col)
            self.account_table.column(col, width=150, anchor="center")
        self.account_table.pack(fill="both", expand=True)

    # Helper Functions
    def execute_query(self, query, params=(), fetch=False):
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            if fetch:
                return cursor.fetchall()

    def show_message(self, title, message):
        messagebox.showinfo(title, message)

    def clear_table(self):
        for row in self.account_table.get_children():
            self.account_table.delete(row)

    # Feature Functions
    def create_account(self):
        def submit():
            acc_no = acc_no_entry.get()
            name = name_entry.get()
            acc_type = acc_type_var.get()
            balance = balance_entry.get()

            if len(acc_no) != 12 or not acc_no.isdigit():
                self.show_message("Error", "Account number must be 12 digits.")
                return
            if not name or acc_type not in ['S', 'C']:
                self.show_message("Error", "Invalid account type or name.")
                return
            try:
                balance = int(balance)
                if (acc_type == 'S' and balance < 500) or (acc_type == 'C' and balance < 1000) or balance > 1000000:
                    self.show_message("Error", "Invalid balance amount.")
                    return
            except ValueError:
                self.show_message("Error", "Balance must be a number.")
                return

            try:
                self.execute_query(
                    "INSERT INTO accounts (account_number, holder_name, account_type, balance) VALUES (?, ?, ?, ?)",
                    (acc_no, name, acc_type, balance),
                )
                self.show_message("Success", "Account created successfully.")
                popup.destroy()
            except sqlite3.IntegrityError:
                self.show_message("Error", "Account number already exists.")

        popup = tk.Toplevel(self.root)
        popup.title("Create Account")
        popup.config(bg="#f0f0f0")  # Light gray background

        tk.Label(popup, text="Account Number (12 digits):", bg="#f0f0f0").pack(pady=5)
        acc_no_entry = tk.Entry(popup)
        acc_no_entry.pack(pady=5)

        tk.Label(popup, text="Holder Name:", bg="#f0f0f0").pack(pady=5)
        name_entry = tk.Entry(popup)
        name_entry.pack(pady=5)

        tk.Label(popup, text="Account Type (S for Saving, C for Current):", bg="#f0f0f0").pack(pady=5)
        acc_type_var = tk.StringVar()
        acc_type_menu = ttk.Combobox(popup, textvariable=acc_type_var, values=["S", "C"], state="readonly")
        acc_type_menu.pack(pady=5)

        tk.Label(popup, text="Initial Balance:", bg="#f0f0f0").pack(pady=5)
        balance_entry = tk.Entry(popup)
        balance_entry.pack(pady=5)

        tk.Button(popup, text="Submit", command=submit, bg="#3498db", fg="#ffffff", activebackground="#2980b9").pack(pady=20)

    def modify_account(self):
        def submit():
            acc_no = acc_no_entry.get()
            name = name_entry.get()
            acc_type = acc_type_var.get()
            balance = balance_entry.get()

            if not acc_no.isdigit() or len(acc_no) != 12:
                self.show_message("Error", "Account number must be 12 digits.")
                return
            if not name or acc_type not in ['S', 'C']:
                self.show_message("Error", "Invalid account type or name.")
                return
            try:
                balance = int(balance)
                if balance < 0 or balance > 1000000:
                    self.show_message("Error", "Balance must be between 0 and 1,000,000.")
                    return
            except ValueError:
                self.show_message("Error", "Balance must be a number.")
                return

            rows_updated = self.execute_query(
                "UPDATE accounts SET holder_name = ?, account_type = ?, balance = ? WHERE account_number = ?",
                (name, acc_type, balance, acc_no),
            )
            if rows_updated:
                self.show_message("Success", "Account updated successfully.")
                popup.destroy()
            else:
                self.show_message("Error", "Account not found.")

        popup = tk.Toplevel(self.root)
        popup.title("Modify Account")
        popup.config(bg="#f0f0f0")  # Light gray background

        tk.Label(popup, text="Account Number (12 digits):", bg="#f0f0f0").pack(pady=5)
        acc_no_entry = tk.Entry(popup)
        acc_no_entry.pack(pady=5)

        tk.Label(popup, text="New Holder Name:", bg="#f0f0f0").pack(pady=5)
        name_entry = tk.Entry(popup)
        name_entry.pack(pady=5)

        tk.Label(popup, text="New Account Type (S for Saving, C for Current):", bg="#f0f0f0").pack(pady=5)
        acc_type_var = tk.StringVar()
        acc_type_menu = ttk.Combobox(popup, textvariable=acc_type_var, values=["S", "C"], state="readonly")
        acc_type_menu.pack(pady=5)

        tk.Label(popup, text="New Balance:", bg="#f0f0f0").pack(pady=5)
        balance_entry = tk.Entry(popup)
        balance_entry.pack(pady=5)

        tk.Button(popup, text="Submit", command=submit, bg="#3498db", fg="#ffffff", activebackground="#2980b9").pack(pady=20)

    def balance_inquiry(self):
        def submit():
            acc_no = acc_no_entry.get()
            if not acc_no.isdigit() or len(acc_no) != 12:
                self.show_message("Error", "Account number must be 12 digits.")
                return

            account = self.execute_query(
                "SELECT * FROM accounts WHERE account_number = ?", (acc_no,), fetch=True
            )
            if account:
                account = account[0]
                self.show_message(
                    "Account Details",
                    f"Account Number: {account[0]}\nName: {account[1]}\nType: {account[2]}\nBalance: {account[3]}",
                )
                popup.destroy()
            else:
                self.show_message("Error", "Account not found.")

        popup = tk.Toplevel(self.root)
        popup.title("Balance Inquiry")
        popup.config(bg="#f0f0f0")  # Light gray background

        tk.Label(popup, text="Account Number (12 digits):", bg="#f0f0f0").pack(pady=5)
        acc_no_entry = tk.Entry(popup)
        acc_no_entry.pack(pady=5)

        tk.Button(popup, text="Submit", command=submit, bg="#3498db", fg="#ffffff", activebackground="#2980b9").pack(pady=20)

    def deposit_money(self):
        def submit():
            acc_no = acc_no_entry.get()
            amount = amount_entry.get()

            if not acc_no.isdigit() or len(acc_no) != 12:
                self.show_message("Error", "Account number must be 12 digits.")
                return
            try:
                amount = int(amount)
                if amount <= 0:
                    self.show_message("Error", "Deposit amount must be positive.")
                    return
            except ValueError:
                self.show_message("Error", "Amount must be a number.")
                return

            # Check if account exists
            account = self.execute_query(
                "SELECT balance FROM accounts WHERE account_number = ?", (acc_no,), fetch=True
            )
            if account:
                # Perform deposit
                self.execute_query(
                    "UPDATE accounts SET balance = balance + ? WHERE account_number = ?",
                    (amount, acc_no),
                )
                self.show_message("Success", f"Deposited {amount} successfully.")
                popup.destroy()
            else:
                self.show_message("Error", "Account not found.")

        # Popup window for deposit
        popup = tk.Toplevel(self.root)
        popup.title("Deposit Money")
        popup.config(bg="#f0f0f0")  # Light gray background

        tk.Label(popup, text="Account Number (12 digits):", bg="#f0f0f0").pack(pady=5)
        acc_no_entry = tk.Entry(popup)
        acc_no_entry.pack(pady=5)

        tk.Label(popup, text="Deposit Amount:", bg="#f0f0f0").pack(pady=5)
        amount_entry = tk.Entry(popup)
        amount_entry.pack(pady=5)

        tk.Button(popup, text="Submit", command=submit, bg="#3498db", fg="#ffffff", activebackground="#2980b9").pack(pady=20)

    def withdraw_money(self):
        def submit():
            acc_no = acc_no_entry.get()
            amount = amount_entry.get()

            if not acc_no.isdigit() or len(acc_no) != 12:
                self.show_message("Error", "Account number must be 12 digits.")
                return
            try:
                amount = int(amount)
                if amount <= 0:
                    self.show_message("Error", "Withdrawal amount must be positive.")
                    return
            except ValueError:
                self.show_message("Error", "Amount must be a number.")
                return

            # Check if account exists and balance is sufficient
            account = self.execute_query(
                "SELECT balance FROM accounts WHERE account_number = ?", (acc_no,), fetch=True
            )
            if account:
                current_balance = account[0][0]
                if current_balance >= amount:
                    # Perform withdrawal
                    self.execute_query(
                        "UPDATE accounts SET balance = balance - ? WHERE account_number = ?",
                        (amount, acc_no),
                    )
                    self.show_message("Success", f"Withdrawn {amount} successfully.")
                    popup.destroy()
                else:
                    self.show_message("Error", "Insufficient balance.")
            else:
                self.show_message("Error", "Account not found.")

        # Popup window for withdrawal
        popup = tk.Toplevel(self.root)
        popup.title("Withdraw Money")
        popup.config(bg="#f0f0f0")  # Light gray background

        tk.Label(popup, text="Account Number (12 digits):", bg="#f0f0f0").pack(pady=5)
        acc_no_entry = tk.Entry(popup)
        acc_no_entry.pack(pady=5)

        tk.Label(popup, text="Withdrawal Amount:", bg="#f0f0f0").pack(pady=5)
        amount_entry = tk.Entry(popup)
        amount_entry.pack(pady=5)

        tk.Button(popup, text="Submit", command=submit, bg="#3498db", fg="#ffffff", activebackground="#2980b9").pack(pady=20)

    def delete_account(self):
        def submit():
            acc_no = acc_no_entry.get()

            if not acc_no.isdigit() or len(acc_no) != 12:
                self.show_message("Error", "Account number must be 12 digits.")
                return

            # Delete account from the database
            rows_deleted = self.execute_query(
                "DELETE FROM accounts WHERE account_number = ?", (acc_no,)
            )
            if rows_deleted:
                self.show_message("Success", "Account deleted successfully.")
                popup.destroy()
            else:
                self.show_message("Error", "Account not found.")

        # Popup window for deleting an account
        popup = tk.Toplevel(self.root)
        popup.title("Delete Account")
        popup.config(bg="#f0f0f0")  # Light gray background

        tk.Label(popup, text="Account Number (12 digits):", bg="#f0f0f0").pack(pady=5)
        acc_no_entry = tk.Entry(popup)
        acc_no_entry.pack(pady=5)

        tk.Button(popup, text="Submit", command=submit, bg="#3498db", fg="#ffffff", activebackground="#2980b9").pack(pady=20)

    def view_all_accounts(self):
        self.clear_table()  # Clear existing data in the table
        accounts = self.execute_query("SELECT * FROM accounts", fetch=True)

        if accounts:  # Check if any records are fetched
            for account in accounts:
                # Insert data into the table
                self.account_table.insert("", "end", values=account)
        else:
            self.show_message("No Records", "No accounts found in the database.")

    def exit_program(self):
        self.root.quit()

# Initialize the root window and the app
root = tk.Tk()
app = BankSystemApp(root)
root.mainloop()
