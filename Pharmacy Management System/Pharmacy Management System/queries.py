class SQLQueries:
    
    @staticmethod
    def get_medicines_with_stock():
        return '''
            SELECT m.medicine_id, m.name, m.barcode, m.price,
                COALESCE(SUM(s.quantity), 0) as total_stock,
                mf.company_name as manufacturer
            FROM Medicines m
            LEFT JOIN Stock s ON m.medicine_id = s.medicine_id
            LEFT JOIN Manufacturer mf ON m.manufacturer_id = mf.manufacturer_id
            GROUP BY m.medicine_id, m.name, m.barcode, m.price, mf.company_name
        '''
    
    @staticmethod
    def get_low_stock(threshold=10):
        return f'''
            SELECT m.medicine_id, m.name, COALESCE(SUM(s.quantity), 0) as stock
            FROM Medicines m
            LEFT JOIN Stock s ON m.medicine_id = s.medicine_id
            GROUP BY m.medicine_id, m.name
            HAVING stock < {threshold}
            ORDER BY stock
        '''
    
    @staticmethod
    def get_expiring_soon(days=30):
        return f'''
            SELECT m.name, s.quantity, s.expiration_date,
                   CAST(julianday(s.expiration_date) - julianday('now') AS INTEGER) as days_left
            FROM Stock s
            JOIN Medicines m ON s.medicine_id = m.medicine_id
            WHERE s.expiration_date <= date('now', '+{days} days')
              AND s.quantity > 0
            ORDER BY s.expiration_date
        '''
    
    @staticmethod
    def get_daily_sales():
        return '''
            SELECT date(sale_date) as day, COUNT(*) as sales, SUM(total_price) as revenue
            FROM Sales WHERE sale_date IS NOT NULL
            GROUP BY date(sale_date)
            ORDER BY day DESC LIMIT 30
        '''
    
    @staticmethod
    def get_top_selling(limit=10):
        return f'''
            SELECT m.name, SUM(s.quantity) as sold, SUM(s.total_price) as revenue
            FROM Sales s
            JOIN Medicines m ON s.medicine_id = m.medicine_id
            GROUP BY m.medicine_id, m.name
            ORDER BY sold DESC LIMIT {limit}
        '''
    
    @staticmethod
    def get_oldest_patient():
        return '''
            SELECT patient_id, first_name, last_name, birth_date,
                   CAST((julianday('now') - julianday(birth_date)) / 365 AS INTEGER) as age
            FROM Patient
            WHERE birth_date IS NOT NULL
            ORDER BY birth_date ASC LIMIT 1
        '''
