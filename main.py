# ============================================================
# PROJECT: SMART EXPENSE TRACKER
# SUBJECT: ADVANCED PROGRAMMING TECHNIQUES
# LANGUAGE: PYTHON
# ============================================================

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import date, datetime
from collections import defaultdict

# Matplotlib is used for the two charts.
# Install it in the VS Code terminal with: python -m pip install matplotlib
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# Store the JSON file beside this Python program, not in an unpredictable
# current working directory.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_NAME = os.path.join(BASE_DIR, "transactions.json")


# ------------------------------------------------------------
# FUNCTION 1: LOAD TRANSACTIONS FROM FILE
# Concepts: Functions, File Handling, Lists, Dictionaries
# ------------------------------------------------------------

def load_transactions():
    if not os.path.exists(FILE_NAME):
        return []

    try:
        with open(FILE_NAME, "r", encoding="utf-8") as file:
            transactions = json.load(file)

        if isinstance(transactions, list):
            # Ignore malformed entries rather than crashing the application.
            valid_transactions = []
            for item in transactions:
                if (
                    isinstance(item, dict)
                    and "id" in item
                    and "type" in item
                    and "category" in item
                    and "amount" in item
                    and "date" in item
                ):
                    valid_transactions.append(item)
            return valid_transactions

        messagebox.showerror(
            "File Error",
            "The transaction file does not contain a valid list."
        )
        return []

    except (json.JSONDecodeError, OSError) as error:
        messagebox.showerror(
            "File Error",
            f"Unable to read the transaction file.\n\n{error}"
        )
        return []


# ------------------------------------------------------------
# FUNCTION 2: SAVE TRANSACTIONS TO FILE
# Concepts: Functions, File Handling, JSON
# ------------------------------------------------------------

def save_transactions(transactions):
    try:
        with open(FILE_NAME, "w", encoding="utf-8") as file:
            json.dump(transactions, file, indent=4, ensure_ascii=False)
        return True

    except OSError as error:
        messagebox.showerror("File Error", str(error))
        return False


# ------------------------------------------------------------
# CLASS: SMART EXPENSE TRACKER
# Concepts: Classes, Objects, Functions, Lists, Dictionaries
# ------------------------------------------------------------

