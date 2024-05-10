
"""  Streamlit Web Application of Group 12.2   """

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#  Welcome to UniSwap ! 
#
#  Planning an exchange semester can be overwhelming and complex for students, as it demands a lot of time 
#  for Research and Organization, which many students don't have because amidst their already packed schedules 
#  and academic responsibilities.
#
#  This is where UniSwap comes in. UniSwap is the first overall University Exchange Information Portal that is 
#  designed to assist students in finding and organizing their exchange semester abroad. Its goal is to provide students
#  with all the information they need at their fingertips.
#
#  UniSwap provides a lot of interesting features that can help students: 
#
#  Features:
#  - Visualization of important deadlines and direct links to all the important StudentWeb pages 
#  - Dynamic and comprehensive searching and filtering options to browse for universities
#  - Detailed university profiles that including link to university website and testimonials, as well as additional information
#  - Interactive maps to visualize university locations.
#  - Integration of APIs for weather data.
#
#  The application is built using Streamlit, making it interactive and easy to navigate. To use streamlit, we had to learn about the 
#  streamlit documentation. We won't reference everytime we used the streamlit documentation in our code, due to the fact that we would
#  need to reference it for almost all the code you use. For this reason we will reference it now here: https://docs.streamlit.io
#  
#
#  Thank you for visiting our application and Enjoy your exploration!
#
#  - Developed by  [Group 12.2]
#  - Last updated: [14th of May 2024]
#  
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #






#  1.) We start our source code, with all the important imports we need:

import streamlit as st                          # | We import the streamlit library to our Python environment under the alias st
import pandas as pd                             # | We import the pandas library to our Python environment under the alias pd
from datetime import datetime, timedelta        # | We import the datetime and timedelta classes directly from the datetime module  -> https://docs.python.org/3/library/datetime.html
import requests                                 # | We import the requests library into our Python environment
import re                                       # | We import the re module (regular expression module) -> Chat GPT helped us here 


#  2.) We now define all small functions that run in the Backend of our application and that we later call in our main function


# a) This is the function for the Timer that we need for our Deadlines
# -> For this function we had help from various Websites: (https://docs.python.org/3/library/datetime.html, https://realpython.com/python-datetime, https://www.geeksforgeeks.org/python-datetime-module)
#    They helped us learn more about the datime library 
def calculate_countdown(target_date):
   
    now = datetime.now()                                   #| We get the current datetime 
    countdown = target_date - now                          #| We Calculate the difference between the target date and now
    
    months = countdown.days // 30                          #| We extract the months, days, and hours from the countdown
    days = countdown.days % 30
    hours = countdown.seconds // 3600
    
    return f"{months} months, {days} days, {hours} hours"  #| # We return a formatted string, that shows how many months, days and hours remain until Deadline 



# b) This is a Function that generates HTML code for a styled button that acts as a hyperlink.
#    Streamlit abstracts much of the HTML/CSS away to simplify the process of turning data scripts into web apps. 
#    It has widgets for many common tasks but lacks the task for a hyperlink button, which is why we had to
#    create this function that does this. 
#
# -> For this function we had the help of ChatGPT, because we didn't know much about HTML code, especially not how to
#    use it to create a styled button that acts as a hyperlink.   

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



# c) This is our function that "visualizes" some of our Data.
#    We use our longitude and latitude data that we saved for every university in our csv to create a Google Maps Widget that shows the location of each university
#    We searched really hard and couldn't find any other way to display a Map directly into our streamlit application, which is why we used this method
#    -> However because we didn't learn about HTML code language yet we had the help of ChatGPT

#    This is our API Key for the Google Maps API we need for this Widget
API_KEY = 'AIzaSyCYSlwK_6UxkKN1cavKJh-HvEFj_M01jy4'            

def generate_map_html(latitude, longitude, api_key):
#| Our iframe code with placeholders for the API key, latitude, and longitude (The latitude and longitude information is saved in our csv). It returns an HTML string that represents an iframe containing the Google Map.
    return f"""
    <iframe
        width="600"
        height="450"
        frameborder="0" style="border:0"
        src="https://www.google.com/maps/embed/v1/place?key={api_key}&q={latitude},{longitude}" allowfullscreen>
    </iframe>
    """




#  3.) Now we introduce our Weather API


#  The API we use is the OpenWeather API.
#| This is our Open Weather API Key
API_KEY_weather = '1ae65478e4405591bd86c93b6526fc4e'                                     

