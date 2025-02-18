import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(layout="wide", page_title="Admissions Dashboard")

# Caching query results to avoid constant reloading and help execute SQL queries
@st.cache_data
def execute_query(query, params=None):
    with sqlite3.connect('healthcare_database.db') as conn:
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        return pd.DataFrame(results, columns=columns)

# Sidebar for adjusting rows because the data was taking forever to run with all the data I had
st.sidebar.title("Admissions Dashboard Settings")
limit = st.sidebar.slider("Number of rows to display:", 10, 1000, 100, 10)
st.sidebar.info("Adjust the settings to filter and optimize your view.")

# explanation for the row limit
st.sidebar.markdown("""
**Why Limit the Rows?**  
To ensure the dashboard performs efficiently and provides a smooth user experience, we have set a limit on the number of rows displayed. This approach minimizes load times and enhances interactivity, especially when analyzing large datasets.
""")

# Dashboard Title
st.header(" Admissions and Admission Logistics")

# Tabs
tab1, tab2, tab3 = st.tabs([
    "Admissions Overview",
    "Average Stay Insights",
    "Room Usage Analytics"
])

# Tab 1: Admissions Distribution
with tab1:
    st.subheader("Admissions by Hospital and Medical Condition")

    # Add tab description
    st.markdown("""
    This tab provides a detailed look into the distribution of patient admissions across hospitals and medical conditions. 
    Use the filters to explore specific hospitals or medical conditions of interest. The interactive table and bar chart 
    will help you identify which hospitals handle the highest volume of patients and the most common medical conditions treated.
    """)

    # Text input for manual filtering to let users focus on specific hospitals or conditions
    typed_hospital = st.text_input(
        "Enter Hospital Name:",
        placeholder="Type a hospital name (e.g., Smith LLC)"
    )

    typed_condition = st.text_input(
        "Enter Medical Condition:",
        placeholder="Type a medical condition (e.g.,  Cancer)"
    )

    # Build WHERE clause based on user input
    where_clauses = []
    params = []

    if typed_hospital:
        where_clauses.append("Hospital LIKE ?")
        params.append(f"%{typed_hospital}%")  

    if typed_condition:
        where_clauses.append("Medical_Condition LIKE ?")
        params.append(f"%{typed_condition}%")  

    where_clause = " AND ".join(where_clauses)
    if where_clause:
        where_clause = f"WHERE {where_clause}"

    # SQL Query1
    query1 = f"""
    SELECT 
        Hospital, 
        Medical_Condition, 
        COUNT(*) AS Admissions
    FROM 
        Healthcare_Dataset
    {where_clause}
    GROUP BY 
        Hospital, Medical_Condition
    ORDER BY 
        Admissions DESC
    LIMIT 100;
    """

    # Execute the query
    data = execute_query(query1, params)

    # Display results and visuals
    if not data.empty:
        st.dataframe(data, use_container_width=True)
        fig = px.bar(data, x="Hospital", y="Admissions", color="Medical_Condition",
                     title="Admissions by Hospital and Medical Condition")
        st.plotly_chart(fig)
    else:
        st.warning("No data available for the entered criteria.")

# Tab 2: Average Stay Insights
with tab2:
    st.subheader("Insights on Average Length of Stay")

 # Add tab description
    st.markdown("""
    This tab explores the average duration of patient stays at hospitals, categorized by admission type and hospital. 
    Use the filters to select specific admission types and hospitals, and dynamically update the results. The table and 
    bar chart will provide insights into which hospitals and admission types have the longest stays, offering a deeper understanding of hospital efficiency and patient care trends.
    """)

    # Filters Layout
    col1, col2 = st.columns(2)

    # # Get the available options for admission types and hospitals
    admission_types_query = "SELECT DISTINCT Admission_Type FROM Healthcare_Dataset;"
    admission_types = execute_query(admission_types_query)
    admission_type_options = admission_types["Admission_Type"].tolist() if not admission_types.empty else []

    hospital_list_query = "SELECT DISTINCT Hospital FROM Healthcare_Dataset;"
    hospitals = execute_query(hospital_list_query)
    hospital_options = hospitals["Hospital"].tolist() if not hospitals.empty else []

    # Filter Widgets
    with col1:
        selected_admission_types = st.multiselect(
            "Select Admission Types:",
            options=admission_type_options,
            default=None,
            help="Filter results by admission types (e.g., Emergency, Elective)."
        )
    with col2:
        selected_hospital = st.selectbox(
            "Select a Hospital:",
            options=["All"] + hospital_options,
            help="Filter results by a specific hospital or view all."
        )

    # build query based on inputs
    where_clauses = []
    params = []

    if selected_admission_types:
        placeholders = ', '.join(['?'] * len(selected_admission_types))
        where_clauses.append(f"Admission_Type IN ({placeholders})")
        params.extend(selected_admission_types)

    if selected_hospital != "All":
        where_clauses.append("Hospital = ?")
        params.append(selected_hospital)

    where_clause = ' AND '.join(where_clauses)
    if where_clause:
        where_clause = f"WHERE {where_clause}"

    query2 = f"""
    SELECT 
        Admission_Type, 
        Hospital, 
        AVG(Total_Days_of_Stay) AS Avg_Stay
    FROM 
        Healthcare_Dataset
    {where_clause}
    GROUP BY 
        Hospital, Admission_Type
    ORDER BY 
        Avg_Stay DESC
    LIMIT ?;
    """
    params.append(limit)
    data = execute_query(query2, params)

    # Longest Overall Stay
    longest_stay_query = """
    SELECT 
        Hospital, 
        Admission_Type, 
        AVG(Total_Days_of_Stay) AS Avg_Stay
    FROM 
        Healthcare_Dataset
    GROUP BY 
        Hospital, Admission_Type
    ORDER BY 
        Avg_Stay DESC
    LIMIT 1;
    """
    longest_stay_data = execute_query(longest_stay_query)

    # Show Metrics and Insights
    if not data.empty:
        # Overall longest stay
        overall_longest_hospital = longest_stay_data.loc[0, "Hospital"]
        overall_longest_type = longest_stay_data.loc[0, "Admission_Type"]
        overall_longest_stay = round(longest_stay_data.loc[0, "Avg_Stay"], 2)

        # overall longest stay
        st.metric("Longest Average Stay (Days)", f"{overall_longest_stay} days")
        st.markdown(f"**Overall Insight:** The longest average stay is at **{overall_longest_hospital}** for **{overall_longest_type}** admissions.")

        # Show filtered stay based on user selection
        if selected_hospital != "All":
            if not data[data["Hospital"] == selected_hospital].empty:
                filtered_longest_stay = data[data["Hospital"] == selected_hospital]["Avg_Stay"].max()
                st.markdown(f"**Filtered Insight:** The longest average stay at **{selected_hospital}** is **{round(filtered_longest_stay, 2)} days**.")
            else:
                st.markdown(f"No data available for **{selected_hospital}**.")

        # Collapsible Data Table
        with st.expander("View Average Stay Data Table"):
            st.dataframe(data, use_container_width=True)

        # Bar Chart
        fig = px.bar(
            data,
            x="Hospital",
            y="Avg_Stay",
            color="Admission_Type",
            title="Average Length of Stay by Admission Type",
            labels={"Avg_Stay": "Average Stay (Days)", "Hospital": "Hospital", "Admission_Type": "Admission Type"}
        )
        st.plotly_chart(fig)

    else:
        st.warning("No data available for the selected filters.")

