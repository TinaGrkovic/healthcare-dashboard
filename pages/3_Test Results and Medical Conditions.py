#load packages
import sqlite3
import pandas as pd
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

#set configuration to wide
st.set_page_config(layout='wide')

#create header
st.header("Test Results and Medical Conditions")


# set db file path
database_path = 'healthcare_database.db'

# create a connection to the SQL db
connection = sqlite3.connect(database_path)

# create a cursor object instance, to execulte SQL queries
cursor = connection.cursor()

#create tabs for visualizations
tab1, tab2, tab3 = st.tabs(["Abnormal Test Results and Conditions", "Test Results and Admissions", "Medications and Conditions"])

with tab1:
##Q1
#What are the most common medical conditions with test results marked as "Abnormal" by Age?
    st.subheader("Most Common Medical Conditions with Abnormal Test Results by Age")
    queryA1 = """SELECT  count(Name) as Number, Medical_Condition, Age
    from Healthcare_Dataset 
    where Test_Results = "Abnormal"
    group by Medical_Condition, Age """
# execute the query 
    cursor.execute(queryA1)

# Fetch the results
    results = cursor.fetchall()

# Convert the results into a pandas DataFrame
    results_df = pd.DataFrame(results, columns=["Number", "Medical_Condition", "Age"])

#list of unique ages
    age_options = results_df['Age'].unique()

#make age an integer if it is a string
    age_options = [int(age) if isinstance(age, str) else age for age in age_options]

# default all ages
    default_age = [age for age in age_options] 

# Create a multiselect widget by age
    age_selection = st.multiselect('Select Age(s):', options=age_options, default=default_age)

    if not age_selection:
        st.warning("No age selected, showing all data.")
        age_selection = age_options  # Show data for all ages if no age is selected

# Filter the DataFrame based on the selected ages
    filtered_df = results_df[results_df['Age'].isin(age_selection)]

# Aggregate the data by Medical_Condition and sum the counts for selected age
    aggregated_data = filtered_df.groupby('Medical_Condition')['Number'].sum().reset_index()

# Sort the data in descending order of count
    aggregated_data = aggregated_data.sort_values('Number', ascending=False)

# Display the bar chart for the aggregated data
    st.bar_chart(aggregated_data.set_index('Medical_Condition'))

#Description in container
    container_one = st.container(border=True)
    container_one.write("The most common medical conditions with abnormal test results in this data are arthritis and diabetes when all age groups are considered. Among individuals under 25, arthritis leads in abnormal results, followed by cancer and obesity. This suggests that diabetes management may improve with early intervention, while obesity-related complications are also evident in younger populations. For patients over 65, arthritis remains the most common condition with abnormal results, followed by cancer and diabetes. The transformation from obesity to diabetes abnormal results suggest that untreated obesity may be correlated with the potential onset of diabetes.")

with tab2:
##Q2
#What test results are the different types of admissions receiving?"?
#subheader
    st.subheader("Test Results of Different Types of Admissions")
    queryA2 = """SELECT 
        Admission_Type, 
        Test_Results, 
        COUNT(*) AS Admission_Count
    FROM 
        Healthcare_Dataset
    GROUP BY 
        Admission_Type, Test_Results"""

# execute the query 
    cursor.execute(queryA2)

#get results
    results = cursor.fetchall()

#results in df
    results = pd.DataFrame(results, columns=["Admission_Type", "Test_Results", "Admission_Count"])

# Create a pivot table for the bar chart
    pivot_data = results.pivot_table(index='Admission_Type', columns='Test_Results', values='Admission_Count', aggfunc='sum').fillna(0)

# Display the regular bar chart (horizontal)
    st.bar_chart(pivot_data.T)  #test results in columns

#Description
    container_two= st.container(border= True)
    container_two.write("This stacked bar chart illustrates the test results categorized by admission type, showing the counts of each type of admission receiving those results. The data indicates that the category of admission does not significantly influence the test results a patient receives. This suggests that some emergency or urgent visits may not be truly critical and could potentially be addressed with a standard visit, therefore saving hospitals time and resources.")

with tab3:
##Q3
#What is the most common medication for each medical condition?
    st.subheader("Most Common Medications by Condition")
    queryA3 = """SELECT 
        Medical_Condition, 
        Medication, 
        COUNT(*) AS MedicationCount
    FROM Healthcare_Dataset
    GROUP BY Medical_Condition, Medication;
    """

# execute the query 
    cursor.execute(queryA3)

#results from the executed query
    results = cursor.fetchall()

# Convert the results into a df
    results_df = pd.DataFrame(results, columns=["Medical_Condition", "Medication", "MedicationCount"])

# Create a list of unique medical conditions 
    medical_condition_options = results_df['Medical_Condition'].unique()

# Create a selectbox widget 
    condition_selection = st.selectbox('Select Medical Condition:', options=medical_condition_options)

# Filter the df by condition
    filtered_df = results_df[results_df['Medical_Condition'] == condition_selection]

# Display the filtered data
    st.dataframe(filtered_df)

# Plot the filtered data in a bar chart
    st.bar_chart(filtered_df.set_index('Medication')['MedicationCount'])

#Description
    container_three = st.container(border= True)
    container_three.write("The above bar chart illustrates the most common medications prescribed for the most common medical conditions in this data. An interesting insight of the data is that cancer and diabetes both share lipitor as the category's most common medications. Lipitor is considered a statin and is utilized to reduce the levels of bad cholesterol in the body. In turn, Lipitor can reduce the risk of heart attack or stroke, which may explain why it is prescribed for both conditions. Another key finding in the data is that the most common medication prescribed for obesity is Penicillin. Penicillin is an antibiotic used to treat bacterial infections. This suggests that obesity is possibly correlated with a higher rate of infections than the general population.")

# close the database connection
connection.close()