def get_weather_data(latitude, longitude, API_KEY_weather):                            
    base_url = f"http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={API_KEY_weather}&units=metric"  #| (longitude & latitude get extracted from our csv). -> To correctly create the URL we had help from the the offical site of the OpenWeather API 
    response = requests.get(base_url)                                                                                                 #   ->https://openweathermap.org/api
    return response.json() 




#  4.) This is our function that is designed to load and clean a dataset from our CSV file with the help of the pandas library in Python



@st.cache_data                                              #| This decorator optimizes performance by storing the function's return value and only re-executing the function when its input parameters or the function's body changes
def load_data():                                            #| Our function load_data takes no parameters and is meant to perform data loading and cleaning operations
    data = pd.read_csv('streamlit_application_data.csv', delimiter=';')          #| We load data from a CSV file named streamlit_application_data. The delimiter ; indicates that the columns in the CSV are separated by semicolons
    

#| During our coding process we encountered many times an error, due to the fact that in some columns of our csv we had missing values and that their data types weren't consistent
#| Chat GPT helped us resolve this error by creating a cleaning process that looks like this 

    columns_to_clean = ['Continent', 'Country', 'Degree Level', 'Exchange Program']  #| We specify, which columns of the csv need cleaning

    for column in columns_to_clean:                                                  #| Our function then iterates over each column listed in columns_to_clean. For each column, it replaces missing values (NaN)                           
        data[column] = data[column].fillna('Unknown').astype(str)                    #| with the string 'Unknown' using fillna('Unknown') and converts the column to string type using astype(str).
                                                                                     #| this ensures that there are no missing values in the columns and that the data type is consistent
    return data


#| We now load our data into a variable
data = load_data() 


#| We also encountered the problem that sometimes one cell in our csv contained multiple entries, which caused an error that shut down our application
#| To prevent this error, we created a function that is designed to process all columns of our csv in which some cells contained multiple entries that were
#| seperated by slashes ('/').
 
def get_unique_list_from_slashed_column(data, column_name):

    all_entries = data[column_name].dropna().str.split('/')                             #| It first drops any NaN (missing) values from this column to avoid errors during splitting then splits each string in the column based on the '/' delimiter. This results in a list of lists, where each sublist contains the split elements of a row.
                                                                                        
    unique_entries = set(entry.strip() for sublist in all_entries for entry in sublist) #| We also strips any leading or trailing whitespace from each element and convert the list into a set, which hich automatically removes any duplicate entries because sets do not allow duplicates
    return list(unique_entries)

unique_degree_levels = get_unique_list_from_slashed_column(data, 'Degree Level')             #| We extract unique entries like "Bachelor/Master/PhD"  from the 'Degree Level' column from our "data" variable.  
unique_exchange_programs = get_unique_list_from_slashed_column(data, 'Exchange Program')     #| We extract unique entries like "Partner University/Freemover"  from the 'Exchange Program' column from our "data" variable. 

#| -> For the get_unique_list_from_slashed_column Function we had help with ChatGPT, because we didn't know how to solve the problem alone. 




#  5.) We now start setting up our sidebar in our streamit application


#   a) The function filter_data is designed to create the filter our csv data based multiple criteria: university name (via a search query), continent, country, academic level, and exchange program type.
#   -> We need this for setting up our filter bars 
def filter_data(data, continent_filter, country_filter, academic_level_filter, exchange_type_filter):

   #| If search_query is provided, it filters our csv data by checking if the 'Name of University' column contains the search query string. It is case-insensitive -> For this help of ChatGPT and ignores any NaN values -> For this help of ChatGPT.
    if search_query:                              
        data = data[data['Name of University'].str.contains(search_query, case=False, na=False)]

   #| If continent_filter is specified and is not 'All', it filters data (our csv data) by matching the 'Continent' column exactly with the value provided in continent_filter
    if continent_filter != 'All':
        data = data[data['Continent'] == continent_filter]

   #| If country_filter is specified and is not 'All', it filters data (our csv data) by the 'Country' column, looking for an exact match with the value in country_filter.
    if country_filter != 'All':
        data = data[data['Country'] == country_filter]

   #| If academic_level_filter is specified and is not 'All', it first converts the list of academic levels into a regular expression string by joining the list elements with the '|' symbol, which represents "or" in regex. 
   #  It then filters the data (our csv data) by the 'Degree Level' column, checking if any of the specified academic levels are present. This also uses a case-insensitive, regex-based search that ignores NaN values.
    if academic_level_filter != 'All':
        academic_level_filter_regex = '|'.join(academic_level_filter)  #| Here we had help with ChatGPT
        data = data[data['Degree Level'].str.contains(academic_level_filter_regex, case=False, na=False, regex=True)]

   #| We do the same that we did for academic_level also for the exhange_type data 
    if exchange_type_filter != 'All':
        exchange_type_filter_regex = '|'.join(exchange_type_filter)
        data = data[data['Exchange Program'].str.contains(exchange_type_filter_regex, case=False, na=False, regex=True)]

    return data


