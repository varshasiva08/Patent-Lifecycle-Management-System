# Patent Lifecycle Management System

---

## Project Overview

The Patent Lifecycle Management System is a robust web-based database application designed to manage the full workflow of intellectual property, specifically patents. Its main goal is to manage all steps of a patent application—from initial filing through the review process, to when it's granted, and even tracking renewals or expiry. The system functions as a central hub, making the entire patent handling process efficient, clear, and easy to track for all involved stakeholders.

The application utilizes a **MySQL** database and a **Streamlit** web interface to enforce business logic through complex queries, stored procedures, functions, and triggers.

---

## Technology Stack 

* **Database (DBMS):** MySQL 
* **Programming Language:** Python 
* **Web Framework/GUI:** Streamlit (Python Library) 
* **Database Connector:** `mysql.connector` 
* **Data Processing:** Pandas 
* **Visualization:** Plotly Express


## Key Features and Roles

The system is designed with strict **Role-Based Security** to control access to essential features.

| User Role | Key Actions (What they can do) |
| :--- | :--- |
| **Administrator** | Manages all patent details, assigns patents to reviewers, updates the official patent status (e.g., "Granted" or "Expired"), and monitors system performance. |
| **Inventor** | Registers, files new patent applications, and checks the status of their own applications. |
| **Reviewer** | Registers, views assigned patents, and submits review decisions (Approve, Reject, or Needs Revision). |
| **Guest/Public** | Views general statistics, uses specialized reports, and files public challenges/oppositions. |

### Advanced Database Functionality

The application includes sophisticated database elements for enhanced data management and reporting:

1.  **Trigger (Status Audit):** A built-in Trigger (`after_patent_status_update`) automatically records every time a patent's `Status` changes into a separate audit table.
2.  **Function (Patent Age Calculator):** An SQL Function (`GetPatentAge`) is defined to calculate the age of a patent in years as a decimal value.
3.  **Procedure (Special Reports):** A Stored Procedure (`GetPatentsByDomain`) allows users to fetch a list of patents based on a specified domain name.
4.  **Complex Queries:** The system utilizes Join, Nested, and Aggregate queries to generate specialized reports for deeper data insights.

---

## Database Schema Overview

The database is built around core entities including **Patents**, **Inventors**, and **Reviewers**, linked via many-to-many relationships (e.g., `Patent_Reviewers` and `Inventor_Patents`).

| Table Name | Primary Keys (PK) / Foreign Keys (FK) | Core Purpose |
| :--- | :--- | :--- |
| **Patents** | `P_ID` (PK) | Stores patent details (Title, Filing Date, Status, Domain). |
| **Inventors** | `I_ID` (PK) | Stores inventor profiles and contact details. |
| **Reviewers** | `R_ID` (PK) | Stores reviewer profiles and professional details. |
| **Patent\_Reviewers** | `P_ID`, `R_ID` (Composite PK/FKs) | Tracks which reviewer is assigned to which patent. |
| **Renewals** | `R_No` (PK), `P_ID` (FK) | Tracks renewal dates and fee status. |
| **Costs** | `Cost_ID` (PK), `P_ID` (FK) | Tracks fees and costs associated with patents]. |

*(See the attached `PES1UG23CS555_PES1UG23CS549.sql` file for complete DDL definitions).*

---

## Getting Started

### Prerequisites

1.  **MySQL Server:** Ensure you have a running MySQL instance (e.g., via XAMPP/WAMP/MAMP or a standalone server).
2.  **Python:** Python 3.x installed.

### Setup Instructions

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/varshasiva08/Patent-Lifecycle-Management-System](https://github.com/varshasiva08/Patent-Lifecycle-Management-System)
    cd Patent-Lifecycle-Management-System
    ```
2.  **Install Dependencies:**
    ```bash
    pip install streamlit mysql-connector-python pandas plotly
    ```
3.  **Database Setup:**
    * Log in to your MySQL server as `root`.
    * Execute the entire contents of the `PES1UG23CS555_PES1UG23CS549.sql` file to create the `patent_system` database, tables, sample data, triggers, functions, and procedures.
    * ***Important:*** Ensure the database credentials in `PES1UG23CS555_PES1UG23CS549.py` match your local MySQL configuration:
        ```python
        host="localhost",
        user="root",
        password="Add your MySQL root password here", 
        database="patent_system",
        ```
4.  **Run the Application:**
    ```bash
    streamlit run app.py
    ```

### Default Login Credentials

* **Admin:** `admin@system.com` / `admin123`
* **Inventor:** `e.reed@qii.com` / `inv123`
* **Reviewer:** `alan@iii.com` / `rev123`
