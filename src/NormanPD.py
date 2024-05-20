import streamlit as st
import pandas as pd
import datetime

from utils import extraction, augmentation


# Set the page configuration
st.set_page_config(layout="wide", page_title="Norman PD Incident Management", page_icon="🚔")
st.title('Incident Summaries in Norman, OK')

# Assign a default value to the date picker state
today = datetime.datetime.now()
min_date = datetime.date(today.year, 12, 1) if (today.month == 1) else datetime.date(today.year, today.month - 1, 1)
max_date = datetime.date(today.year, today.month, today.day) if (today.day < 3) else datetime.date(today.year, today.month, today.day - 2)

# Assign default values to the session state variables
if "incident_date_range" not in st.session_state:
    st.session_state.incident_date_range = [min_date, max_date]

if "augmented_data" not in st.session_state:
    st.session_state.augmented_data = []


# Download and extract the incident data for the a single date
@st.cache_data
def extract_pdf(date):
    # Create the url for each selected date
    ## Example URL: https://www.normanok.gov/sites/default/files/documents/YYYY-MM/YYYY-MM-DD_daily_incident_summary.pdf
    url = "https://www.normanok.gov/sites/default/files/documents/" + date.strftime("%Y-%m") + "/" + date.strftime("%Y-%m-%d") + "_daily_incident_summary.pdf"

    # Download the incident summary PDF from the url
    incident_data = extraction.fetchincidents(url)

    # Extract and return the incident data present in PDF
    return extraction.extractincidents(incident_data)


# Augment the incident data for the selected dates
@st.cache_data
def transform_data(all_dates):
    # Initialize the list to store the extracted incidents
    incidents = []

    # Iterate through each url and extract the raw incident data
    for date in all_dates:
        incidents.extend(extract_pdf(date))

    # Augment the data
    augmented_data = augmentation.augment_data(incidents)
    return augmented_data


# Write the augmented data to streamlit app
def write_data(augmented_data):
    if not augmented_data:
        st.error("Download the data to view the transformed incident summaries here:")
        return

    # Create a dataframe to store the augmented data
    augmented_df = pd.DataFrame(augmented_data, columns=["Date (YYYY-MM-DD)", "Day of the Week", "Time of Day", "Location", "Location Rank", "Incident Nature", "Incident Rank"])
    st.write(augmented_df)


def main():
    # Create a form with a date picker in the sidebar
    with st.form(key ='Form1'):
        st.success(f"Select a date range between {st.session_state.incident_date_range[0]} and {st.session_state.incident_date_range[1]} to download and view the incident data")
        selected_date_range = st.date_input(("Select a date range:"), 
                                            value=(st.session_state.incident_date_range[0], st.session_state.incident_date_range[1]), 
                                            min_value=min_date, max_value=max_date, format="MM/DD/YYYY")

        submit_button = st.form_submit_button("Download data for selected dates")

    # If the form is submitted, download the data
    resultant_data = []
    if submit_button:
        # Save the selected range into a state variable
        st.session_state.incident_date_range = selected_date_range
        st.write("You Selected: ", st.session_state.incident_date_range[0], " - ", st.session_state.incident_date_range[1])

        # Get all the dates in the selected range
        all_dates = pd.date_range(start=st.session_state.incident_date_range[0], end=st.session_state.incident_date_range[1], freq='D').to_list()

        # Download the incident data for each selected date
        resultant_data = transform_data(all_dates)
        if resultant_data:
            st.session_state.augmented_data = resultant_data

    # View the augmented data
    write_data(st.session_state.augmented_data)


if __name__ == '__main__':
    # Call the main function
    main()
