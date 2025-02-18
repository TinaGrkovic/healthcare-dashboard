import sqlite3
import pandas as pd
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt 
import seaborn as sns
import plotly.express as px
import altair as alt

st.set_page_config(layout='wide')
# file path
database_path = 'healthcare_database.db'

# create a connection to the SQL db
connection = sqlite3.connect(database_path)

# create a cursor object instance, to execulte SQL queries
curser = connection.cursor()

st.header("Demographics and Billing Analysis")

# Tabs for Different Charts
tab1, tab2, tab3 = st.tabs(["Commonn Age Groups", "Billing Amount by Age", "Billing by Gender"])

with tab1:
    # Streamlit UI for dropdown filter
    st.subheader("Most Common Age Group by Admission Type for Each Hospital")

    # Query to fetch unique hospital names
    hospital_query = "SELECT DISTINCT Hospital FROM Healthcare_Dataset;"
    curser.execute(hospital_query)
    hospitals = [row[0] for row in curser.fetchall()]

    # Single-select dropdown for hospitals
    selected_hospital = st.selectbox("Select a Hospital:", options=hospitals)

    # Query to fetch data based on the selected hospital
    query = f"""
    SELECT 
    Admission_Type,
    Age_Group,
    COUNT(*) AS admission_count
    FROM Healthcare_Dataset
    WHERE Hospital = '{selected_hospital}'
    GROUP BY Admission_Type, Age_Group
    ORDER BY Admission_Type, admission_count DESC;
    """

    # Execute the query and fetch results
    curser.execute(query)
    results = curser.fetchall()
    df = pd.DataFrame(results, columns=['Admission_Type', 'Age_Group', 'admission_count'])

    # Check if there is data for the selected hospital
    if df.empty:
        st.warning(f"No data available for the selected hospital: {selected_hospital}")
    else:
        # Create a subplot with 3 pie charts (one for each admission type)
        admission_types = ['Emergency', 'Elective', 'Urgent']  # Ensure all expected admission types are included
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))

        for i, admission_type in enumerate(admission_types):
            # Filter data for the current admission type
            admission_df = df[df['Admission_Type'] == admission_type]
            
            if admission_df.empty:
                # Display "Not Applicable" for missing data
                axes[i].pie([1], labels=["Not Applicable"], colors=["lightgrey"], startangle=90)
                axes[i].set_title(f"{admission_type}")
            else:
                # Plot pie chart for available data
                axes[i].pie(
                    admission_df['admission_count'], 
                    labels=admission_df['Age_Group'], 
                    autopct='%1.1f%%', 
                    startangle=90, 
                    colors=plt.cm.Paired.colors
                )
                axes[i].set_title(f"{admission_type}")

        # Display the pie charts in Streamlit
        st.pyplot(fig)

        # Summary statistics
        st.subheader(f"Prominent Age Groups Overview for {selected_hospital}")
        summary = (
            df.groupby('Admission_Type')
            .apply(lambda x: x.loc[x['admission_count'].idxmax(), ['Age_Group', 'admission_count']]
                if not x.empty else pd.Series({'Age_Group': 'Not Applicable', 'admission_count': 0}))
            .reset_index()
            .rename(columns={'Age_Group': 'Most Common Age Group', 'admission_count': 'Admission Count'})
        )

        # Ensure all data types are JSON serializable
        summary['Admission Count'] = summary['Admission Count'].astype(int)  # Convert to Python int
        summary['Most Common Age Group'] = summary['Most Common Age Group'].astype(str)  # Convert to Python str

        # Convert entire DataFrame to a dictionary for compatibility
        summary_dict = summary.to_dict(orient='records')

        # Display the summary using Streamlit's `st.table` for better handling
        st.table(summary_dict)
  #Description in container
    container = st.container(border=True)
    container.write("""This dashboard provides a detailed analysis of the most common admission types across different age groups for a selected hospital. Users can filter the data by selecting a hospital from the dropdown menu, which dynamically updates the visualizations and summary statistics. The tab includes three pie charts, each representing the distribution of age groups for the admission types: Emergency, Elective, and Urgent. If a particular admission type is not applicable to the selected hospital, it is indicated in the chart. Below the visualizations, summary statistics highlight the most prominent age group for each admission type, offering valuable insights into patient demographics and their relationship with hospital admission trends. This tool aids healthcare professionals and administrators in understanding patient distributions, improving resource allocation, and identifying key demographic trends for specific hospitals.""") 




with tab2:
  # How does average billing amount differ by age group?
  st.subheader ("Average Billing Amount By Age Group")
  quiery11= """ SELECT 
  Age_Group, AVG(billing_amount) AS avg_billing_amount
  FROM Healthcare_Dataset 
  GROUP BY Age_Group"""
  # execute the query 
  curser.execute(quiery11)

  # fetch all of the results from the executed query
  results = curser.fetchall()

  columns = ["Age_Group","avg_billing_amount"]
  results_df = pd.DataFrame(results, columns=columns)

  # fetch all of the results from the executed query
  fig = px.bar(results_df, x="Age_Group" , y="avg_billing_amount", labels={"Age_Group": "Age Group", "avg_billing_amount":"Average Billing Amount"},)

  st.plotly_chart(fig, use_container_width=True)

  #Description in container
  container = st.container(border=True)
  container.write("""This bar chart visualizes the average billing amount by age group, bringing awareness on how healthcare changes across different age groups. By examining the height of each bar, users can identify which age groups incur higher healthcare costs. This helps not only healthcare workers but patients understand financial demands and constraints of healthcare cost based on age group.This also helps with resource allocation, insurance and financial planning.""") 

with tab3: 
  # Billing amount by admission type and gender
  query_billing = """
      SELECT 
          Billing_Amount, 
          Medical_Condition, 
          Gender
      FROM Healthcare_Dataset
      WHERE Billing_Amount >= 0;
      """
  billing_data = pd.read_sql_query(query_billing, connection)

  # Title
  st.subheader("Billing Amount by Admission Type and Gender")

  # Add a Multiselect Filter for Admission Type
  selected_admission_types = st.selectbox("Filter by Medical Condition", 
  options=billing_data["Medical_Condition"].unique(), index=0)

      # Filter Data Based on Selected Admission Types
  filtered_data = billing_data[billing_data["Medical_Condition"] == selected_admission_types]

      # Plot Boxplot with Admission_Type on X-Axis
  fig_billing = px.box(
          filtered_data, 
          x="Medical_Condition", 
          y="Billing_Amount", 
          color="Gender",
          labels={"Billing_Amount": "Billing Amount", "Medical_Condition":""},
          boxmode="group"
      )
  st.plotly_chart(fig_billing, use_container_width=True)

  #Description in container
  container = st.container(border=True)
  container.write("""This box plot shows the distribution of billing amounts by gender for a selected medical condition. Use the dropdown menu to filter by condition and explore differences in billing patterns between male and female patients. The plot highlights the median, range, and any variability in billing amounts for the chosen condition.""")