#   b) together with the filter_data function we also set up our Sidebars
with st.sidebar:

    # Continent Filter Bar  
    continent_filter = st.sidebar.selectbox(
        'Select Continent', 
        ['All'] + sorted(data['Continent'].unique())
    )
    
    #Country Filter bar 
    country_filter = st.sidebar.selectbox(
        'Select Country', 
        ['All'] + sorted(data['Country'].unique())
    )
 
    #Degree Filter bar
    academic_level_filter = st.sidebar.multiselect(
        'Select Degree Level', 
        ['All'] + sorted(unique_degree_levels)
    )

    #Exhange Program Filter bar 
    exchange_type_filter = st.sidebar.multiselect(
        'Select Exchange Program', 
        ['All'] + sorted(unique_exchange_programs)
    )
    
    #We also create our search bar 
    search_query = st.text_input("Search for a university")
    
    #All of the filtered date should be saved under a variable we call filtered data
    filtered_data = filter_data(data, continent_filter, country_filter, academic_level_filter, exchange_type_filter)


    #We also create a button for each university that is displayed below our sidebars
    for index, university in filtered_data.iterrows():
        
        #For each university we constructs a unique key for a Streamlit button. 
        #This unique key ensures that each button has a distinct identifier in the Streamlit interface
        unique_key = f'uni_button_{index}_{university["Degree Level"]}_{university["Term Dates"]}'       #|This key is formed using the string 'uni_button_', the row index, and specific attributes of the university such as "Degree Level" and "Term Dates" -> We had help from ChatGPT for this

        #When a user clicks on a button, the application captures and stores the detailed information of the selected university
        if st.button(university['Name of University'], key=unique_key):
            st.session_state.selected_university = university.to_dict()




# Now we set up the Main Layout of the Pop-Up, meaning the center page that appears when you click on a university on the sidebar


#   a) First we Initialize the session state for selected_university, in the case that it doesn't exist
if 'selected_university' not in st.session_state:
    st.session_state.selected_university = None


#   b) We create function to clear the page
def clear_session():                              
    for key in st.session_state.keys():           #| We iterate over all the keys (university selected) currently stored in Streamlit's session state.
        del st.session_state[key]                 #  and delete each key-value pair in the session state one by one


#   c) Now this is our Main Function for the Pop-Up Window