class ExpenseTracker:

    def __init__(self, root):
        self.root = root
        self.root.title("Smart Expense Tracker")
        self.root.geometry("1120x760")
        self.root.minsize(900, 620)
        self.root.configure(bg="#f0f4f8")

        self.transactions = load_transactions()

        # Find the next ID while tolerating old or incomplete JSON records.
        existing_ids = []
        for item in self.transactions:
            try:
                existing_ids.append(int(item.get("id", 0)))
            except (TypeError, ValueError):
                pass
        self.next_id = max(existing_ids, default=0) + 1

        self.create_interface()
        self.refresh_table()

    # --------------------------------------------------------
    # FUNCTION 3: CREATE GRAPHICAL INTERFACE
    # --------------------------------------------------------

    def create_interface(self):
        heading = tk.Label(
            self.root,
            text="SMART EXPENSE TRACKER",
            font=("Arial", 23, "bold"),
            bg="#243447",
            fg="white",
            pady=18
        )
        heading.pack(fill="x")

        summary_frame = tk.Frame(self.root, bg="#f0f4f8")
        summary_frame.pack(fill="x", padx=20, pady=12)

        self.income_label = self.create_card(
            summary_frame, "Total Income", "#198754"
        )
        self.expense_label = self.create_card(
            summary_frame, "Total Expenses", "#dc3545"
        )
        self.balance_label = self.create_card(
            summary_frame, "Remaining Balance", "#2457a7"
        )

        form = tk.LabelFrame(
            self.root,
            text="Add New Transaction",
            font=("Arial", 12, "bold"),
            bg="#f0f4f8",
            padx=12,
            pady=10
        )
        form.pack(fill="x", padx=20, pady=4)

        tk.Label(form, text="Type:", bg="#f0f4f8").grid(
            row=0, column=0, padx=5, pady=7, sticky="w"
        )
        self.type_var = tk.StringVar(value="Expense")
        ttk.Combobox(
            form,
            textvariable=self.type_var,
            values=("Income", "Expense"),
            state="readonly",
            width=14
        ).grid(row=0, column=1, padx=5, sticky="w")

        tk.Label(form, text="Category:", bg="#f0f4f8").grid(
            row=0, column=2, padx=5, sticky="w"
        )
        self.category_var = tk.StringVar(value="Food")
        ttk.Combobox(
            form,
            textvariable=self.category_var,
            values=(
                "Food", "Travel", "Education", "Shopping", "Bills",
                "Health", "Salary", "Business", "Other"
            ),
            state="readonly",
            width=15
        ).grid(row=0, column=3, padx=5, sticky="w")

        tk.Label(form, text="Amount (Rs.):", bg="#f0f4f8").grid(
            row=1, column=0, padx=5, pady=7, sticky="w"
        )
        self.amount_entry = ttk.Entry(form, width=17)
        self.amount_entry.grid(row=1, column=1, padx=5, sticky="w")

        tk.Label(form, text="Date (YYYY-MM-DD):", bg="#f0f4f8").grid(
            row=1, column=2, padx=5, sticky="w"
        )
        self.date_entry = ttk.Entry(form, width=18)
        self.date_entry.insert(0, date.today().isoformat())
        self.date_entry.grid(row=1, column=3, padx=5, sticky="w")

        tk.Label(form, text="Description:", bg="#f0f4f8").grid(
            row=2, column=0, padx=5, pady=7, sticky="w"
        )
        self.description_entry = ttk.Entry(form, width=35)
        self.description_entry.grid(
            row=2, column=1, columnspan=2, padx=5, sticky="w"
        )

        tk.Button(
            form,
            text="Add Transaction",
            command=self.add_transaction,
            bg="#2457a7",
            fg="white",
            activebackground="#193e78",
            activeforeground="white",
            padx=12,
            pady=6
        ).grid(row=2, column=3, padx=5, sticky="w")

        controls = tk.Frame(self.root, bg="#f0f4f8")
        controls.pack(fill="x", padx=20, pady=9)

        tk.Label(controls, text="Search:", bg="#f0f4f8").pack(side="left")
        self.search_entry = ttk.Entry(controls, width=24)
        self.search_entry.pack(side="left", padx=8)

        ttk.Button(
            controls, text="Search", command=self.search_transactions
        ).pack(side="left")
        ttk.Button(
            controls, text="Show All", command=self.refresh_table
        ).pack(side="left", padx=5)
        ttk.Button(
            controls, text="Expense Pie Chart", command=self.show_expense_pie_chart
        ).pack(side="left", padx=(12, 4))
        ttk.Button(
            controls, text="Monthly Bar Chart", command=self.show_monthly_bar_chart
        ).pack(side="left", padx=4)
        ttk.Button(
            controls, text="Delete Selected", command=self.delete_transaction
        ).pack(side="right")

        table_frame = tk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=20, pady=(3, 12))

        columns = ("id", "type", "category", "amount", "date", "description")
        self.table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        headings = {
            "id": "ID",
            "type": "Type",
            "category": "Category",
            "amount": "Amount (Rs.)",
            "date": "Date",
            "description": "Description"
        }
        widths = {
            "id": 45,
            "type": 90,
            "category": 110,
            "amount": 120,
            "date": 120,
            "description": 300
        }

        for column in columns:
            self.table.heading(column, text=headings[column])
            self.table.column(
                column,
                width=widths[column],
                anchor="center"
            )

        scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical", command=self.table.yview
        )
        self.table.configure(yscrollcommand=scrollbar.set)
        self.table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        footer = tk.Label(
            self.root,
            text="Your transactions are saved locally in transactions.json",
            bg="#f0f4f8",
            fg="#526170",
            font=("Arial", 9)
        )
        footer.pack(pady=(0, 6))

    # --------------------------------------------------------
    # FUNCTION 4: CREATE SUMMARY CARDS
    # --------------------------------------------------------

    def create_card(self, parent, title, color):
        card = tk.Frame(parent, bg="white", padx=15, pady=10)
        card.pack(side="left", fill="x", expand=True, padx=7)

        tk.Label(
            card,
            text=title,
            font=("Arial", 11),
            bg="white",
            fg="#243447"
        ).pack()

        value_label = tk.Label(
            card,
            text="Rs. 0.00",
            font=("Arial", 17, "bold"),
            fg=color,
            bg="white"
        )
        value_label.pack(pady=5)
        return value_label

    # --------------------------------------------------------
    # FUNCTION 5: ADD A TRANSACTION
    # --------------------------------------------------------

    def add_transaction(self):
        transaction_type = self.type_var.get()
        category = self.category_var.get()
        amount_text = self.amount_entry.get().strip()
        transaction_date = self.date_entry.get().strip()
        description = self.description_entry.get().strip()

        if not amount_text:
            messagebox.showerror("Invalid Amount", "Please enter an amount.")
            return

        try:
            amount = float(amount_text)
        except ValueError:
            messagebox.showerror(
                "Invalid Amount", "Enter a numeric amount, for example 250 or 250.50."
            )
            return

        if amount <= 0:
            messagebox.showerror(
                "Invalid Amount", "Amount must be greater than zero."
            )
            return

        if not transaction_type or not category:
            messagebox.showerror(
                "Missing Information",
                "Please select a transaction type and category."
            )
            return

        try:
            parsed_date = date.fromisoformat(transaction_date)
        except ValueError:
            messagebox.showerror(
                "Invalid Date",
                "Enter a valid date in YYYY-MM-DD format, for example 2026-10-21."
            )
            return

        if parsed_date > date.today():
            messagebox.showerror(
                "Invalid Date", "Transaction date cannot be in the future."
            )
            return

        transaction = {
            "id": self.next_id,
            "type": transaction_type,
            "category": category,
            "amount": round(amount, 2),
            "date": transaction_date,
            "description": description
        }

        self.transactions.append(transaction)

        if save_transactions(self.transactions):
            self.next_id += 1
            self.amount_entry.delete(0, tk.END)
            self.description_entry.delete(0, tk.END)
            self.refresh_table()
            messagebox.showinfo(
                "Success", "Transaction added successfully!"
            )
        else:
            self.transactions.pop()

    # --------------------------------------------------------
    # FUNCTION 6: CALCULATE INCOME, EXPENSES AND BALANCE
    # --------------------------------------------------------

    def calculate_summary(self):
        total_income = sum(
            float(item.get("amount", 0))
            for item in self.transactions
            if item.get("type") == "Income"
        )
        total_expenses = sum(
            float(item.get("amount", 0))
            for item in self.transactions
            if item.get("type") == "Expense"
        )
        balance = total_income - total_expenses
        return total_income, total_expenses, balance

    # --------------------------------------------------------
    # FUNCTION 7: UPDATE SUMMARY CARDS
    # --------------------------------------------------------

    def update_summary(self):
        income, expenses, balance = self.calculate_summary()
        self.income_label.config(text=f"Rs. {income:,.2f}")
        self.expense_label.config(text=f"Rs. {expenses:,.2f}")
        self.balance_label.config(text=f"Rs. {balance:,.2f}")

    # --------------------------------------------------------
    # FUNCTION 8: DISPLAY TRANSACTIONS
    # --------------------------------------------------------

    def refresh_table(self):
        for row in self.table.get_children():
            self.table.delete(row)

        sorted_transactions = sorted(
            self.transactions,
            key=lambda item: (item.get("date", ""), int(item.get("id", 0))),
            reverse=True
        )

        for transaction in sorted_transactions:
            self.table.insert(
                "",
                tk.END,
                values=(
                    transaction.get("id", ""),
                    transaction.get("type", ""),
                    transaction.get("category", ""),
                    f"{float(transaction.get('amount', 0)):.2f}",
                    transaction.get("date", ""),
                    transaction.get("description", "")
                )
            )

        self.update_summary()

    # --------------------------------------------------------
    # FUNCTION 9: SEARCH TRANSACTIONS
    # --------------------------------------------------------

    def search_transactions(self):
        search_text = self.search_entry.get().strip().lower()

        for row in self.table.get_children():
            self.table.delete(row)

        sorted_transactions = sorted(
            self.transactions,
            key=lambda item: (item.get("date", ""), int(item.get("id", 0))),
            reverse=True
        )

        for transaction in sorted_transactions:
            searchable_text = " ".join(
                str(transaction.get(field, ""))
                for field in ("id", "type", "category", "amount", "date", "description")
            ).lower()

            if search_text in searchable_text:
                self.table.insert(
                    "",
                    tk.END,
                    values=(
                        transaction.get("id", ""),
                        transaction.get("type", ""),
                        transaction.get("category", ""),
                        f"{float(transaction.get('amount', 0)):.2f}",
                        transaction.get("date", ""),
                        transaction.get("description", "")
                    )
                )

    # --------------------------------------------------------
    # FUNCTION 10: DELETE A TRANSACTION
    # --------------------------------------------------------

    def delete_transaction(self):
        selected_rows = self.table.selection()

        if not selected_rows:
            messagebox.showwarning(
                "No Selection", "Please select a transaction to delete."
            )
            return

        confirm = messagebox.askyesno(
            "Confirm Deletion",
            "Are you sure you want to delete this transaction?"
        )
        if not confirm:
            return

        selected_values = self.table.item(selected_rows[0], "values")
        transaction_id = int(selected_values[0])
        old_transactions = self.transactions.copy()

        self.transactions = [
            item for item in self.transactions
            if int(item.get("id", -1)) != transaction_id
        ]

        if save_transactions(self.transactions):
            self.refresh_table()
            messagebox.showinfo(
                "Success", "Transaction deleted successfully."
            )
        else:
            self.transactions = old_transactions
            self.refresh_table()

    # --------------------------------------------------------
    # FUNCTION 11: EXPENSE CATEGORY PIE CHART
    # --------------------------------------------------------

    def show_expense_pie_chart(self):
        category_totals = defaultdict(float)

        for transaction in self.transactions:
            if transaction.get("type") == "Expense":
                category_totals[str(transaction.get("category", "Other"))] += float(
                    transaction.get("amount", 0)
                )

        # A pie chart cannot display meaningful slices when there are no expenses.
        category_totals = {
            category: total for category, total in category_totals.items()
            if total > 0
        }

        if not category_totals:
            messagebox.showinfo(
                "No Expense Data",
                "Add at least one expense transaction before opening the pie chart."
            )
            return

        chart_window = tk.Toplevel(self.root)
        chart_window.title("Expense Breakdown by Category")
        chart_window.geometry("760x600")
        chart_window.configure(bg="white")

        figure = Figure(figsize=(7.2, 5.2), dpi=100)
        axis = figure.add_subplot(111)
        labels = list(category_totals.keys())
        values = list(category_totals.values())

        axis.pie(
            values,
            labels=labels,
            autopct="%1.1f%%",
            startangle=90
        )
        axis.set_title("Expense Breakdown by Category")
        axis.axis("equal")

        canvas = FigureCanvasTkAgg(figure, master=chart_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        total_expenses = sum(values)
        tk.Label(
            chart_window,
            text=f"Total recorded expenses: Rs. {total_expenses:,.2f}",
            font=("Arial", 11, "bold"),
            bg="white",
            fg="#243447"
        ).pack(pady=(0, 12))

    # --------------------------------------------------------
    # FUNCTION 12: MONTHLY INCOME / EXPENSE BAR CHART
    # --------------------------------------------------------

    def show_monthly_bar_chart(self):
        monthly_income = defaultdict(float)
        monthly_expenses = defaultdict(float)

        for transaction in self.transactions:
            try:
                transaction_month = datetime.strptime(
                    str(transaction.get("date", "")), "%Y-%m-%d"
                ).strftime("%Y-%m")
            except ValueError:
                # Skip records with an invalid date in the saved file.
                continue

            amount = float(transaction.get("amount", 0))
            if transaction.get("type") == "Income":
                monthly_income[transaction_month] += amount
            elif transaction.get("type") == "Expense":
                monthly_expenses[transaction_month] += amount

        months = sorted(set(monthly_income) | set(monthly_expenses))

        if not months:
            messagebox.showinfo(
                "No Transaction Data",
                "Add income or expense transactions before opening the monthly chart."
            )
            return

        chart_window = tk.Toplevel(self.root)
        chart_window.title("Monthly Income vs Expenses")
        chart_window.geometry("900x600")
        chart_window.configure(bg="white")

        figure = Figure(figsize=(8.6, 5.2), dpi=100)
        axis = figure.add_subplot(111)

        positions = list(range(len(months)))
        bar_width = 0.38
        income_values = [monthly_income.get(month, 0) for month in months]
        expense_values = [monthly_expenses.get(month, 0) for month in months]

        axis.bar(
            [position - bar_width / 2 for position in positions],
            income_values,
            bar_width,
            label="Income"
        )
        axis.bar(
            [position + bar_width / 2 for position in positions],
            expense_values,
            bar_width,
            label="Expenses"
        )

        axis.set_title("Monthly Income vs Expenses")
        axis.set_xlabel("Month")
        axis.set_ylabel("Amount (Rs.)")
        axis.set_xticks(positions)
        axis.set_xticklabels(months, rotation=35, ha="right")
        axis.legend()
        axis.grid(axis="y", linestyle="--", alpha=0.35)
        figure.tight_layout()

        canvas = FigureCanvasTkAgg(figure, master=chart_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)


# ------------------------------------------------------------
# MAIN PROGRAM
# Concepts: Conditions, Objects, Modules, Function Calls
# ------------------------------------------------------------

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()