# Tab 3: Room Usage Analytics
with tab3:
    st.subheader("Analysis of Room Assignments")

# Add tab description
    st.markdown("""
    This tab analyzes the utilization of patient rooms, highlighting the most frequently assigned rooms and their associated admission types. 
    Use the filters to refine the results by admission types or room numbers. Explore the interactive table and charts to understand room 
    usage patterns and optimize room assignments for better operational efficiency.
    """)

    # Filters for admission type and room numbers
    st.markdown("### Filter Room Assignments")
    col1, col2 = st.columns(2)

    with col1:
        admission_type_filter = st.multiselect(
            "Select Admission Types:",
            options=execute_query("SELECT DISTINCT Admission_Type FROM Healthcare_Dataset")["Admission_Type"].tolist(),
            default=None
        )

    with col2:
        room_number_filter = st.multiselect(
            "Select Room Numbers:",
            options=execute_query("SELECT DISTINCT Room_Number FROM Healthcare_Dataset")["Room_Number"].tolist(),
            default=None
        )

    # Build WHERE clause based on filters
    where_clauses = []
    params = []

    if admission_type_filter:
        placeholders = ', '.join(['?'] * len(admission_type_filter))
        where_clauses.append(f"Admission_Type IN ({placeholders})")
        params.extend(admission_type_filter)

    if room_number_filter:
        placeholders = ', '.join(['?'] * len(room_number_filter))
        where_clauses.append(f"Room_Number IN ({placeholders})")
        params.extend(room_number_filter)

    where_clause = " AND ".join(where_clauses)
    if where_clause:
        where_clause = f"WHERE {where_clause}"

    # SQL Query3
    query3 = f"""
    SELECT 
        Room_Number, 
        Admission_Type, 
        COUNT(*) AS Room_Usage
    FROM 
        Healthcare_Dataset
    {where_clause}
    GROUP BY 
        Room_Number, Admission_Type
    ORDER BY 
        Room_Usage DESC
    LIMIT ?;
    """
    params.append(limit)

    # Execute query
    data = execute_query(query3, params)

    if not data.empty:
        # Summary
        st.markdown("### Key Insights")
        total_usage = data["Room_Usage"].sum()
        most_used_room = data.loc[data["Room_Usage"].idxmax(), "Room_Number"]
        most_used_type = data.loc[data["Room_Usage"].idxmax(), "Admission_Type"]

        st.metric("Total Room Usage", total_usage)
        st.markdown(f"**Most Frequently Used Room:** {most_used_room}, primarily for **{most_used_type}** admissions.")

        # Data table
        with st.expander("View Detailed Room Usage Table"):
            st.dataframe(data, use_container_width=True)

        # Pie chart for room usage
        fig_pie = px.pie(
            data,
            values="Room_Usage",
            names="Room_Number",
            title="Room Usage Distribution",
            hover_data=["Admission_Type"],
            labels={"Room_Usage": "Usage Count", "Room_Number": "Room"}
        )
        st.plotly_chart(fig_pie)

        # Stacked bar chart for room usage by admission type
        fig_bar = px.bar(
            data,
            x="Room_Number",
            y="Room_Usage",
            color="Admission_Type",
            title="Room Usage by Admission Type",
            labels={"Room_Usage": "Usage Count", "Room_Number": "Room"},
            barmode="stack"
        )
        st.plotly_chart(fig_bar)
    else:
        st.warning("No data available for the selected filters.")