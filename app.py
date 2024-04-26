"""This is to test the Weather API, so far"""


import streamlit as st
import pandas as pd 
from datetime import datetime, timedelta
import requests
import re
import matplotlib.pyplot as plt


#This is the function for the Timer
def calculate_countdown(target_date):
    # Get the current datetime
    now = datetime.now()
    
    # Calculate the difference between the target date and now
    countdown = target_date - now
    
    # Extract the months, days, and hours from the countdown
    months = countdown.days // 30
    days = countdown.days % 30
    hours = countdown.seconds // 3600
    
    # Return a formatted string
    return f"{months} months, {days} days, {hours} hours"

#This is the Function to make links into Buttons on the Entry Page -> Streamlit doesn't allow direct hyperlinks thats why we had to do this
def create_button(link, text):
    button_style = """
    <a href="{}" target="_blank">
        <button style='
            color: white;
            background-color: #008CBA;
            padding: 10px 20px;
            text-align: center;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            cursor: pointer;
            border: none;
            border-radius: 4px;
        '>{}</button>
    </a>""".format(link, text)
    return button_style


#This is our Google API Key 
API_KEY = 'AIzaSyCYSlwK_6UxkKN1cavKJh-HvEFj_M01jy4'


#This is the Function to generate the Map of the API
def generate_map_html(latitude, longitude, api_key):
    # Our iframe code with placeholders for the API key, latitude, and longitude
    return f"""
    <iframe
        width="600"
        height="450"
        frameborder="0" style="border:0"
        src="https://www.google.com/maps/embed/v1/place?key={api_key}&q={latitude},{longitude}" allowfullscreen>
    </iframe>
    """


#This is our Open Weather API Key
API_KEY_weather = '1ae65478e4405591bd86c93b6526fc4e'

#This is the function to call the API and receive the weather information back 
def get_weather_data(latitude, longitude, API_KEY_weather):
    base_url = f"http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={API_KEY_weather}&units=metric"
    response = requests.get(base_url)
    return response.json() 



@st.cache_data  
def load_data():
    data = pd.read_csv('final.csv', delimiter=';')
    
    # Clean the rest of the columns as before
    columns_to_clean = ['Continent', 'Country', 'Degree Level', 'Exchange Program']
    for column in columns_to_clean:
        data[column] = data[column].fillna('Unknown').astype(str)
    
    return data

def get_unique_list_from_slashed_column(data, column_name):
    # Split the entries on '/' and create a flat list of all programs
    all_entries = data[column_name].dropna().str.split('/')
    unique_entries = set(entry.strip() for sublist in all_entries for entry in sublist)
    return list(unique_entries)


# We now load our data into a variable
data = load_data()

# We now load our data into a variable
university_data = load_data()


unique_degree_levels = get_unique_list_from_slashed_column(data, 'Degree Level')
unique_exchange_programs = get_unique_list_from_slashed_column(data, 'Exchange Program')


# Count the occurrences of each type of exchange program
exchange_counts = data['Exchange Program'].value_counts()
# Filter out only 'Partner University' and 'Freemover'
partner_university_count = exchange_counts.filter(like='Partner University').sum()
freemover_count = exchange_counts.filter(like='Freemover').sum()

# Prepare a DataFrame for the bar chart
bar_chart_data = pd.DataFrame({
    'Exchange Type': ['Partner University', 'Freemover'],
    'Count': [partner_university_count, freemover_count]
})


fig, ax = plt.subplots()

# Plot the bar chart
bars = ax.bar(bar_chart_data['Exchange Type'], bar_chart_data['Count'], color=['#1f77b4', '#ff7f0e'])

# Customize the chart
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.tick_params(bottom=False, left=False)  # Remove the ticks
plt.xticks(rotation=45)  # Rotate the x labels if needed
plt.ylabel('Number of Universities')
plt.title('Number of Universities available')

# Add a light grid
plt.grid(axis='y', color='gray', linestyle='--', linewidth=0.5, alpha=0.5)

# Make the bars stand out by adding the count above them
for bar in bars:
    height = bar.get_height()
    ax.annotate('{}'.format(height),
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),  # 3 points vertical offset
                textcoords="offset points",
                ha='center', va='bottom')



# We now Initialize the session state for selected_university, int the case that it doesn't exist
if 'selected_university' not in st.session_state:
    st.session_state.selected_university = None


