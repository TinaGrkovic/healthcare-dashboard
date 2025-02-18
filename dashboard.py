import sqlite3
import pandas as pd
import streamlit as st
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
from datetime import datetime
from wordcloud import WordCloud

st.set_page_config(layout='wide')

# Database Connection
database_path = 'healthcare_database.db'
connection = sqlite3.connect(database_path)

# Query to Load Full Dataset
query = """SELECT * FROM "Healthcare_Dataset";"""
data = pd.read_sql_query(query, connection)

st.header('Summary of Healthcare Data in 2014-2019')

# Tabs for Different Charts
tab1, tab2, tab3 = st.tabs(["Data Summary", "Revenue Summary", "Demographics Summary"])

# Welcome message in the sidebar
st.sidebar.markdown("""
### Welcome!

This dashboard provides insights into healthcare data trends, including financial metrics, patient demographics, 
hospital admission logistics, and medical conditions.

**Navigate to the above pages for in-depth analysis**
""")

# Home Summary & Statistics --------------------------------------------------------------------------------------------------------
with tab1:
    # Interactive Search Section
    st.subheader('Search the Dataset')
    search_query = st.text_input("Search by Name, Hospital, Doctor, or Medical Condition").lower()

    # Modify Query if Search Query is Provided
    if search_query:
        query = f"""
        SELECT * 
        FROM "Healthcare_Dataset" 
        WHERE 
            Name LIKE '%{search_query}%' OR 
            Hospital LIKE '%{search_query}%' OR
            Doctor LIKE '%(search_query)%' OR 
            Medical_Condition LIKE '%{search_query}%';
        """

    # Fetch Data Using Updated Query
    data = pd.read_sql_query(query, connection)

    # Drop first column
    data = data.iloc[:, 1:]

    # Display Data
    st.write(f"Showing results for search: **'{search_query}'**" if search_query else "Showing all data:")
    st.dataframe(data, use_container_width=True)


    # Summary Statistics Section
    st.subheader('Summary Statistics')
    col1, col2, col3 = st.columns(3)

    # Total Records
    query_total_records = """SELECT COUNT(*) AS total_records FROM "Healthcare_Dataset";"""
    total_records = pd.read_sql_query(query_total_records, connection)['total_records'][0]
    col1.metric("Total Records", total_records)

    # Unique Hospitals
    query_unique_hospitals = """SELECT COUNT(DISTINCT Hospital) AS unique_hospitals FROM "Healthcare_Dataset";"""
    unique_hospitals = pd.read_sql_query(query_unique_hospitals, connection)['unique_hospitals'][0]
    col2.metric("Unique Hospitals", unique_hospitals)

    # Unique Medical Conditions
    query_unique_conditions = """SELECT COUNT(DISTINCT Medical_Condition) AS unique_conditions FROM "Healthcare_Dataset";"""
    unique_conditions = pd.read_sql_query(query_unique_conditions, connection)['unique_conditions'][0]
    col3.metric("Unique Medical Conditions", unique_conditions)

    # Additional Summary Statistics
    st.subheader("Additional Statistics")
    col4, col5, col6 = st.columns(3)

    # Billing Amount Statistics
    query_billing_stats = """
    SELECT 
        AVG(Billing_Amount) AS avg_billing, 
        MAX(Billing_Amount) AS max_billing, 
        MIN(Billing_Amount) AS min_billing 
    FROM "Healthcare_Dataset";
    """
    billing_stats = pd.read_sql_query(query_billing_stats, connection)
    avg_billing = billing_stats['avg_billing'][0]
    max_billing = billing_stats['max_billing'][0]
    min_billing = billing_stats['min_billing'][0]

    col4.metric("Avg Billing Amount", f"${avg_billing:,.0f}")
    col5.metric("Max Billing Amount", f"${max_billing:,.0f}")
    col6.metric("Min Billing Amount", f"${min_billing:,.0f}")

    # Average Length of Stay
    query_avg_length_of_stay = """SELECT AVG(Total_Days_of_Stay) AS avg_length_of_stay FROM "Healthcare_Dataset";"""
    avg_length_of_stay = pd.read_sql_query(query_avg_length_of_stay, connection)['avg_length_of_stay'][0]
    col4.metric("Avg Length of Stay", f"{avg_length_of_stay:.1f} days")
    
    #Description in container
    container = st.container(border=True)
    container.write("""This synthetic healthcare dataset, covering 55,500 records from 2014 to 2019,
                     provides comprehensive insights into patient demographics, medical conditions, 
                    hospital operations, and financial details. With data from 39,876 unique hospitals 
                    and 6 distinct medical conditions, it enables users to analyze healthcare trends 
                    and develop predictive models. It includes details on demographics, medical conditions, 
                    hospital stays, billing amounts, test results, and more. By exploring this data, users 
                    can uncover healthcare trends, analyze hospital operations, evaluate patient outcomes. 
                    The dataset serves 
                    as a valuable resource for studying real-world healthcare scenarios while safeguarding 
                    patient confidentiality""")