def display_university_details(university):

    #Main Title of each Pop-Up page, based on which university button was clicked
    st.title(f"{university['Name of University']} Details")

    for _ in range(2):                                                               #| We created a loop that creates blank space in the streamlit application. If we adjust the range we can create more or less blank space.
        st.write("")                                                                 #  We will repeat this loop many times, just to make the page more structured -> ChatGPT gave us the idea for this
    


    #- First Subtitle -> Below this we will show the basic information for each Uni and 
    st.markdown("## 1) Useful Information")

    for _ in range(1):                                                               #|We already explained this loop above
        st.write("")

    # Display university details
    st.write(f"Country: {university['Country']}")                                    #| Based on the university selected, the country of this university that is saved in the csv gets displayed 
    st.write(f"Continent: {university['Continent']}")                                #| Based on the university selected, the continent of this university that is saved in the csv gets displayed 
    st.write(f"Degree Level: {university['Degree Level']}")                          #| Based on the university selected, the Degree Level of this university that is saved in the csv gets displayed 
    st.write(f"Exchange Program: {university['Exchange Program']}")                  #| Based on the university selected, the country of this university that is saved in the csv gets displayed 
    
    # Provide a link to the university's website and the testimonials
    st.markdown(f"[University Homepage]({university['University URL']})")            #| For the university selected, the link for the website of this university gets diplayed. We ectract this information from the 'University URL' column in our csv 
    st.markdown(f"[Student Testimonials]({university['Testimonials']})")             #| For the university selected, the link for the website with the student testimonials for this university gets diplayed. We extract this information from the 'Testimonials' column in our csv  



    #- Second Subtitle -> Now we Display the Map Widget for the selected University
    st.markdown("## 2) Location")

    if pd.notnull(university['Latitude']) and pd.notnull(university['Longitude']):                   #| If the latitude and longitude columns for this university in the csv are not null:
        map_html = generate_map_html(university['Latitude'], university['Longitude'], API_KEY)       #  we call the generate_map_html funtion from 2.) to generate the map widget, based on the data for this uni that is saved in the two columns 'latitude' and 'longitude' in the csv 
        
        # We use the map_html in the Streamlit component to display the map -> Help of ChatGPT
        st.components.v1.html(map_html, width=700, height=500)                                       #  this function is used to to render the HTML content generated by generate_map_html directly in the Streamlit app. We also specify the dimensions of the iframe with the width and height parameters.

    

    #- Third Subtitle -> Now we Display the information we received with the Open Weather API for the selected University
    st.markdown("## 3) Weather Information")

    if pd.notnull(university['Latitude']) and pd.notnull(university['Longitude']):                             #| If the latitude and longitude columns for this university in the csv are not null:

        weather_data = get_weather_data(university['Latitude'], university['Longitude'], API_KEY_weather)      #  We call the get_weather_data from 2.) based on the latitude and longitude information in the csv

        temperature = weather_data['main']['temp']                #| We assign the temperature information we received from the API to a new variable
        temperature_max = weather_data['main']['temp_max']        #| We assign the max temperature information we received from the API to a new variable
        temperature_min = weather_data['main']['temp_min']        #| We assign the min temperature information we received from the API to a new variable
        description = weather_data['weather'][0]['description']   #| We assign the weather description temperature information we received from the API to a new variable
        
        # All the information we want to display in one line 
        st.write(f"Weather for {university['Name of University']}: {temperature}°C, Temperature Max. {temperature_max}, Temperature Min. {temperature_min}, {description}")



    #- Fourth Subtitle -> Here we Display the additional information (Structure, App. Places Available and Requirements) that can be accesed individually with expanders
    st.markdown("## 4) Additional Information")

    # We use st.expander to show or hide information if you click on it 
    with st.expander("Structure"):
        st.write(university['Term Dates'])                        #| The Term Dates information for each university column in the csv 

    with st.expander("Approximate Places Available"):             
        st.write(university['Approximate Places Available'])      #| The Approximate Places information for each university column in the csv

    with st.expander("Requirements"):
        st.write(university['Requirements'])                      #| The additional Requirement information for each university column in the csv


if st.session_state.selected_university:
    # This will clear the main page for the new content
    st.empty()
    display_university_details(st.session_state.selected_university)



#   d) Now we set up up the front page that is displayed when no university is selected 


