TABS_INFO = {
    "Manufacturer": ["manufacturer_id", "company_name", "phone", "address"],
    "Medicines": ["medicine_id", "name", "barcode", "price", "manufacturer_id"],
    "Stock": ["stock_id", "medicine_id", "quantity", "expiration_date"],
    "Patient": ["patient_id", "first_name", "last_name", "tc_no", "birth_date", "phone", "address"],
    "Doctor": ["doctor_id", "first_name", "last_name", "tel_no", "specialization"],
    "Pharmacist": ["p_id", "p_first_name", "p_last_name", "p_tel_no", "p_address", "p_start_date"],
    "Prescription": ["prescription_id", "patient_id", "doctor_id", "prescription_date", "medicine_id"],
    "Sales": ["sale_id", "p_id", "medicine_id", "quantity", "sale_date", "total_price"],
}

KEY_FIELDS = {
    "Manufacturer": ["manufacturer_id"],
    "Medicines": ["name", "manufacturer_id"],
    "Stock": ["stock_id"],
    "Patient": ["patient_id"],
    "Doctor": ["doctor_id"],
    "Pharmacist": ["p_id"],
    "Prescription": ["prescription_id"],
    "Sales": ["sale_id"],
}

AUTO_ID_FIELDS = {"stock_id", "prescription_id", "sale_id", "patient_id"}

INT_FIELDS = {
    "Manufacturer": {"manufacturer_id"},
    "Medicines": {"medicine_id", "manufacturer_id"},
    "Stock": {"stock_id", "medicine_id", "quantity"},
    "Patient": {"patient_id"},
    "Doctor": {"doctor_id"},
    "Pharmacist": {"p_id"},
    "Prescription": {"prescription_id", "patient_id", "doctor_id", "medicine_id"},
    "Sales": {"sale_id", "p_id", "medicine_id", "quantity"},
}

FLOAT_FIELDS = {
    "Medicines": {"price"},
    "Sales": {"total_price"},
}

FK_MAP = {
    "Medicines": {
        "manufacturer_id": ("Manufacturer", "manufacturer_id", "company_name")
    },
    "Stock": {
        "medicine_id": ("Medicines", "medicine_id", "name")
    },
    "Prescription": {
        "patient_id": ("Patient", "patient_id", "first_name"),
        "doctor_id": ("Doctor", "doctor_id", "last_name"),
        "medicine_id": ("Medicines", "medicine_id", "name")
    },
    "Sales": {
        "p_id": ("Pharmacist", "p_id", "p_last_name"),
        "medicine_id": ("Medicines", "medicine_id", "name")
    }
}

REQUIRED_FIELDS = {
    "Manufacturer": ["manufacturer_id", "company_name"],
    "Medicines": ["medicine_id", "name", "manufacturer_id"],
    "Stock": ["medicine_id", "quantity"],
    "Patient": ["first_name", "last_name"],
    "Doctor": ["doctor_id", "first_name", "last_name"],
    "Pharmacist": ["p_id", "p_first_name", "p_last_name"],
    "Prescription": ["patient_id", "doctor_id", "medicine_id"],
    "Sales": ["p_id", "medicine_id", "quantity"],
}
