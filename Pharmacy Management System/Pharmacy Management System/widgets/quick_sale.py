import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import db
from utils import (fetch_fk_choices, parse_fk_choice, to_int_or_none, 
                   check_medicine_expiration, EXPIRATION_WARNING_MESSAGE)

class QuickSalePanel(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.cart = []
        self.create_widgets()
    
    def create_widgets(self):
        ttk.Label(self, text="Quick Sale - Multiple Items", font=('Helvetica', 14, 'bold')).pack(pady=10)
        
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=2)
        main_frame.rowconfigure(0, weight=1)
        
        left_frame = ttk.Frame(main_frame)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        form = ttk.LabelFrame(left_frame, text="Add Item to Cart", padding=15)
        form.pack(fill="x", pady=5)
        
        ttk.Label(form, text="Pharmacist *:").grid(row=0, column=0, sticky="w", pady=5)
        self.pharmacist_var = tk.StringVar()
        self.pharmacist_cb = ttk.Combobox(form, textvariable=self.pharmacist_var, state="readonly", width=25)
        self.pharmacist_cb.grid(row=0, column=1, pady=5, padx=10, sticky="w")
        
        ttk.Label(form, text="Medicine *:").grid(row=1, column=0, sticky="w", pady=5)
        self.medicine_var = tk.StringVar()
        self.medicine_cb = ttk.Combobox(form, textvariable=self.medicine_var, state="readonly", width=25)
        self.medicine_cb.grid(row=1, column=1, pady=5, padx=10, sticky="w")
        self.medicine_cb.bind("<<ComboboxSelected>>", self.on_medicine_selected)
        
        ttk.Label(form, text="Quantity *:").grid(row=2, column=0, sticky="w", pady=5)
        self.quantity_var = tk.StringVar(value="1")
        ttk.Entry(form, textvariable=self.quantity_var, width=10).grid(row=2, column=1, sticky="w", pady=5, padx=10)
        
        self.stock_label = ttk.Label(form, text="", foreground="blue")
        self.stock_label.grid(row=2, column=2, sticky="w", padx=5)
        
        self.expiration_warning_label = ttk.Label(form, text="", foreground="red", wraplength=250)
        self.expiration_warning_label.grid(row=3, column=0, columnspan=3, sticky="w", pady=5, padx=10)
        
        btn_frame = ttk.Frame(form)
        btn_frame.grid(row=4, column=0, columnspan=3, pady=10)
        
        ttk.Button(btn_frame, text="Add to Cart", command=self.add_to_cart, width=12).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Refresh", command=self.refresh_choices, width=12).grid(row=0, column=1, padx=5)
        
        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        right_frame.rowconfigure(0, weight=1)
        right_frame.columnconfigure(0, weight=1)
        
        cart_frame = ttk.LabelFrame(right_frame, text="Shopping Cart", padding=10)
        cart_frame.pack(fill="both", expand=True)
        cart_frame.rowconfigure(0, weight=1)
        cart_frame.columnconfigure(0, weight=1)
        
        columns = ("medicine_id", "medicine_name", "quantity", "unit_price", "subtotal", "status")
        self.cart_tree = ttk.Treeview(cart_frame, columns=columns, show='headings', height=10)
        
        self.cart_tree.heading("medicine_id", text="ID")
        self.cart_tree.heading("medicine_name", text="Medicine")
        self.cart_tree.heading("quantity", text="Qty")
        self.cart_tree.heading("unit_price", text="Unit Price")
        self.cart_tree.heading("subtotal", text="Subtotal")
        self.cart_tree.heading("status", text="Status")
        
        self.cart_tree.column("medicine_id", width=50, anchor="center")
        self.cart_tree.column("medicine_name", width=150, anchor="w")
        self.cart_tree.column("quantity", width=50, anchor="center")
        self.cart_tree.column("unit_price", width=80, anchor="e")
        self.cart_tree.column("subtotal", width=80, anchor="e")
        self.cart_tree.column("status", width=100, anchor="center")
        
        self.cart_tree.tag_configure('expired', background='#ffcccc')
        self.cart_tree.tag_configure('expiring', background='#ffffcc')
        
        self.cart_tree.grid(row=0, column=0, sticky="nsew")
        
        vsb = ttk.Scrollbar(cart_frame, orient="vertical", command=self.cart_tree.yview)
        self.cart_tree.configure(yscrollcommand=vsb.set)
        vsb.grid(row=0, column=1, sticky="ns")
        
        cart_btn_frame = ttk.Frame(cart_frame)
        cart_btn_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        ttk.Button(cart_btn_frame, text="Remove Selected", command=self.remove_from_cart, width=15).grid(row=0, column=0, padx=5)
        ttk.Button(cart_btn_frame, text="Clear Cart", command=self.clear_cart, width=15).grid(row=0, column=1, padx=5)
        
        total_frame = ttk.Frame(cart_frame)
        total_frame.grid(row=2, column=0, columnspan=2, pady=5)
        
        ttk.Label(total_frame, text="Total Items:", font=('Helvetica', 10, 'bold')).grid(row=0, column=0, sticky="w", padx=10)
        self.total_items_label = ttk.Label(total_frame, text="0", font=('Helvetica', 10))
        self.total_items_label.grid(row=0, column=1, sticky="w")
        
        ttk.Label(total_frame, text="Total Amount:", font=('Helvetica', 12, 'bold')).grid(row=1, column=0, sticky="w", padx=10)
        self.total_amount_label = ttk.Label(total_frame, text="$0.00", font=('Helvetica', 12, 'bold'), foreground="green")
        self.total_amount_label.grid(row=1, column=1, sticky="w")
        
        checkout_frame = ttk.Frame(self)
        checkout_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(checkout_frame, text="Complete Sale", command=self.complete_sale, width=20).pack(side="right", padx=10)
        
        self.result_label = ttk.Label(checkout_frame, text="", font=('Helvetica', 11))
        self.result_label.pack(side="left", padx=10)
        
        self.refresh_choices()
    
    def refresh_choices(self):
        self.pharmacist_cb['values'] = fetch_fk_choices("Pharmacist", "p_id", "p_last_name")
        self.medicine_cb['values'] = fetch_fk_choices("Medicines", "medicine_id", "name")
        self.result_label.config(text="Lists updated.", foreground="blue")
        self.expiration_warning_label.config(text="")
        self.stock_label.config(text="")
    
    def on_medicine_selected(self, event):
        m_id = parse_fk_choice(self.medicine_var.get())
        if m_id:
            stock_result = db.execute_query(
                "SELECT COALESCE(SUM(quantity), 0) FROM Stock WHERE medicine_id = ?",
                (m_id,), fetch=True
            )
            stock = stock_result[0][0] if stock_result else 0
            self.stock_label.config(text=f"(Stock: {stock})")
            
            status = check_medicine_expiration(m_id)
            if status in ("expired", "expiring_soon"):
                self.expiration_warning_label.config(text=EXPIRATION_WARNING_MESSAGE)
            else:
                self.expiration_warning_label.config(text="")
        else:
            self.stock_label.config(text="")
            self.expiration_warning_label.config(text="")
    
    def add_to_cart(self):
        m_id = parse_fk_choice(self.medicine_var.get())
        qty = to_int_or_none(self.quantity_var.get())
        medicine_name = self.medicine_var.get().split(" - ", 1)[1] if " - " in self.medicine_var.get() else "Unknown"
        
        if not m_id:
            messagebox.showwarning("Warning", "Please select a medicine!")
            return
        if not qty or qty <= 0:
            messagebox.showwarning("Warning", "Please enter a valid quantity!")
            return
        
        stock_result = db.execute_query(
            "SELECT COALESCE(SUM(quantity), 0) FROM Stock WHERE medicine_id = ?",
            (m_id,), fetch=True
        )
        available_stock = stock_result[0][0] if stock_result else 0
        
        already_in_cart = sum(item['quantity'] for item in self.cart if item['medicine_id'] == m_id)
        
        if available_stock < (qty + already_in_cart):
            messagebox.showwarning("Warning", 
                f"Insufficient stock!\nAvailable: {available_stock}\nAlready in cart: {already_in_cart}\nRequested: {qty}")
            return
        
        price_result = db.execute_query(
            "SELECT COALESCE(price, 0) FROM Medicines WHERE medicine_id = ?",
            (m_id,), fetch=True
        )
        unit_price = price_result[0][0] if price_result else 0
        
        status = check_medicine_expiration(m_id)
        status_text = "OK"
        if status == "expired":
            status_text = "EXPIRED"
        elif status == "expiring_soon":
            status_text = "EXPIRING SOON"
        
        existing_item = None
        for item in self.cart:
            if item['medicine_id'] == m_id:
                existing_item = item
                break
        
        if existing_item:
            existing_item['quantity'] += qty
            existing_item['subtotal'] = existing_item['quantity'] * unit_price
        else:
            self.cart.append({
                'medicine_id': m_id,
                'medicine_name': medicine_name,
                'quantity': qty,
                'unit_price': unit_price,
                'subtotal': unit_price * qty,
                'status': status_text,
                'exp_status': status
            })
        
        self.update_cart_display()
        self.quantity_var.set("1")
        self.result_label.config(text=f"Added {qty}x {medicine_name} to cart.", foreground="green")
    
    def update_cart_display(self):
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
        
        total_amount = 0
        total_items = 0
        
        for item in self.cart:
            tags = ()
            if item['exp_status'] == "expired":
                tags = ('expired',)
            elif item['exp_status'] == "expiring_soon":
                tags = ('expiring',)
            
            self.cart_tree.insert("", "end", values=(
                item['medicine_id'],
                item['medicine_name'],
                item['quantity'],
                f"${item['unit_price']:.2f}",
                f"${item['subtotal']:.2f}",
                item['status']
            ), tags=tags)
            
            total_amount += item['subtotal']
            total_items += item['quantity']
        
        self.total_items_label.config(text=str(total_items))
        self.total_amount_label.config(text=f"${total_amount:.2f}")
    
    def remove_from_cart(self):
        selected = self.cart_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item to remove!")
            return
        
        values = self.cart_tree.item(selected[0], 'values')
        m_id = int(values[0])
        
        self.cart = [item for item in self.cart if item['medicine_id'] != m_id]
        self.update_cart_display()
        self.result_label.config(text="Item removed from cart.", foreground="blue")
    
    def clear_cart(self):
        if not self.cart:
            return
        
        if messagebox.askyesno("Confirm", "Clear all items from cart?"):
            self.cart = []
            self.update_cart_display()
            self.result_label.config(text="Cart cleared.", foreground="blue")
    
    def complete_sale(self):
        if not self.cart:
            messagebox.showwarning("Warning", "Cart is empty!")
            return
        
        p_id = parse_fk_choice(self.pharmacist_var.get())
        if not p_id:
            messagebox.showwarning("Warning", "Please select a pharmacist!")
            return
        
        expired_items = [item for item in self.cart if item['exp_status'] in ("expired", "expiring_soon")]
        if expired_items:
            expired_names = ", ".join([item['medicine_name'] for item in expired_items])
            if not messagebox.askyesno("Expiration Warning", 
                f"{EXPIRATION_WARNING_MESSAGE}\n\nAffected items: {expired_names}\n\nDo you still want to proceed?"):
                return
        
        for item in self.cart:
            stock_result = db.execute_query(
                "SELECT COALESCE(SUM(quantity), 0) FROM Stock WHERE medicine_id = ?",
                (item['medicine_id'],), fetch=True
            )
            available = stock_result[0][0] if stock_result else 0
            if available < item['quantity']:
                messagebox.showerror("Error", 
                    f"Insufficient stock for {item['medicine_name']}!\nAvailable: {available}, Required: {item['quantity']}")
                return
        
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            total_sale = 0
            
            for item in self.cart:
                db.execute_query(
                    "INSERT INTO Sales (p_id, medicine_id, quantity, sale_date, total_price) VALUES (?, ?, ?, ?, ?)",
                    (p_id, item['medicine_id'], item['quantity'], today, item['subtotal'])
                )
                
                remaining_qty = item['quantity']
                stock_rows = db.execute_query(
                    "SELECT stock_id, quantity FROM Stock WHERE medicine_id = ? AND quantity > 0 ORDER BY expiration_date ASC",
                    (item['medicine_id'],), fetch=True
                )
                
                for stock_id, stock_qty in stock_rows:
                    if remaining_qty <= 0:
                        break
                    
                    deduct = min(remaining_qty, stock_qty)
                    db.execute_query(
                        "UPDATE Stock SET quantity = quantity - ? WHERE stock_id = ?",
                        (deduct, stock_id)
                    )
                    remaining_qty -= deduct
                
                total_sale += item['subtotal']
            
            item_count = len(self.cart)
            self.cart = []
            self.update_cart_display()
            
            self.result_label.config(
                text=f"Sale completed! {item_count} items, Total: ${total_sale:.2f}",
                foreground="green"
            )
            
            messagebox.showinfo("Success", 
                f"Sale completed successfully!\n\nItems sold: {item_count}\nTotal amount: ${total_sale:.2f}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Sale failed: {e}")
            self.result_label.config(text=f"Error: {e}", foreground="red")