# Revenue Trends --------------------------------------------------------------------------------------------------------
with tab2:
    st.subheader("Monthly Revenue Trends")

    # SQL Query to Aggregate Monthly Revenue
    query_revenue = """
    SELECT 
        strftime('%Y-%m', Date_of_Admission) AS Month, 
        SUM(Billing_Amount) AS Total_Revenue
    FROM Healthcare_Dataset
    WHERE Billing_Amount >= 0
    GROUP BY Month
    ORDER BY Month;
    """
    revenue_data = pd.read_sql_query(query_revenue, connection)

    # Plot Line Chart
    fig_revenue = px.line(
        revenue_data, 
        x="Month", 
        y="Total_Revenue", 
        title="Revenue by Year",
        labels={"Month": "Year", "Total_Revenue": "Total Revenue"}
    )
    st.plotly_chart(fig_revenue, use_container_width=True)

    # Query data for bar graph
    query_monthlyrev = """
    SELECT 
        strftime('%Y', Date_of_Admission) AS Year, 
        strftime('%m', Date_of_Admission) AS Month, 
        SUM(Billing_Amount) AS Total_Revenue
    FROM Healthcare_Dataset
    WHERE Billing_Amount >= 0
    GROUP BY Year, Month
    ORDER BY Year, Month;
    """
    monthly_revenue_data = pd.read_sql_query(query_monthlyrev, connection)

    # Add a column to convert Month to full name
    monthly_revenue_data["Month_Full"] = monthly_revenue_data["Month"].apply(lambda x: datetime.strptime(x, "%m").strftime("%B"))

    # Selectbox for filtering by month
    selected_month = st.selectbox(
        "Select a Month",
        options=monthly_revenue_data["Month_Full"].unique()
    )

    # Filter data for the selected month
    filtered_data = monthly_revenue_data[monthly_revenue_data["Month_Full"] == selected_month]

    # Bar graph
    fig_monthlyrev = px.bar(
        filtered_data,
        x="Year",
        y="Total_Revenue",
        text="Total_Revenue",
        title=f"Revenues in {selected_month}",
        labels={"Total_Revenue": "Total Revenue", "Year": selected_month}
    )
    fig_monthlyrev.update_traces(texttemplate='%{text:.2s}', textposition='outside')  # Format bar labels
    st.plotly_chart(fig_monthlyrev, use_container_width=True)

    # Summary statistics for revenue trends
    st.subheader("Summary Statistics for Revenue Trends")

    # Calculate summary metrics
    total_revenue = revenue_data["Total_Revenue"].sum()
    average_monthly_revenue = revenue_data["Total_Revenue"].mean()
    max_revenue = revenue_data["Total_Revenue"].max()
    min_revenue = revenue_data["Total_Revenue"].min()
    max_revenue_month = revenue_data.loc[revenue_data["Total_Revenue"].idxmax(), "Month"]
    min_revenue_month = revenue_data.loc[revenue_data["Total_Revenue"].idxmin(), "Month"]

    # Format the month for highest and lowest revenue
    max_revenue_month_formatted = datetime.strptime(max_revenue_month, "%Y-%m").strftime("%B %Y")
    min_revenue_month_formatted = datetime.strptime(min_revenue_month, "%Y-%m").strftime("%B %Y")


    # Display metrics
    st.write(f"**Total Revenue (All Months):** ${total_revenue:,.2f}")
    st.write(f"**Average Monthly Revenue:** ${average_monthly_revenue:,.2f}")
    st.write(f"**Highest Monthly Revenue:** ${max_revenue:,.2f} ({max_revenue_month_formatted})")
    st.write(f"**Lowest Monthly Revenue:** ${min_revenue:,.2f} ({min_revenue_month_formatted})")

    con = st.container(border=True)
    con.write("""The revenue summary provides key insights into hospital billing trends over time, 
              highlighting consistent revenue generation with notable fluctuations. The line chart 
              reveals steady performance across most months, with peaks in revenue during specific 
              periods, such as October 2019, which had the highest monthly revenue of 26.3M. A sharp 
              decline is observed in May 2024, where revenue dropped significantly to 5.4M, compared 
              to the average monthly revenue of 23.2M. The bar chart further explores revenue trends 
              for May across years, showing a peak in 2020 at 25M, followed by consistent performance 
              until 2024. Overall, total revenue across all months amounts to 1.42B. These trends 
              suggest opportunities for deeper analysis into seasonal and operational factors driving 
              revenue fluctuations, especially the sharp dip in May 2024, which may require targeted 
              financial planning and investigation.""")

              
