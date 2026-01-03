from datetime import datetime, timedelta
from database import db

def to_int_or_none(val):
    if val is None or val == "":
        return None
    try:
        return int(val)
    except:
        return None

def to_float_or_none(val):
    if val is None or val == "":
        return None
    try:
        return float(val)
    except:
        return None

def fetch_all(table):
    return db.execute_query(f"SELECT * FROM {table}", fetch=True)

def fetch_fk_choices(table, id_col, display_col):
    query = f"SELECT {id_col}, {display_col} FROM {table} WHERE {id_col} IS NOT NULL"
    try:
        items = db.execute_query(query, fetch=True)
        return [f"{r[0]} - {r[1] if r[1] else 'N/A'}" for r in items]
    except:
        return []

def parse_fk_choice(text):
    if not text:
        return None
    try:
        return int(text.split(" - ", 1)[0].strip())
    except:
        return None

def exists_medicine_id(medicine_id, exclude_keys=None):
    if medicine_id is None:
        return False
    conn = db.get_connection()
    cursor = conn.cursor()
    if exclude_keys:
        cursor.execute(
            "SELECT 1 FROM Medicines WHERE medicine_id = ? AND NOT (name = ? AND manufacturer_id = ?)",
            (medicine_id, exclude_keys.get("name"), exclude_keys.get("manufacturer_id"))
        )
    else:
        cursor.execute("SELECT 1 FROM Medicines WHERE medicine_id = ?", (medicine_id,))
    row = cursor.fetchone()
    conn.close()
    return row is not None

def count_refs(table, col, val):
    if val is None:
        return 0
    try:
        result = db.execute_query(f"SELECT COUNT(1) FROM {table} WHERE {col} = ?", (val,), fetch=True)
        return result[0][0] if result else 0
    except:
        return 0

def check_expiration(expiration_date_str, warning_days=30):
    if not expiration_date_str or expiration_date_str == "None":
        return None
    
    try:
        exp_date = datetime.strptime(str(expiration_date_str), "%Y-%m-%d").date()
        today = datetime.now().date()
        days_left = (exp_date - today).days
        
        if days_left < 0:
            return "expired"
        elif days_left <= warning_days:
            return "expiring_soon"
        else:
            return "ok"
    except:
        return None

def check_medicine_expiration(medicine_id, warning_days=30):
    if medicine_id is None:
        return None
    
    try:
        result = db.execute_query(
            "SELECT MIN(expiration_date) FROM Stock WHERE medicine_id = ? AND quantity > 0",
            (medicine_id,), fetch=True
        )
        if result and result[0][0]:
            return check_expiration(result[0][0], warning_days)
        return None
    except:
        return None

EXPIRATION_WARNING_MESSAGE = (
    "WARNING: This medicine is expired or about to expire.\n\n"
    "Its use and procurement are entirely the responsibility of the user."
)
