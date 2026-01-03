import tkinter as tk
from tkinter import ttk
from database import setup_database
from metadata import TABS_INFO
from widgets import TableManager, ReportsPanel, QuickSalePanel

class PharmacyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pharmacy Management System - CENG 301")
        self.root.geometry("1250x800")
        
        style = ttk.Style()
        style.theme_use('clam')
        
        setup_database()
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=5, pady=5)
        
        self.managers = {}
        for table, cols in TABS_INFO.items():
            frame = TableManager(self.notebook, table, cols)
            self.notebook.add(frame, text=f"{table}")
            self.managers[table] = frame
        
        reports = ReportsPanel(self.notebook)
        self.notebook.add(reports, text="Reports")
        
        sale_panel = QuickSalePanel(self.notebook)
        self.notebook.add(sale_panel, text="Quick Sale")
        
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)
        
        self.status = tk.StringVar(value="Ready | SQLite Database")
        ttk.Label(self.root, textvariable=self.status, relief="sunken").pack(side="bottom", fill="x")
    
    def on_tab_change(self, event):
        tab = self.notebook.tab(self.notebook.select(), "text")
        if tab in self.managers:
            self.managers[tab].refresh_fk_choices()
            self.managers[tab].load_data()
