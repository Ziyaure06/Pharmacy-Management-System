import sqlite3
from config import SQLITE_PATH

class DatabaseManager:
    def __init__(self):
        pass
        
    def get_connection(self):
        conn = sqlite3.connect(SQLITE_PATH)
        conn.execute("PRAGMA foreign_keys = OFF")
        return conn
    
    def execute_query(self, query, params=None, fetch=False):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            if fetch:
                result = cursor.fetchall()
                conn.close()
                return result
            else:
                conn.commit()
                last_id = cursor.lastrowid
                conn.close()
                return last_id
        except Exception as e:
            conn.rollback()
            conn.close()
            raise e

db = DatabaseManager()

def setup_database():
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS Manufacturer (
        manufacturer_id INTEGER PRIMARY KEY,
        company_name TEXT,
        phone TEXT,
        address TEXT
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS Medicines (
        medicine_id INTEGER,
        name TEXT,
        barcode TEXT UNIQUE,
        price REAL,
        manufacturer_id INTEGER,
        PRIMARY KEY (name, manufacturer_id),
        FOREIGN KEY (manufacturer_id) REFERENCES Manufacturer(manufacturer_id)
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS Stock (
        stock_id INTEGER PRIMARY KEY AUTOINCREMENT,
        medicine_id INTEGER,
        quantity INTEGER,
        expiration_date DATE,
        FOREIGN KEY (medicine_id) REFERENCES Medicines(medicine_id)
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS Patient (
        patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        tc_no TEXT UNIQUE,
        birth_date DATE,
        phone TEXT,
        address TEXT
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS Doctor (
        doctor_id INTEGER PRIMARY KEY,
        first_name TEXT,
        last_name TEXT,
        tel_no TEXT,
        specialization TEXT
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS Prescription (
        prescription_id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        doctor_id INTEGER,
        prescription_date DATE,
        medicine_id INTEGER,
        FOREIGN KEY (patient_id) REFERENCES Patient(patient_id),
        FOREIGN KEY (doctor_id) REFERENCES Doctor(doctor_id),
        FOREIGN KEY (medicine_id) REFERENCES Medicines(medicine_id)
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS Pharmacist (
        p_id INTEGER PRIMARY KEY,
        p_first_name TEXT,
        p_last_name TEXT,
        p_tel_no TEXT,
        p_address TEXT,
        p_start_date DATE
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS Sales (
        sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
        p_id INTEGER,
        medicine_id INTEGER,
        quantity INTEGER DEFAULT 1,
        sale_date DATE,
        total_price REAL,
        FOREIGN KEY (p_id) REFERENCES Pharmacist(p_id),
        FOREIGN KEY (medicine_id) REFERENCES Medicines(medicine_id)
    )''')
    
    conn.commit()
    conn.close()