def filter_data(data, continent_filter, country_filter, academic_level_filter, exchange_type_filter):
    if search_query:
        data = data[data['Name of University'].str.contains(search_query, case=False, na=False)]

    if continent_filter != 'All':
        data = data[data['Continent'] == continent_filter]

    if country_filter != 'All':
        data = data[data['Country'] == country_filter]

    # Ensure academic_level_filter is a string by joining the list with '|', which stands for "or" in regex
    if academic_level_filter != 'All':
        academic_level_filter_regex = '|'.join(academic_level_filter)
        data = data[data['Degree Level'].str.contains(academic_level_filter_regex, case=False, na=False, regex=True)]

    # Ensure exchange_type_filter is a string by joining the list with '|'
    if exchange_type_filter != 'All':
        exchange_type_filter_regex = '|'.join(exchange_type_filter)
        data = data[data['Exchange Program'].str.contains(exchange_type_filter_regex, case=False, na=False, regex=True)]

    return data


# With the filter function we now also set up our Sidebars
with st.sidebar:
    # Filter options
    continent_filter = st.sidebar.selectbox(
        'Select Continent', 
        ['All'] + sorted(data['Continent'].unique())
    )
    
    country_filter = st.sidebar.selectbox(
        'Select Country', 
        ['All'] + sorted(data['Country'].unique())
    )

    academic_level_filter = st.sidebar.multiselect(
        'Select Degree Level', 
        ['All'] + sorted(unique_degree_levels)
    )

    exchange_type_filter = st.sidebar.multiselect(
        'Select Exchange Program', 
        ['All'] + sorted(unique_exchange_programs)
    )
    
    search_query = st.text_input("Search for a university")
    
    filtered_data = filter_data(data, continent_filter, country_filter, academic_level_filter, exchange_type_filter)

    for index, university in filtered_data.iterrows():

        unique_key = f'uni_button_{index}_{university["Degree Level"]}_{university["Term Dates"]}'
        if st.button(university['Name of University'], key=unique_key):
            st.session_state.selected_university = university.to_dict()


# Now we go to the Main Layout of the Pop-Up, meaning the center page that appears when you click on a university on the sidebar


# This is our Main Function for the Pop-Up Window


#We define a Function to clear the page 
def clear_session():
    for key in st.session_state.keys():
        del st.session_state[key]

def display_university_details(university):

    #Main Title for each Pop-Up
    st.title(f"{university['Name of University']} Details")

    for _ in range(2):  # This is the Method we use to create blank space -> We will repeated it many times, just to make the page more structured
        st.write("")
    

    #First Subtitle -> Below this we will show the basic information for each Uni and 
    st.markdown("## 1) Useful Information")

    for _ in range(1):  # This is the Method we use to create blank space -> We will repeated it many times, just to make the page more structured
        st.write("")

    # Display university details
    st.write(f"Country: {university['Country']}")
    st.write(f"Continent: {university['Continent']}")
    st.write(f"Degree Level: {university['Degree Level']}")
    st.write(f"Exchange Program: {university['Exchange Program']}")
    
    # Provide a link to the university's website and the testimonials
    st.markdown(f"[University Homepage]({university['University URL']})")
    st.markdown(f"[Student Testimonials]({university['Testimonials']})")



    #Second Subtitle -> Now we Display the information we received with the Google Maps API for the selected University
    st.markdown("## 2) Location")

    if pd.notnull(university['Latitude']) and pd.notnull(university['Longitude']):

        map_html = generate_map_html(university['Latitude'], university['Longitude'], API_KEY)
        
        # Use the map_html in the Streamlit component to display the map
        st.components.v1.html(map_html, width=700, height=500)



    #Third Subtitle -> Now we Display the information we received with the Open Weather API for the selected University 
    st.markdown("## 3) Weather Information")

    if pd.notnull(university['Latitude']) and pd.notnull(university['Longitude']):

        weather_data = get_weather_data(university['Latitude'], university['Longitude'], API_KEY_weather)

        temperature = weather_data['main']['temp']
        temperature_max = weather_data['main']['temp_max']  # Changed 'temp' to 'temp_max'
        temperature_min = weather_data['main']['temp_min']  # Changed 'temp' to 'temp_min'
        description = weather_data['weather'][0]['description']
        
        # You can use a modal or just display the information on the page
        st.write(f"Weather for {university['Name of University']}: {temperature}°C, Temperature Max. {temperature_max}, Temperature Min. {temperature_min}, {description}")



    #Fourth Subtitle -> Here we Display the additional information (Structure, App. Places Available and Requirements) that can be accesed individually with expanders
    st.markdown("## 4) Additional Information")

    # We use st.expander to show or hide information if you click on it 
    with st.expander("Structure"):
        st.write(university['Term Dates'])

    with st.expander("Approximate Places Available"):
        st.write(university['Approximate Places Available'])

    with st.expander("Requirements"):
        st.write(university['Requirements'])
        

#We add after all this a mechanism to clear the main page for the new content 

if st.session_state.selected_university:
    # This will clear the main page for the new content
    st.empty()
    display_university_details(st.session_state.selected_university)
    
