import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import db
from queries import SQLQueries

class ReportsPanel(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()
    
    def create_widgets(self):
        ttk.Label(self, text="Reports and Analytics", font=('Helvetica', 14, 'bold')).pack(pady=10)
        
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)
        
        reports = [
            ("Low Stock", self.show_low_stock),
            ("Expiring Soon", self.show_expiring),
            ("Daily Sales", self.show_daily_sales),
            ("Top Selling", self.show_top_selling),
            ("Oldest Patient", self.show_oldest_patient),
            ("Stock Status", self.show_stock_status),
        ]
        
        for i, (text, cmd) in enumerate(reports):
            row, col = divmod(i, 3)
            ttk.Button(btn_frame, text=text, command=cmd, width=18).grid(row=row, column=col, padx=5, pady=5)
        
        result_frame = ttk.LabelFrame(self, text="Results", padding=10)
        result_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.result_text = tk.Text(result_frame, height=25, width=90, font=('Consolas', 10))
        self.result_text.pack(fill="both", expand=True)
    
    def display(self, title, rows, columns):
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"{'=' * 60}\n  {title}\n{'=' * 60}\n\n")
        
        if not rows:
            self.result_text.insert(tk.END, "  No results found.\n")
            return
        
        header = "  " + " | ".join(str(c).ljust(15)[:15] for c in columns)
        self.result_text.insert(tk.END, header + "\n")
        self.result_text.insert(tk.END, "  " + "-" * (len(columns) * 18) + "\n")
        
        for row in rows:
            line = "  " + " | ".join(str(v if v is not None else "N/A").ljust(15)[:15] for v in row)
            self.result_text.insert(tk.END, line + "\n")
        
        self.result_text.insert(tk.END, f"\n  Total: {len(rows)} records\n")
    
    def show_low_stock(self):
        try:
            rows = db.execute_query(SQLQueries.get_low_stock(10), fetch=True)
            self.display("LOW STOCK MEDICINES (<10)", rows, ["ID", "Medicine Name", "Stock"])
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def show_expiring(self):
        try:
            rows = db.execute_query(SQLQueries.get_expiring_soon(30), fetch=True)
            self.display("MEDICINES EXPIRING IN 30 DAYS", rows, ["Medicine", "Quantity", "Expiration Date", "Days Left"])
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def show_daily_sales(self):
        try:
            rows = db.execute_query(SQLQueries.get_daily_sales(), fetch=True)
            self.display("DAILY SALES SUMMARY", rows, ["Date", "Sales Count", "Total Revenue"])
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def show_top_selling(self):
        try:
            rows = db.execute_query(SQLQueries.get_top_selling(10), fetch=True)
            self.display("TOP 10 SELLING MEDICINES", rows, ["Medicine Name", "Quantity Sold", "Total Revenue"])
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def show_oldest_patient(self):
        try:
            rows = db.execute_query(SQLQueries.get_oldest_patient(), fetch=True)
            self.display("OLDEST PATIENT", rows, ["ID", "First Name", "Last Name", "Birth Date", "Age"])
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def show_stock_status(self):
        try:
            rows = db.execute_query(SQLQueries.get_medicines_with_stock(), fetch=True)
            self.display("MEDICINE STOCK STATUS", rows, ["ID", "Medicine", "Barcode", "Price", "Stock", "Manufacturer"])
        except Exception as e:
            messagebox.showerror("Error", str(e))
