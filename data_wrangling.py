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


def replace_spaces(x):
    try:
        return " ".join(x.split())
    except AttributeError:
        pass


def read_all_performances():
    all_p = pd.read_csv("data/all_performances_preprocessed_v6.csv", sep=";")
    all_p["composerName"] = all_p["composerName"].apply(lambda x: replace_spaces(x))
    all_p.fillna("-", inplace=True)
    return all_p


def read_country_data():
    return pd.read_csv("data/all_locations_aggregated.csv")


def read_state_data():
    return pd.read_csv("data/all_locations_aggregated_state.csv")