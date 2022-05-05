# Streamlit Project
# Ryan O'Connor

import streamlit as st
import pandas as pd
import datetime as dt
import numpy as np
import matplotlib.pyplot as plt


def read_crime_file():
    crime_df = pd.read_csv("BostonCrime.csv")
    crime_df['OCCURRED_ON_DATE'] = pd.to_datetime(crime_df['OCCURRED_ON_DATE']).dt.date
    crime_df = crime_df.rename(columns={"Lat": "lat", "Long": "lon"})
    return crime_df


def read_districts_file():
    return pd.read_csv("BostonDistricts.csv")


def get_district_list(district_df):
    districts = np.array(district_df['DISTRICT_NAME'])
    districts = districts.tolist()
    return districts


def get_days_list(crime_df):
    days = np.array(crime_df['DAY_OF_WEEK'].values.tolist())
    return np.unique(days)


def get_district_code(district_name, district_df):
    # filters district dataframe and finds row where the district name matched value passed in
    district_df = district_df.loc[district_df['DISTRICT_NAME'] == district_name]
    # because each district has a unique name, dataframe now has one row.  extracts only row's district number as string
    code = district_df['DISTRICT_NUMBER'].values[0]
    # returns string to analyze district function
    return code


def analyze_district(crime_df, district_df, districts):
    # empty list to append district codes to later
    codes = []
    # only runs if at least one district was selected and passed to function
    if len(districts) != 0:
        # for each district code in the list, calls get district code function (line 33). passes in
        # district and district dataframe
        for district in districts:
            code = get_district_code(district, district_df)
            # adds district number code to codes list
            codes.append(code)
        # filters crime dataframe to rows where the district number is in the codes list
        crime_df = crime_df.loc[crime_df['DISTRICT'].isin(codes)]
    # user can select to filter data further by a selected date
    date_filter_bool = st.checkbox('Filter by Date?')
    if date_filter_bool is True:
        # Streamlit date input, only available dates are the dates with data in the crime dataframe
        date_filter = st.date_input("Enter a Date", value=dt.date(2022, 1, 1),
                                    min_value=dt.date(2022, 1, 1),
                                    max_value=dt.date(2022, 4, 8))
        # filters crime dataframe to rows where the date matches the inputted date
        crime_df = crime_df.loc[crime_df['OCCURRED_ON_DATE'] == date_filter]
    # finds the length of the dataframe index to find the number of crimes
    crime_count = f"Crimes Occurred: {len(crime_df.index)}"
    st.subheader(crime_count)
    # checkbox if user wants to view the raw filtered data
    show_data = st.checkbox('Show Raw Data?')
    if show_data is True:
        # streamlit write the dataframe to page
        st.write(crime_df)
    # passes remaining data into map_crimes function which removes rows without lat/lon data and returns mappable data
    map_data = map_crimes(crime_df)
    # streamlit maps remaining data
    st.map(map_data)
    # passes relevant data into district_visualization and pie_shootings functions to make graphs for queried data
    district_visualization(crime_df, district_df, districts)
    pie_shootings(crime_df)


def district_visualization(crime_df, district_df, districts):
    st.header(f"Breakdown of {len(crime_df.index):,} crimes by chosen districts")
    districts_dict = {}
    if len(districts) == 0:
        districts = get_district_list(district_df)
    for district in districts:
        num = len(crime_df.loc[crime_df['DISTRICT'] == get_district_code(district, district_df)])
        districts_dict[district] = num
    table_data = pd.DataFrame.from_dict(districts_dict, orient='index')
    table_data = table_data.rename(columns={0: 'Number of Crimes'})
    table_data = table_data.sort_values(by=['Number of Crimes'], ascending=False)
    st.table(table_data)
    fig, ax = plt.subplots()
    plt.pie(districts_dict.values(), labels=districts_dict.keys(), autopct='%1.1f%%',
            colors=['#ff9999', '#66b3ff', '#99ff99', '#ffe5cc', '#ffff99', '#eeaaf2', '#cce5ff', '#ffcce5', '#99ff33',
                    '#99ffff', '#ffb266', '#e5ccff'])
    plt.axis('equal')
    plt.tight_layout()
    plt.title("Distribution of Crimes")
    if len(districts) >= 2:
        st.pyplot(fig)


def pie_shootings(crime_df):
    shooting_dict = {'Shooting': len(crime_df.loc[crime_df['SHOOTING'] == 1]),
                     'No Shooting': len(crime_df.loc[crime_df['SHOOTING'] == 0])}
    fig, ax = plt.subplots()
    plt.pie(shooting_dict.values(), labels=shooting_dict.keys(), autopct='%1.1f%%', explode=[.05, .05],
            shadow=True, colors=['#99ff99', '#eeaaf2'])
    plt.axis('equal')
    plt.title('Shooting Involvement Distribution')
    st.subheader(f"{shooting_dict['Shooting']} out of {shooting_dict['Shooting'] + shooting_dict['No Shooting']} "
                 f"crimes in this area involved a shooting")
    st.pyplot(fig)


def map_crimes(crime_df):
    crime_df = crime_df.loc[crime_df['lat'] != 0]
    return crime_df


def graph_times(crime_df):
    # for time in crime_df['HOUR']:
    time_dict = {}
    fig, ax = plt.subplots()
    crime_df = crime_df[['HOUR']]
    plt.hist(crime_df, bins=range(25), align='left', color='grey', edgecolor='lightblue')
    plt.title(f"Time of Day Histogram")
    plt.ylabel("Number of Crimes")
    plt.xlabel("Time of Day")
    ax.set_xticks(np.arange(0, 24))
    plt.xticks(fontsize=8, rotation=90)
    st.pyplot(fig)


def graph_day(crime_df):
    day_dict = {}
    for day in ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']:
        day_dict[day] = len(crime_df.loc[crime_df['DAY_OF_WEEK'] == day])
    days = list(day_dict.keys())
    values = list(day_dict.values())
    fig, ax = plt.subplots()
    plt.bar(days, values, color='grey')
    for i in range(len(days)):
        plt.text(i, values[i], values[i], ha='center')
    plt.xlabel("Day of the Week")
    plt.ylabel("Number of Crimes")
    plt.title("Crimes by Day of the Week")
    plt.xticks(rotation=45)
    st.pyplot(fig)


def main():
    st.title("Ryan's Boston Crime Streamlit Project")
    st.sidebar.write("What page would you like?")
    crime_df = read_crime_file()
    district_df = read_districts_file()
    option = st.sidebar.radio("Select Page", ("District Analysis", "Time Analysis"))
    if option == 'District Analysis':
        # streamlit multiselect, uses get_district_list function for list of districts by name.
        # user can select none or multiple districts and a list of their choices is outputted
        district_choices = st.multiselect('District', get_district_list(district_df))
        # calls analyze_district function, passes in arguments crime dataframe, district dataframe,
        # and list of district choices.  Goes to line 39
        analyze_district(crime_df, district_df, district_choices)
    elif option == 'Time Analysis':
        st.header("Breakdown of crimes reported based off time of day")
        st.header(" ")
        st.write()
        graph_times(crime_df)
        st.header("Breakdown of crimes reported based off day of week")
        st.header(" ")
        graph_day(crime_df)
        pass


main()



