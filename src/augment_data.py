from src import augment_utils, weather_helper, location_helper


# Read and augment the data from the database
def augment_data(db):
    # Raw incident structure: [incident_time, incident_number, incident_location, incident_nature, incident_ori]
    # Augmented data row: [Day of the Week, Time of Day, Weather, Location Rank, Side of Town, Incident Rank, Nature, EMSSTAT]
    augmented_data = []
    incidents = db.execute("SELECT * FROM incidents").fetchall()

    # Create and populate the location_ranks dictionary
    location_ranks = augment_utils.get_location_ranks(db)

    # Create and populate the incident_ranks dictionary
    incident_ranks = augment_utils.get_incident_ranks(db)

    # Augment the data
    for row_num, incident in enumerate(incidents):
        output_row = []

        # Get the day of the week the incident occurred
        output_row.append(augment_utils.get_day(incident[0].split()[0]))

        # Get the time of day the incident occurred
        output_row.append(augment_utils.get_time(incident[0].split()[1]))

        # Get the weather at the time and location of the incident
        output_row.append(weather_helper.get_weather(incident[0], incident[2]))

        # Get the incident_location rank
        output_row.append(location_ranks[incident[2]])

        # Get the side of town using the incident_location
        output_row.append(location_helper.get_side_of_town(incident[2]))

        # Get the incident_nature rank
        output_row.append(incident_ranks[incident[3]])

        # Get the nature of the incident
        output_row.append(incident[3])

        # Get the EMSSTAT value
        output_row.append(augment_utils.get_emsstat(row_num, incident[4], incidents))

        # Append the augmented data row to the list
        augmented_data.append(output_row)

    return augmented_data