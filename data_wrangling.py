import pandas as pd



def give_location_events(data, year=None, top_n=20):
    if year:
        location_events = data[(data['geocode'] != "-") & (data["year"] == year)].groupby('geocode')['programID'].nunique().reset_index(
            name="count").sort_values(by="count", ascending=True).tail(top_n)
    else:
        location_events = data[data['geocode'] != "-"].groupby('geocode')[
            'programID'].nunique().reset_index(
            name="count").sort_values(by="count", ascending=True).tail(top_n)
    return location_events


def read_all_performances():
    return pd.read_csv("data/all_performances_preprocessed_v6.csv", sep=";")


def read_country_data():
    return pd.read_csv("data/all_locations_aggregated.csv")


def read_state_data():
    return pd.read_csv("data/all_locations_aggregated_state.csv")