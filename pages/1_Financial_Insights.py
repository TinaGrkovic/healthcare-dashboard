import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import sqlite3
import altair as alt


database_path = 'healthcare_database.db'

connect = sqlite3.connect('healthcare_database.db')

# Sidebar for adjusting rows
st.sidebar.title("Financial Dashboard Settings")
limit = st.sidebar.slider("Number of rows to display:", 10, 1000, 100, 10)
st.sidebar.info("Adjust the settings to filter and optimize your view.")

# explanation for the row limit
st.sidebar.markdown("""
**Why Limit the Rows?**  
To ensure the dashboard performs efficiently and provides a smooth user experience, we have set a limit on the number of rows displayed. This approach minimizes load times and enhances interactivity, especially when analyzing large datasets.
""")

cursor = connect.cursor()
#total revenue by hospital
hospital_revenue = pd.read_sql_query(f"""SELECT Hospital, SUM(Billing_Amount) AS Total_Revenue FROM Healthcare_Dataset GROUP BY Hospital ORDER BY Total_Revenue DESC LIMIT {limit}""", connect)

#admission by hospital revenue
admission_hospital_revenue = pd.read_sql_query(f"""SELECT 
    Hospital,
    Admission_Type,
    SUM(Billing_Amount) AS Revenue
FROM Healthcare_Dataset 
GROUP BY Hospital, Admission_Type
ORDER BY Revenue DESC
LIMIT {limit};""", connect)

#medical condition and insurance revenue
medical_condition_insurance_revenue = pd.read_sql_query(f"""SELECT 
    Medical_Condition,
    Insurance_Provider,
    SUM(Billing_Amount) AS Revenue
FROM Healthcare_Dataset 
GROUP BY Medical_Condition, Insurance_Provider
ORDER BY Revenue DESC
LIMIT {limit};""", connect)


#avg billing by medical type and by hospital 
avg_billing_by_type_hospital = pd.read_sql_query(f"""SELECT 
    Admission_Type,
    Hospital,                                            
    AVG(Billing_Amount) AS Avg_Billing
FROM Healthcare_Dataset 
GROUP BY Admission_Type, Hospital ORDER BY Avg_Billing DESC LIMIT {limit};""", connect)



#avg billing amount by admission type 
query_5 = pd.read_sql_query(f"""
SELECT 
    Admission_Type,
    AVG(Billing_Amount) AS Avg_Billing
FROM Healthcare_Dataset 
GROUP BY Admission_Type ORDER BY Avg_Billing DESC LIMIT {limit};
""", connect)
#cursor.execute(query_5)

#top rev generating medical condition x insurance provider 
query_6 = pd.read_sql_query("""
SELECT 
    Medical_Condition,
    Insurance_Provider,
    SUM(Billing_Amount) AS Total_Revenue
FROM Healthcare_Dataset 
GROUP BY Medical_Condition, Insurance_Provider
ORDER BY Total_Revenue DESC
LIMIT 1;
""", connect)
#cursor.execute(query_6)
results = cursor.fetchall()
results_df = pd.DataFrame(results, columns=['Medical_Condition', 'Insurance_Provider', 'Total_Revenue'])


#get results from query
results = cursor.fetchall()
results = pd.DataFrame(results)
print(results)

st.header("Financial Insights and Revenue Analysis")
tab1, tab2, tab3 = st.tabs(["Revenue Analysis", "Trends by Hospital Admission Type", "Insurance & Medical Condition"])


#THIS IS THE START OF TAB ONE IN PAGE ONE
# Tab 1: Revenue Analysis
with tab1:
    st.subheader("Highest Revenues by Hospital")

    # Summary statistics
    total_revenue = medical_condition_insurance_revenue['Revenue'].sum()

    # Display the summary
    st.markdown(f"""
    - **Total Revenue**: ${total_revenue:,.0f}
    """)

    # Select hospitals with multiselect
    selected_hospitals = st.multiselect(
        "Search to select one or more hospitals:",
        hospital_revenue['Hospital'].unique(),  
        help="Search and select hospitals from the dropdown."
    )

    # Filter the data for selected hospitals
    if selected_hospitals:
        filtered_hospital_revenue = hospital_revenue[hospital_revenue['Hospital'].isin(selected_hospitals)]
    else: 
        filtered_hospital_revenue = hospital_revenue 

    st.write(filtered_hospital_revenue.round(0))

    # Check if the filtered data has only one unique revenue value
    min_revenue = filtered_hospital_revenue['Total_Revenue'].min()
    max_revenue = filtered_hospital_revenue['Total_Revenue'].max()
    if filtered_hospital_revenue['Total_Revenue'].nunique() == 1:
        st.warning("All records have the same revenue value.")
        min_revenue = max_revenue = filtered_hospital_revenue['Total_Revenue'].iloc[0]
    else:
        # Revenue range filter
        revenue_range = st.slider(
            "Select Revenue Range: ",
            min_value=int(filtered_hospital_revenue['Total_Revenue'].min()),
            max_value=int(filtered_hospital_revenue['Total_Revenue'].max()),
            value=(
                int(filtered_hospital_revenue['Total_Revenue'].min()),
                int(filtered_hospital_revenue['Total_Revenue'].max()),     
            ), 
        )
        min_revenue, max_revenue = revenue_range

    filtered_hospital_revenue = filtered_hospital_revenue[
        (filtered_hospital_revenue['Total_Revenue'] >= min_revenue) & 
        (filtered_hospital_revenue['Total_Revenue'] <= max_revenue)
    ]
    
    # Display the selected revenue range 
    st.write(f"Selected Revenue Range: {min_revenue} - {max_revenue}")

    # Display the filtered data
    # Sort the data by Total_Revenue in descending order
    filtered_hospital_revenue = filtered_hospital_revenue.sort_values(by='Total_Revenue', ascending=False)

    # Create the Altair chart
    chart = alt.Chart(filtered_hospital_revenue).mark_bar().encode(
        x=alt.X('Hospital:N', sort='-y', title='Hospital'),  # Sort x-axis by descending revenue
        y=alt.Y('Total_Revenue:Q', title='Total Revenue')
    ).properties(
        title="Hospitals Generating Highest Revenue",
        width=800,
        height=400
    )
    st.altair_chart(chart, use_container_width=True)
    #st.bar_chart(filtered_hospital_revenue[['Hospital', 'Total_Revenue']].set_index('Hospital'))
    
    # Revenue for second part with selected hospitals
    st.subheader("Revenue by Admission Type and Hospital (Select Hospital for Graph)")

    if selected_hospitals:  
        for selected_hospital in selected_hospitals:  
            st.write(f"Admission type revenue comparison for {selected_hospital}")

            hospital_data = admission_hospital_revenue[admission_hospital_revenue['Hospital'] == selected_hospital]

            if hospital_data.empty:
                st.write(f"No data available for {selected_hospital}")
            else:
                fig, ax = plt.subplots(figsize=(10, 6))
                sns.barplot(
                    data=hospital_data,
                    x="Admission_Type",
                    y="Revenue",
                    ax=ax,
                    estimator="mean", 
                    ci=None  
                )
                st.pyplot(fig)

    connect.close()  