elif st.session_state.selected_university is None:
    # This is where we display the welcome message if no university has been selected yet
    st.title('_Welcome_ _to_ _Uni:green[Swap]_ !')


    for _ in range(2):  # Adjust the range for more or less space
        st.write("")

    st.markdown("## 1) Important Deadlines")

    partner_university_start_date = datetime(2024, 11, 21, 0, 0)  
    freemover_start_date = datetime(2024, 7, 1, 0, 0) 

    # Create additional space
    for _ in range(1):  # Adjust the range for more or less space
        st.write("")

    st.write("Start of registration for a partner university exchange in autumn 2025 or spring 2026")
    
    for _ in range(1):  # Adjust the range for more or less space
        st.write("")

    countdown_1 = calculate_countdown(partner_university_start_date)
    st.markdown(f'<div style="font-size: large; color: red; border: 2px solid; padding: 10px; display: inline-block;">{countdown_1}</div>', unsafe_allow_html=True)

    for _ in range(2):  # Adjust the range for more or less space
        st.write("")

    st.write("Start of the registration for Freemover exchange for spring 2025")

    for _ in range(1):  # Adjust the range for more or less space
        st.write("")

    countdown_2 = countdown_2 = calculate_countdown(freemover_start_date)
    st.markdown(f'<div style="font-size: large; color: red; border: 2px solid; padding: 10px; display: inline-block;">{countdown_2}</div>', unsafe_allow_html=True)
    
    for _ in range(2):  # Adjust the range for more or less space
        st.write("")

    # Underlined subtitle

    st.markdown("## 2) Important Information")

    for _ in range(1):  # Adjust the range for more or less space
        st.write("")

    #Bachelor Level Information
    with st.expander("Exchange at Bachelor Level"):
    # Links styled as buttons for Bachelor level (streamlit doesn't allow direct hyperlinks so we had to do it like this, C)
        st.markdown(create_button("https://universitaetstgallen.sharepoint.com/sites/AustauschDE/SitePages/START_BA_Partneruniversität.aspx", "Bachelor partner universities"), unsafe_allow_html=True)
        st.markdown(create_button("https://universitaetstgallen.sharepoint.com/sites/AustauschDE/SitePages/START_BA_Freemover.aspx", "Bachelor Freemover"), unsafe_allow_html=True)
        st.markdown(create_button("https://universitaetstgallen.sharepoint.com/sites/AustauschDE/SitePages/START_BA_SwissMobility.aspx", "Bachelor Swiss Mobility"), unsafe_allow_html=True)
        st.markdown(create_button("https://universitaetstgallen.sharepoint.com/sites/AustauschDE/SitePages/en/HSG-Asia-Term.aspx", "HSG Asia Term"), unsafe_allow_html=True)
        st.markdown(create_button("https://universitaetstgallen.sharepoint.com/sites/AustauschDE/SitePages/en/HSG.aspx", "HSG Latam Term"), unsafe_allow_html=True)
        st.markdown(create_button("https://universitaetstgallen.sharepoint.com/sites/AustauschDE/SitePages/en/ECOL-Virtual-Courses.aspx", "HSG ECOL Virtual Courses"), unsafe_allow_html=True)
        
    for _ in range(2):  # Adjust the range for more or less space
        st.write("")

    # Master Level Information
    with st.expander("Exchange at Master Level"):
    # Links styled as buttons for Master level (streamlit doesn't allow direct hyperlinks so we had to do it like this)
        st.markdown(create_button("https://universitaetstgallen.sharepoint.com/sites/AustauschDE/SitePages/START_MA_Partneruniversität.aspx", "Master partner universities"), unsafe_allow_html=True)
        st.markdown(create_button("https://universitaetstgallen.sharepoint.com/sites/AustauschDE/SitePages/START_MA_Freemover.aspx", "Master Freemover"), unsafe_allow_html=True)
        st.markdown(create_button("https://universitaetstgallen.sharepoint.com/sites/AustauschDE/SitePages/START_MA_SwissMobility.aspx", "Master Swiss Mobility"), unsafe_allow_html=True)
        st.markdown(create_button("https://universitaetstgallen.sharepoint.com/sites/AustauschDE/SitePages/en/Master-THEMIS.aspx", "Master THEMIS"), unsafe_allow_html=True)
    
    for _ in range(2):  # Adjust the range for more or less space
        st.write("")

    st.markdown("## 3) Number of Universities available")

    for _ in range(2):  # Adjust the range for more or less space
        st.write("")

    st.pyplot(fig)

# Add a button to clear the session state, which will effectively "reset" the app
if st.button('Clear Page'):
    clear_session()
    st.experimental_rerun()


