"""Test if the csv works, as well as the Search Bar und Filter!"""

import streamlit as st
import pandas as pd  

@st.cache_data  # Updated caching decorator
def load_data():
    return pd.read_csv('test3.csv', delimiter=';')

# Load your data into a variable
data = load_data()

# Load your data into a variable
university_data = load_data()

#Create the Sidebar filters 

# If the actual name in the CSV has a different case or extra spaces, use the exact name.
continent_filter = st.sidebar.selectbox('Select Continent', ['All'] + sorted(data['Continent'].unique()))  # Note the space after 'Continent'
country_filter = st.sidebar.selectbox('Select Country', ['All'] + sorted(data['Country'].unique()))
academic_level_filter = st.sidebar.selectbox('Select Level for Exchange', ['All', 'Bachelor', 'Master'])
exchange_type_filter = st.sidebar.selectbox('Select Exchange Program', ['All', 'Partner University', 'Freemover'])


#Create Search bar
search_query = st.text_input('Search for a university')

# Create Function to filter data based on selections
def filter_data(data):
    if continent_filter != 'All':
        data = data[data['Continent'] == continent_filter]
    if country_filter != 'All':
        data = data[data['Country'] == country_filter]
    
    if academic_level_filter != 'All':
        # Adjusted to include rows that have either the specific level or 'Bachelor/Master'
        data = data[(data['Level for Exchange'] == academic_level_filter) | (data['Level for Exchange'] == 'Bachelor/Master')]
    
    if exchange_type_filter != 'All':
        data = data[data['Exchange Program'] == exchange_type_filter]

    if search_query:
        data = data[data['Name of University'].str.contains(search_query, case=False)]
    return data

# Now when you call the filter_data function, pass 'data' as the argument
filtered_data = filter_data(data)


# Display the filtered data
def display_universities(dataframe):
    for index, row in dataframe.iterrows():
        # I only did it now for three things: Name, Country and Continent 
        with st.container():
            st.write(f"### {row['Name of University']}")
            st.write(f"Country: {row['Country']}")
            st.write(f"Continent: {row['Continent']}")
            # We add more later

# Call the display function with the filtered data
display_universities(filtered_data)