# THIS IS THE START OF TAB 2 IN PAGE 1


with tab2:
    st.subheader("Average Billing by Admission Type and Hospital")
    #st.write(avg_billing_by_type_hospital)

    selected_hospitals = st.multiselect(
        "Search to select one or more hospitals:",
        avg_billing_by_type_hospital['Hospital'].unique(),  
        help="Search and select hospitals from the dropdown.",
        key="hospital_select_tab2"  
    )


    # Filter the data based on selected hospitals
    if selected_hospitals:
        filtered_avg_billing = avg_billing_by_type_hospital[avg_billing_by_type_hospital['Hospital'].isin(selected_hospitals)]
    else:
        filtered_avg_billing = avg_billing_by_type_hospital

    
    
    # Filter the data for selected admission types
    selected_admission_types = st.multiselect(
        "Search to select one or more admission types:",
        filtered_avg_billing['Admission_Type'].unique(),
        help="Search and select admission types from the dropdown.",
        key="admission_type_select_tab2" 
    )
    
    if selected_admission_types:
        filtered_avg_billing = filtered_avg_billing[filtered_avg_billing['Admission_Type'].isin(selected_admission_types)]

    #st.write(filtered_avg_billing)



    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        data=avg_billing_by_type_hospital,
        x="Admission_Type",
        y="Avg_Billing",
        ax=ax
    )
    st.pyplot(fig)

connect.close()  

#THIS IS THE START OF TAB 3


with tab3:
    st.subheader("Highest Revenue Insurance Provider")

    # Summary statistics
    top_condition = medical_condition_insurance_revenue.groupby('Medical_Condition')['Revenue'].sum().idxmax()
    top_condition_revenue = medical_condition_insurance_revenue.groupby('Medical_Condition')['Revenue'].sum().max()
    top_insurance = medical_condition_insurance_revenue.groupby('Insurance_Provider')['Revenue'].sum().idxmax()
    top_insurance_revenue = medical_condition_insurance_revenue.groupby('Insurance_Provider')['Revenue'].sum().max()

    # Display the summary
    st.markdown(f"""
    - Top Medical Condition: **{top_condition} wiith ${top_condition_revenue:,.0f}**
    - Top Insurance Provider: **{top_insurance} with ${top_insurance_revenue:,.0f}**
    """)    
    
    selected_conditions = st.multiselect(
        "Search to select one or more medical conditions: ",
        medical_condition_insurance_revenue['Medical_Condition'].unique(),
        help="Search and select medical conditions from the dropdown.",
        key="condition_select_tab3"
    )
 
    selected_insurance_providers = st.multiselect(
        "Search to select one or more insurance providers:",
        medical_condition_insurance_revenue['Insurance_Provider'].unique(),
        help="Search and select insurance providers from the dropdown.",
        key="insurance_provider_select_tab3"
    )
   
    filtered_condition_insurance_revenue = medical_condition_insurance_revenue
    if selected_conditions:
        filtered_condition_insurance_revenue = filtered_condition_insurance_revenue[filtered_condition_insurance_revenue['Medical_Condition'].isin(selected_conditions)]
    if selected_insurance_providers:
        filtered_condition_insurance_revenue = filtered_condition_insurance_revenue[filtered_condition_insurance_revenue['Insurance_Provider'].isin(selected_insurance_providers)]
    
    # Show DF
    #st.write(medical_condition_insurance_revenue)
    st.write(filtered_condition_insurance_revenue.round(0))


    fig, ax = plt.subplots(figsize=(12, 8))
    pivot_table = filtered_condition_insurance_revenue.pivot(
        index='Medical_Condition',
        columns='Insurance_Provider',
        values='Revenue'
    )
    sns.heatmap(pivot_table, cmap="YlGnBu", annot=True, fmt=".0f", ax=ax)
    st.pyplot(fig)

connect.close()  