# Which factors (e.g., age group, admission type, or length of stay) have the strongest relationship with billing amounts?
with tab3:
    # Query for demographics data
    query_demosum = """
    SELECT 
        Age, 
        Gender, 
        Blood_Type, 
        Insurance_Provider
    FROM Healthcare_Dataset;
    """
    demographics_data = pd.read_sql_query(query_demosum, connection)

    # Demographics Summary Statistics
    st.subheader("Demographics Summary")
    mean_age = demographics_data["Age"].mean()
    median_age = demographics_data["Age"].median()
    gender_counts = demographics_data["Gender"].value_counts()

    # Display Summary Statistics
    st.write(f"**Gender Distribution:**")
    st.dataframe(gender_counts)

    # Horizontal Bar Chart for Top Insurance Providers
    insurance_provider_counts = demographics_data["Insurance_Provider"].value_counts()
    insurance_fig = px.bar(
    insurance_provider_counts,
    x=insurance_provider_counts.values,
    y=insurance_provider_counts.index,
    orientation="h",
    title="Patient Insurance Providers"
    )
    
    # Explicitly set axis labels
    insurance_fig.update_layout(
    xaxis_title=" ",
    yaxis_title="Insurance Provider"
    )

    st.plotly_chart(insurance_fig, use_container_width=True)

    # Histogram for Age Distribution
    age_fig = px.histogram(
    demographics_data,
    x="Age",
    nbins=5,
    title="Patient Age Distribution"
    )

    # Explicitly set axis labels
    age_fig.update_layout(
    xaxis_title="Age",
    yaxis_title="Frequency",
    bargap=0.1
    )

    st.plotly_chart(age_fig, use_container_width=True)
    
    # Age summary
    st.write(f"**Mean Age:** {mean_age:.1f} years")
    st.write(f"**Median Age:** {median_age:.1f} years")

    #Description in container
    container = st.container(border=True)
    container.write("""The demographics summary provides a comprehensive overview of the patient population, 
                    highlighting key characteristics such as gender distribution, age distribution, and 
                    insurance provider preferences. The dataset reveals an almost equal split between male 
                     and female patients, ensuring balanced representation. The age 
                    distribution shows that the majority of patients fall into middle-aged and senior 
                    categories, with an average patient age of around 50 years. 
                    Insurance providers play a crucial role, with UnitedHealthcare, Aetna, Blue Cross, 
                    Medicare, and Cigna serving a significant portion of the population. These insights 
                    provide a comprehensive understanding of the patient demographics and their financial 
                    implications within the healthcare system. """)


# close the database connection
connection.close()

# What are the most common medical conditions, and which generate the most revenue?