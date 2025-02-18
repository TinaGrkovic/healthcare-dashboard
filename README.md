# Healthcare Analytics Dashboard  
📊 SQL + Streamlit Dashboard for Healthcare Data Analysis  

## Overview  
This project analyzes **real-world healthcare data** using **SQL and Python**, visualized in an **interactive Streamlit dashboard**.  
It aims to **identify trends in patient admissions, hospital revenue, test results, and patient demographics** to improve decision-making in healthcare settings.

### **Key Features**  
✔️ **Data Cleaning & Wrangling** – Removed missing values, structured dataset for analysis.  
✔️ **SQLite Database Integration** – All data is stored and retrieved using SQL queries.  
✔️ **Streamlit Dashboard** – Interactive and user-friendly data visualization tool.  
✔️ **Dynamic Insights** – Data updates automatically when new records are added.  

---

## Problem Statement  
### **Why This Project?**  
Healthcare providers collect vast amounts of patient and hospital data, but **many hospitals lack the tools** to efficiently analyze and interpret this data.  
This dashboard **bridges the gap** by turning raw data into **actionable insights**.

### **Business Objectives**  
- **Optimize hospital operations** by understanding admission and length-of-stay trends.  
- **Increase revenue insights** by analyzing billing data and insurance trends.  
- **Improve patient care** by identifying common medical conditions and test result trends.  

---

## **Dashboard Structure & Insights**  
The dashboard consists of **five main sections**, each containing multiple tabs for detailed analysis.  

### **🏠 Main Page: Summary & Trends**  
- Provides an **overview of admissions, billing, and test results** across all hospitals.  
- Shows **correlations between billing, length of stay, and medical conditions**.  
- Interactive **filters** for hospital, admission type, and time period.  

### **📊 Financial Insights**  
- Revenue trends by **hospital, admission type, and medical condition**.  
- Identifies the **highest revenue-generating hospitals and insurance providers**.  

### **📊 Demographics & Billing Analysis**  
- Analyzes **how age, gender, and medical conditions impact billing**.  
- Identifies the **most common admission reasons for different demographics**.  

### **📊 Test Results & Medical Conditions**  
- Examines **test result distributions (Normal, Abnormal, Inconclusive)**.  
- Identifies **hospitals with the highest number of abnormal test results**.  

### **📊 Admissions & Hospital Logistics**  
- Breaks down **hospital admission trends** by medical condition and type.  
- Shows **how room assignments impact patient length of stay**.  

---

## **Technical Implementation**  
### **Technology Stack**  
- **SQL (SQLite)** – Used for data storage and queries.  
- **Python (Pandas, NumPy)** – Data processing and transformation.  
- **Streamlit** – Dashboard development for visualization.  
- **Matplotlib / Seaborn** – Data visualization tools.  

### **How It Works**  
1. **Data Processing:** The dataset is cleaned and loaded into a **SQLite database**.  
2. **SQL Queries:** The dashboard dynamically pulls insights using SQL.  
3. **Streamlit Visualization:** Charts and tables are generated from the query results.  

---

## **Installation & Setup**  
1. **Clone the repository**  
   ```sh
   git clone https://github.com/TinaGrkovic/healthcare-dashboard.git
   cd healthcare-dashboard
2. **Install dependencies**  
   ```sh
   pip install -r requirements.txt
3. **Run the Streamlit app**  
   ```sh
   streamlit run dashboard.py
