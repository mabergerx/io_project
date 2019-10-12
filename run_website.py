import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import data_wrangling as dw
import dash_table
import plotly.express as px
from dash.dependencies import Input, Output
import json


# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# print(big_location_aggregation.head(5))

# df = pd.read_csv(
#     'https://gist.githubusercontent.com/chriddyp/'
#     'cb5392c35661370d95f300086accea51/raw/'
#     '8e0768211f6b747c0db42a9ce9a0937dafcbd8b2/'
#     'indicators.csv')

# available_indicators = df['Indicator Name'].unique()

app.layout = html.Div([

    dbc.Row(
            [
                dbc.Col(html.Div([
                dcc.Loading(dcc.Graph(id="location-graph", config={
                'displayModeBar': False
                 })),
                dcc.Dropdown(
                    id='location-dropdown',
                    options=[
                        {'label': 'World', 'value': 'World'},
                        {'label': 'USA', 'value': 'USA'}
                    ],
                    value='World',
                    clearable=False
                ),
                html.P(id='placeholder-text'),
            ]), width=6),
                dbc.Col(dbc.Tabs(
            [
                dbc.Tab([dcc.Loading(html.Div(id="composer-graph"))],label="Composer", tab_id="tab-1"),
                dbc.Tab([dcc.Loading(html.Div(id="conductor-graph"))], label="Conductor", tab_id="tab-2"),
            ],
            id="tabs",
            active_tab="tab-1",
        ), style={"paddingTop": "20px"})]
        ),
])

# @app.callback(Output("content", "children"), [Input("tabs", "active_tab")])
# def switch_tab(at):
#     if at == "tab-1":
#         return tab1_content
#     elif at == "tab-2":
#         return tab2_content
#     return html.P("This shouldn't ever be displayed...")

# @app.callback(Output('location_data_country', 'data'),
#               [Input('location-dropdown', 'value')])
# def filter_countries(dropdown_value):
#     if dropdown_value == "World":
#         stuff = big_location_aggregation.reset_index(drop=True)
#         return stuff.to_json(orient="records")
#     elif dropdown_value == "USA":
#         stuff = big_location_aggregation_state.reset_index(drop=True)
#         return stuff.to_json(orient="records")


@app.callback(Output("location-graph", "figure"),
              [Input('location-dropdown', 'value')])
def make_location_figure(value):
    if value == "World":
        fig = px.scatter_geo(big_location_aggregation, locations="geocode", color="count", hover_name="country",
                         animation_frame="year", projection="natural earth", size="log_count", hover_data=["year"],
                         color_continuous_scale=px.colors.cmocean.delta, title="Number of events per Country per Year")

        return fig

    elif value == "USA":
        return px.scatter_geo(big_location_aggregation_state, locations="State", color="count", hover_name="State",
                     animation_frame="year", scope="usa", locationmode="USA-states", size="log_count", hover_data=["year"],
                     color_continuous_scale=px.colors.cmocean.delta, title="Number of events per State per Year (USA)")
#

@app.callback(Output("composer-graph", "children"),
              [Input('location-dropdown', 'value'),
               Input("location-graph", "clickData")])
def make_composer_figure(value, clickData):
    if clickData:
        if value == "World":
            year = clickData["points"][0]["customdata"][0]
            location = clickData["points"][0]["location"]
            print(year)
            composer_events = all_performances[(all_performances["geocode"] == location) & (all_performances["year"] == year)].groupby('composerName')['programID'].nunique().reset_index(name="count").sort_values(
                by='count', ascending=True).tail(20)
            fig = px.bar(composer_events, x="count", y="composerName", orientation='h',
                         title=f'Number of Events by Composer (top 20) in {location} in {year}')
            fig.update_layout(xaxis_type="log")
            return dcc.Graph(figure=fig, id="composer-bar", config={
                                'displayModeBar': False
                                 })
        elif value == "USA":
            year = clickData["points"][0]["customdata"][0]
            location = clickData["points"][0]["location"]
            print(year)
            composer_events = \
            all_performances[(all_performances["State"] == location) & (all_performances["year"] == year)].groupby(
                'composerName')['programID'].nunique().reset_index(name="count").sort_values(
                by='count', ascending=True).tail(20)
            fig = px.bar(composer_events, x="count", y="composerName", orientation='h',
                         title=f'Number of Events by Composer (top 20) in {location}, USA in {year}')
            fig.update_layout(xaxis_type="log")
            return dcc.Graph(figure=fig, id="composer-bar", config={
                'displayModeBar': False
            })
    else:
        return html.P("Select a point on the map!")


@app.callback(Output("conductor-graph", "children"),
              [Input('location-dropdown', 'value'),
               Input("location-graph", "clickData")])
def make_conductor_figure(value, clickData):
    if clickData:
        if value == "World":
            year = clickData["points"][0]["customdata"][0]
            location = clickData["points"][0]["location"]
            print(year)
            composer_events = all_performances[(all_performances["geocode"] == location) & (all_performances["year"] == year)].groupby('conductorName')['programID'].nunique().reset_index(name="count").sort_values(
                by='count', ascending=True).tail(20)
            fig = px.bar(composer_events, x="count", y="conductorName", orientation='h',
                         title=f'Number of Events by Conductor (top 20) in {location} in {year}')
            fig.update_layout(xaxis_type="log")
            return dcc.Graph(figure=fig, id="conductor-bar", config={
                                'displayModeBar': False
                                 })
        elif value == "USA":
            year = clickData["points"][0]["customdata"][0]
            location = clickData["points"][0]["location"]
            print(year)
            composer_events = \
            all_performances[(all_performances["State"] == location) & (all_performances["year"] == year)].groupby(
                'conductorName')['programID'].nunique().reset_index(name="count").sort_values(
                by='count', ascending=True).tail(20)
            fig = px.bar(composer_events, x="count", y="conductorName", orientation='h',
                         title=f'Number of Events by Conductor (top 20) in {location}, USA in {year}')
            fig.update_layout(xaxis_type="log")
            return dcc.Graph(figure=fig, id="conductor-bar", config={
                'displayModeBar': False
            })
    else:
        return html.P("Select a point on the map!")

#
#
#
@app.callback(Output("placeholder-text", 'children'),
              [Input("location-graph", "clickData")])
def show_clickdata(data):
    return json.dumps(data)


if __name__ == '__main__':
    big_location_aggregation = dw.read_country_data().sort_values("year").reset_index(drop=True)
    big_location_aggregation_state = dw.read_state_data().sort_values("year").reset_index(drop=True)
    all_performances = dw.read_all_performances().sort_values("year").reset_index(drop=True)
    app.run_server(debug=False, port=5000, host='0.0.0.0')
