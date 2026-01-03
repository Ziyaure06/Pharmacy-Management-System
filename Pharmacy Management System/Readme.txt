# Pharmacy Management System 🏥

A comprehensive and robust desktop application developed to streamline pharmacy operations, including drug inventory tracking, automated sales processing, and detailed financial reporting. This project was developed as part of the **CENG 301** curriculum.

## 🚀 Key Features
* **Inventory Tracking:** Real-time monitoring of drug stocks with the ability to add, update, and remove items.
* **Quick Sales Interface:** A user-friendly Point of Sale (POS) system for rapid transaction handling.
* **Automated Reporting:** Generate instant reports on sales performance and stock levels to support business decisions.
* **Persistent Storage:** Utilizes a local SQLite database for secure and efficient data management.
* **Modular Architecture:** Organized code structure with separate handlers for database queries and UI widgets for better maintainability.

## 🛠️ Tech Stack
* **Language:** Python 3.x
* **Database:** SQLite
* **UI Components:** Modular Python-based widgets

## 📁 Project Structure
The project is organized into the following key files and directories:
* `main.py`: The main entry point of the application.
* `database.py`: Manages SQLite connection and table initialization.
* `queries.py`: Centralized location for SQL query logic.
* `widgets/`: Directory containing specific UI panels like `quick_sale.py` and `reports_panel.py`.

## 🔧 Installation and Usage

To get this project running on your local machine, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/your-username/your-repository-name.git](https://github.com/your-username/your-repository-name.git)

Run the application:
python main.py