elif st.session_state.selected_university is None:

    #- We display the title with black and green colors
    st.title('_Welcome_ _to_ _Uni:green[Swap]_ !')                                 #| To find out how to change color, we had help from the website: https://docs.streamlit.io/develop/api-reference/text/st.markdown#

    for _ in range(2):                                                             #| We created a loop that creates blank space in the streamlit application. If we adjust the range we can create more or less blank space
        st.write("")                                                               #| -> ChatGPT gave us the idea for this loop


    #- We diplay our first subtitle 
    st.markdown("## 1) Important Deadlines")

    for _ in range(1):                                                             #| We already explained this loop above 
        st.write("")

    partner_university_start_date = datetime(2024, 11, 21, 0, 0)                   #| We create a datetime object for the first deadline (Start of registration for partner univeristies)
    freemover_start_date = datetime(2024, 7, 1, 0, 0)                              #| We create a second datetime object for the second important Deadline (Start of registration for Freemover universities)

    #- We Display a text for our first Timer
    st.write("Start of registration for a partner university exchange in autumn 2025 or spring 2026")
    
    for _ in range(1):                                                             #| We already explained this loop above
        st.write("")
    
    countdown_1 = calculate_countdown(partner_university_start_date)               #| We call our calculate_countdown function from 2.) to create a countdown based on our partner_university_start_date datetime object. The timer will show how many months, days, hours are left until the deadline is met
    
    #- We Dispay the Timer as a large red block
    st.markdown(f'<div style="font-size: large; color: red; border: 2px solid; padding: 10px; display: inline-block;">{countdown_1}</div>', unsafe_allow_html=True)  #|-> To create this block we had help from ChatGPT


    for _ in range(2):                                                             #| We already explained this loop above
        st.write("")

    #- We Display the text for our second Timer
    st.write("Start of the registration for Freemover exchange for spring 2025")

    for _ in range(1):                                                             #| We already explained this loop above 
        st.write("")

    countdown_2 = countdown_2 = calculate_countdown(freemover_start_date)          #| We call our calculate_countdown function from 2.) to create, based on our freemover_start_date datetime object, a timer. The timer will show how many months, days, hours are left until the deadline is met

    #- We Dispay the Countdown as a large red block
    st.markdown(f'<div style="font-size: large; color: red; border: 2px solid; padding: 10px; display: inline-block;">{countdown_2}</div>', unsafe_allow_html=True)  #|-> We created the box the same way as the first 
    
    for _ in range(2):                                                             #| We already explained this loop above 
        st.write("")


    #- We display a second Subtitle 
    st.markdown("## 2) Important Information")

    for _ in range(1):                                                             #| We already explained this loop above 
        st.write("")

    #- We create an expandable section the content within this block is hidden by default and can be expanded by the user
    with st.expander("Exchange at Bachelor Level"):

    #- Links leading to StudentWeb pages with important information.
    #  We now use our create_button function from 2.) because streamlit doesn't allow direct hyperlinks so we had to do it like this
    #  Each st.markdown call uses a custom create_button function to generate HTML for a button. This HTML is then rendered as part of the Streamlit page
        st.markdown(create_button("https://universitaetstgallen.sharepoint.com/sites/AustauschDE/SitePages/START_BA_Partneruniversität.aspx", "Bachelor partner universities"), unsafe_allow_html=True)
        st.markdown(create_button("https://universitaetstgallen.sharepoint.com/sites/AustauschDE/SitePages/START_BA_Freemover.aspx", "Bachelor Freemover"), unsafe_allow_html=True)
        st.markdown(create_button("https://universitaetstgallen.sharepoint.com/sites/AustauschDE/SitePages/START_BA_SwissMobility.aspx", "Bachelor Swiss Mobility"), unsafe_allow_html=True)
        st.markdown(create_button("https://universitaetstgallen.sharepoint.com/sites/AustauschDE/SitePages/en/HSG-Asia-Term.aspx", "HSG Asia Term"), unsafe_allow_html=True)
        st.markdown(create_button("https://universitaetstgallen.sharepoint.com/sites/AustauschDE/SitePages/en/HSG.aspx", "HSG Latam Term"), unsafe_allow_html=True)
        st.markdown(create_button("https://universitaetstgallen.sharepoint.com/sites/AustauschDE/SitePages/en/ECOL-Virtual-Courses.aspx", "HSG ECOL Virtual Courses"), unsafe_allow_html=True)
        
    for _ in range(2):                                                            #| We already explained this loop above 
        st.write("")

    #- We create an expandable section the content within this block is hidden by default and can be expanded by the user
    with st.expander("Exchange at Master Level"):
    
    #- Links leading to StudentWeb pages with important information.
    #  We now use our create_button function from 2.) because streamlit doesn't allow direct hyperlinks so we had to do it like this
    #  Each st.markdown call uses a custom create_button function to generate HTML for a button. This HTML is then rendered as part of the Streamlit page
        st.markdown(create_button("https://universitaetstgallen.sharepoint.com/sites/AustauschDE/SitePages/START_MA_Partneruniversität.aspx", "Master partner universities"), unsafe_allow_html=True)
        st.markdown(create_button("https://universitaetstgallen.sharepoint.com/sites/AustauschDE/SitePages/START_MA_Freemover.aspx", "Master Freemover"), unsafe_allow_html=True)
        st.markdown(create_button("https://universitaetstgallen.sharepoint.com/sites/AustauschDE/SitePages/START_MA_SwissMobility.aspx", "Master Swiss Mobility"), unsafe_allow_html=True)
        st.markdown(create_button("https://universitaetstgallen.sharepoint.com/sites/AustauschDE/SitePages/en/Master-THEMIS.aspx", "Master THEMIS"), unsafe_allow_html=True)
    
    for _ in range(2):                                                            #| We already explained this loop above 
        st.write("")
    
    #- We display a Third Subtitle 
    st.markdown("## 3) Number of Universities available")

    for _ in range(2):                                                            #| We already explained this loop above 
        st.write("")


# Add a button to clear the session state, which will effectively "reset" the app
if st.button('Clear Page'):                                       #| If the 'Clear Page' Button is pressed
    clear_session()                                               #| the clear_session function is called 
    st.experimental_rerun()                                       #| st.experimental_rerun() is called, the script is halted - no more statements will be run, and the script will be queued to re-run from the top. -> We go this info from: https://docs.streamlit.io/develop/api-reference/execution-flow/st.experimental_rerun                                  #|


