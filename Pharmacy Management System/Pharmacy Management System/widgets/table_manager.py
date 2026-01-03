import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import db
from metadata import TABS_INFO, KEY_FIELDS, AUTO_ID_FIELDS, INT_FIELDS, FLOAT_FIELDS, FK_MAP, REQUIRED_FIELDS
from utils import to_int_or_none, to_float_or_none, fetch_all, fetch_fk_choices, parse_fk_choice, exists_medicine_id, count_refs

class TableManager(ttk.Frame):
    def __init__(self, parent, table_name, columns):
        super().__init__(parent)
        self.table = table_name
        self.columns = columns
        self.key_fields = KEY_FIELDS[self.table]
        self.original_key_values = None
        self.fk_widgets = {}
        self.entry_widgets = {}
        self.var_strings = {}
        self.create_widgets()
        self.refresh_fk_choices()
        self.load_data()
    
    def create_widgets(self):
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        
        form_frame = ttk.LabelFrame(self, text=f"{self.table}", padding=10)
        form_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ns")
        
        required_fields = REQUIRED_FIELDS.get(self.table, [])
        
        for i, col in enumerate(self.columns):
            label_text = col.replace('_', ' ').replace('p ', '').title()
            if col in required_fields:
                label_text += " *"
            ttk.Label(form_frame, text=f"{label_text}:").grid(row=i, column=0, sticky="w", padx=5, pady=3)
            
            var = tk.StringVar()
            self.var_strings[col] = var
            
            if self.table in FK_MAP and col in FK_MAP[self.table]:
                cb = ttk.Combobox(form_frame, textvariable=var, state="readonly", width=28)
                cb.grid(row=i, column=1, sticky="w", padx=5, pady=3)
                self.fk_widgets[col] = cb
            else:
                state = "disabled" if col in AUTO_ID_FIELDS else "normal"
                ent = ttk.Entry(form_frame, textvariable=var, state=state, width=30)
                ent.grid(row=i, column=1, sticky="w", padx=5, pady=3)
                self.entry_widgets[col] = ent
        
        ttk.Label(form_frame, text="* Required fields", foreground="red").grid(
            row=len(self.columns), column=0, columnspan=2, sticky="w", padx=5, pady=5)
        
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=len(self.columns)+1, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Add", command=self.on_add, width=10).grid(row=0, column=0, padx=2)
        ttk.Button(btn_frame, text="Update", command=self.on_update, width=10).grid(row=0, column=1, padx=2)
        ttk.Button(btn_frame, text="Delete", command=self.on_delete, width=10).grid(row=0, column=2, padx=2)
        ttk.Button(btn_frame, text="Clear", command=self.on_clear, width=10).grid(row=0, column=3, padx=2)
        
        search_frame = ttk.LabelFrame(self, text="Search", padding=5)
        search_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        self.search_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.search_var, width=22).grid(row=0, column=0, padx=5)
        ttk.Button(search_frame, text="Search", command=self.on_search, width=6).grid(row=0, column=1, padx=2)
        ttk.Button(search_frame, text="All", command=self.load_data, width=6).grid(row=0, column=2, padx=2)
        
        tree_frame = ttk.Frame(self)
        tree_frame.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=10, pady=10)
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)
        
        self.tree = ttk.Treeview(tree_frame, columns=self.columns, show='headings')
        for col in self.columns:
            heading = col.replace('_', ' ').replace('p ', '').upper()
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=100, anchor="center")
        self.tree.grid(row=0, column=0, sticky="nsew")
        
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscroll=vsb.set, xscroll=hsb.set)
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
    
    def refresh_fk_choices(self):
        if self.table not in FK_MAP:
            return
        for col, spec in FK_MAP[self.table].items():
            ref_table, id_col, display_col = spec
            choices = fetch_fk_choices(ref_table, id_col, display_col)
            if col in self.fk_widgets:
                self.fk_widgets[col]['values'] = choices
    
    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        try:
            rows = fetch_all(self.table)
            for row in rows:
                self.tree.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {e}")
    
    def on_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0], "values")
        
        for i, col in enumerate(self.columns):
            val = vals[i]
            if self.table in FK_MAP and col in FK_MAP[self.table]:
                if val and val != "None" and val != "":
                    choices = list(self.fk_widgets[col]['values'])
                    match = next((c for c in choices if c.split(" - ")[0].strip() == str(val)), "")
                    self.var_strings[col].set(match)
                else:
                    self.var_strings[col].set("")
            else:
                self.var_strings[col].set("" if val is None or val == "None" else str(val))
        
        self.original_key_values = {k: vals[self.columns.index(k)] for k in self.key_fields}
    
    def on_clear(self):
        for col in self.columns:
            self.var_strings[col].set("")
        self.original_key_values = None
    
    def get_payload(self):
        payload = {}
        for col in self.columns:
            raw = self.var_strings[col].get().strip()
            
            if self.table in FK_MAP and col in FK_MAP[self.table]:
                payload[col] = parse_fk_choice(raw)
            elif col in INT_FIELDS.get(self.table, set()):
                payload[col] = to_int_or_none(raw)
            elif col in FLOAT_FIELDS.get(self.table, set()):
                payload[col] = to_float_or_none(raw)
            else:
                payload[col] = raw if raw else None
        
        return payload
    
    def validate(self, payload, for_update=False):
        required = REQUIRED_FIELDS.get(self.table, [])
        
        for field in required:
            val = payload.get(field)
            if val is None or val == "":
                field_name = field.replace('_', ' ').title()
                messagebox.showwarning("Warning", f"'{field_name}' field is required!")
                return False
        
        if self.table == "Medicines":
            mid = payload.get("medicine_id")
            if mid is not None:
                exclude = None
                if for_update and self.original_key_values:
                    exclude = {
                        "name": self.original_key_values.get("name"),
                        "manufacturer_id": self.original_key_values.get("manufacturer_id")
                    }
                if exists_medicine_id(mid, exclude):
                    messagebox.showwarning("Warning", f"Medicine ID {mid} is already in use!")
                    return False
        
        if self.table == "Stock":
            mid = payload.get("medicine_id")
            if mid is None:
                messagebox.showwarning("Warning", "Please select a medicine!")
                return False
            if not exists_medicine_id(mid):
                messagebox.showwarning("Warning", f"Selected medicine (ID: {mid}) not found!")
                return False
        
        return True
    
    def on_add(self):
        payload = self.get_payload()
        if not self.validate(payload, for_update=False):
            return
        
        cols = [c for c in self.columns if c not in AUTO_ID_FIELDS or payload[c] is not None]
        vals = [payload[c] for c in cols]
        placeholders = ", ".join(["?" for _ in cols])
        
        sql = f"INSERT INTO {self.table} ({', '.join(cols)}) VALUES ({placeholders})"
        
        try:
            db.execute_query(sql, tuple(vals))
            self.load_data()
            self.on_clear()
            messagebox.showinfo("Success", "Record added successfully.")
        except sqlite3.IntegrityError as e:
            error_msg = str(e)
            if "UNIQUE constraint" in error_msg:
                messagebox.showerror("Error", "This record already exists! (Uniqueness violation)")
            elif "NOT NULL constraint" in error_msg:
                messagebox.showerror("Error", f"Required field cannot be empty!\n{error_msg}")
            else:
                messagebox.showerror("Error", f"Integrity error: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Add error: {e}")
    
    def on_update(self):
        if not self.original_key_values:
            messagebox.showwarning("Warning", "Please select a row first.")
            return
        
        payload = self.get_payload()
        if not self.validate(payload, for_update=True):
            return
        
        if self.table == "Medicines":
            self._handle_medicine_update(payload)
        
        set_clause = ", ".join([f"{col} = ?" for col in self.columns])
        where_clause = " AND ".join([f"{k} = ?" for k in self.key_fields])
        
        params = [payload[c] for c in self.columns] + [self.original_key_values[k] for k in self.key_fields]
        sql = f"UPDATE {self.table} SET {set_clause} WHERE {where_clause}"
        
        try:
            db.execute_query(sql, tuple(params))
            self.load_data()
            self.on_clear()
            messagebox.showinfo("Success", "Record updated successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Update error: {e}")
    
    def _handle_medicine_update(self, payload):
        old_mid = self._get_selected_medicine_id()
        new_mid = payload.get("medicine_id")
        
        if old_mid and new_mid and str(old_mid) != str(new_mid):
            cnt_s = count_refs("Stock", "medicine_id", old_mid)
            cnt_p = count_refs("Prescription", "medicine_id", old_mid)
            cnt_sale = count_refs("Sales", "medicine_id", old_mid)
            total = cnt_s + cnt_p + cnt_sale
            
            if total > 0:
                if messagebox.askyesno("Related Records",
                    f"This medicine has {cnt_s} stock, {cnt_p} prescription and {cnt_sale} sales records.\n"
                    f"Do you want to update medicine_id from {old_mid} to {new_mid} in all records?"):
                    try:
                        db.execute_query("UPDATE Stock SET medicine_id = ? WHERE medicine_id = ?", (new_mid, old_mid))
                        db.execute_query("UPDATE Prescription SET medicine_id = ? WHERE medicine_id = ?", (new_mid, old_mid))
                        db.execute_query("UPDATE Sales SET medicine_id = ? WHERE medicine_id = ?", (new_mid, old_mid))
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to update related records: {e}")
    
    def _get_selected_medicine_id(self):
        if self.table != "Medicines":
            return None
        sel = self.tree.selection()
        if not sel:
            return None
        vals = self.tree.item(sel[0], "values")
        idx = self.columns.index("medicine_id")
        try:
            return int(vals[idx]) if vals[idx] and vals[idx] != "None" else None
        except:
            return None
    
    def on_delete(self):
        if not self.original_key_values:
            messagebox.showwarning("Warning", "Please select a row first.")
            return
        
        if not messagebox.askyesno("Confirm", "Are you sure you want to delete this record?"):
            return
        
        try:
            if self.table == "Medicines":
                self._cascade_delete_medicine()
            elif self.table == "Manufacturer":
                self._cascade_delete_manufacturer()
            elif self.table == "Doctor":
                self._cascade_delete_doctor()
            elif self.table == "Pharmacist":
                self._cascade_delete_pharmacist()
            elif self.table == "Patient":
                self._cascade_delete_patient()
            else:
                self._delete_direct()
            
            self.load_data()
            self.on_clear()
            messagebox.showinfo("Success", "Record deleted successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Delete error: {e}")
    
    def _delete_direct(self):
        where = " AND ".join([f"{k} = ?" for k in self.key_fields])
        vals = [self.original_key_values[k] for k in self.key_fields]
        db.execute_query(f"DELETE FROM {self.table} WHERE {where}", tuple(vals))
    
    def _cascade_delete_medicine(self):
        mid = self._get_selected_medicine_id()
        if mid:
            cnt_s = count_refs("Stock", "medicine_id", mid)
            cnt_p = count_refs("Prescription", "medicine_id", mid)
            cnt_sale = count_refs("Sales", "medicine_id", mid)
            total = cnt_s + cnt_p + cnt_sale
            
            if total > 0:
                if not messagebox.askyesno("Related Records",
                    f"This medicine has {cnt_s} stock, {cnt_p} prescription and {cnt_sale} sales records.\n"
                    f"Do you want to delete all of them?"):
                    return
                
                db.execute_query("DELETE FROM Stock WHERE medicine_id = ?", (mid,))
                db.execute_query("DELETE FROM Prescription WHERE medicine_id = ?", (mid,))
                db.execute_query("DELETE FROM Sales WHERE medicine_id = ?", (mid,))
        
        self._delete_direct()
    
    def _cascade_delete_manufacturer(self):
        man_id = self.original_key_values["manufacturer_id"]
        meds = db.execute_query(
            "SELECT medicine_id FROM Medicines WHERE manufacturer_id = ?", 
            (man_id,), fetch=True
        )
        
        if meds:
            if not messagebox.askyesno("Related Records",
                f"This manufacturer has {len(meds)} medicines. Do you want to delete all of them?"):
                return
            
            for (mid,) in meds:
                if mid:
                    db.execute_query("DELETE FROM Stock WHERE medicine_id = ?", (mid,))
                    db.execute_query("DELETE FROM Prescription WHERE medicine_id = ?", (mid,))
                    db.execute_query("DELETE FROM Sales WHERE medicine_id = ?", (mid,))
            
            db.execute_query("DELETE FROM Medicines WHERE manufacturer_id = ?", (man_id,))
        
        self._delete_direct()
    
    def _cascade_delete_doctor(self):
        did = self.original_key_values["doctor_id"]
        cnt = count_refs("Prescription", "doctor_id", did)
        
        if cnt > 0:
            if not messagebox.askyesno("Related Records",
                f"This doctor has {cnt} prescriptions. Do you want to delete them?"):
                return
            db.execute_query("DELETE FROM Prescription WHERE doctor_id = ?", (did,))
        
        self._delete_direct()
    
    def _cascade_delete_pharmacist(self):
        pid = self.original_key_values["p_id"]
        cnt = count_refs("Sales", "p_id", pid)
        
        if cnt > 0:
            if not messagebox.askyesno("Related Records",
                f"This pharmacist has {cnt} sales. Do you want to delete them?"):
                return
            db.execute_query("DELETE FROM Sales WHERE p_id = ?", (pid,))
        
        self._delete_direct()
    
    def _cascade_delete_patient(self):
        pid = self.original_key_values["patient_id"]
        cnt = count_refs("Prescription", "patient_id", pid)
        
        if cnt > 0:
            if not messagebox.askyesno("Related Records",
                f"This patient has {cnt} prescriptions. Do you want to delete them?"):
                return
            db.execute_query("DELETE FROM Prescription WHERE patient_id = ?", (pid,))
        
        self._delete_direct()
    
    def on_search(self):
        query = self.search_var.get().strip()
        if not query:
            self.load_data()
            return
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        like = f"%{query}%"
        where_parts = [f"CAST({c} AS TEXT) LIKE ?" for c in self.columns]
        sql = f"SELECT * FROM {self.table} WHERE {' OR '.join(where_parts)}"
        
        try:
            rows = db.execute_query(sql, tuple(like for _ in self.columns), fetch=True)
            for row in rows:
                self.tree.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Error", f"Search error: {e}")
