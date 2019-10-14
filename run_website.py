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

app.config['suppress_callback_exceptions']=True

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
                 }, style={"marginTop": "100"})),
                dcc.Dropdown(
                    id='location-dropdown',
                    options=[
                        {'label': 'World', 'value': 'World'},
                        {'label': 'USA', 'value': 'USA'}
                    ],
                    value='World',
                    clearable=False
                ),
            ]), width=9, id="map-and-dropdown", style={"marginLeft": "12%"}),
                dbc.Col(dbc.Tabs(
            [
                dbc.Tab([dcc.Loading(html.Div(id="composer-graph"))],label="Composer", tab_id="tab-1"),
                dbc.Tab([dcc.Loading(html.Div(id="conductor-graph"))], label="Conductor", tab_id="tab-2"),
                dbc.Tab([dcc.Loading(html.Div(id="worktitle-graph"))], label="WorkTitle", tab_id="tab-3"),
                dbc.Tab([dcc.Loading(html.Div(id="venue-graph"))], label="Venue", tab_id="tab-4"),
                dbc.Tab([dcc.Loading(html.Div(id="soloist-graph"))], label="Soloist", tab_id="tab-5"),
                dbc.Tab([dcc.Loading(html.Div(id="orchestra-graph"))], label="Orchestra", tab_id="tab-6"),
                dbc.Tab([dcc.Loading(html.Div(id="instrument-graph"))], label="Solo Instrument", tab_id="tab-7"),
                dbc.Tab([dcc.Loading(html.Div(id="season-graph"))], label="Season", tab_id="tab-8"),
            ],
            id="tabs",
            active_tab="tab-1",
        ), style={"paddingTop": "20px", "marginLeft": "12%"}, width=9)]
        ), html.Div(id="testing-stuff")
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
                             color_continuous_scale=px.colors.cmocean.phase)
        fig.update_layout(margin={"l": 0, "r": 0, "b": 0, "t": 10, "pad": 4})

        return fig

    elif value == "USA":
        return px.scatter_geo(big_location_aggregation_state, locations="State", color="count", hover_name="State",
                     animation_frame="year", scope="usa", locationmode="USA-states", size="log_count", hover_data=["year"],
                              color_continuous_scale=px.colors.cmocean.phase)
#

@app.callback(Output("composer-graph", "children"),
              [Input('location-dropdown', 'value'),
               Input("location-graph", "clickData")])
def make_composer_figure(value, clickData):
    if clickData:
        if value == "World":
            year = clickData["points"][0]["customdata"][0]
            location = clickData["points"][0]["location"]
            composer_events = all_performances[(all_performances["geocode"] == location) & (all_performances["year"] == year)].groupby('composerName')['programID'].nunique().reset_index(name="count").sort_values(
                by='count', ascending=True).tail(20)
            fig = px.bar(composer_events, x="count", y="composerName", orientation='h', color="count",
                         color_continuous_scale=px.colors.cmocean.phase, text="count",
                         title=f'Number of Events per Composer (top 20) in {location} in {year}')
            fig.update_layout(xaxis={"dtick": 1, "automargin": True, "autorange": True}, yaxis={"automargin": True})
            if composer_events["count"].max() > 100:
                fig.update_layout(xaxis_type="log")
            else:
                pass
            return dcc.Graph(figure=fig, id="composer-bar", config={
                                'displayModeBar': False
                                 })
        elif value == "USA":
            year = clickData["points"][0]["customdata"][0]
            location = clickData["points"][0]["location"]
            composer_events = \
            all_performances[(all_performances["State"] == location) & (all_performances["year"] == year)].groupby(
                'composerName')['programID'].nunique().reset_index(name="count").sort_values(
                by='count', ascending=True).tail(20)
            fig = px.bar(composer_events, x="count", y="composerName", orientation='h', color="count",
                         color_continuous_scale=px.colors.cmocean.phase,
                         title=f'Number of Events per Composer (top 20) in {location}, USA in {year}')
            fig.update_layout(xaxis={"dtick": 1, "automargin": True}, yaxis={"automargin": True})
            if composer_events["count"].max() > 100:
                fig.update_layout(xaxis_type="log")
            else:
                pass
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
            conductor_events = all_performances[(all_performances["geocode"] == location) & (all_performances["year"] == year)].groupby('conductorName')['programID'].nunique().reset_index(name="count").sort_values(
                by='count', ascending=True).tail(20)
            fig = px.bar(conductor_events, x="count", y="conductorName", orientation='h', color="count",
                         color_continuous_scale=px.colors.cmocean.phase,
                         title=f'Number of Events per Conductor (top 20) in {location} in {year}')
            fig.update_layout(xaxis={"dtick": 1, "automargin": True}, yaxis={"automargin": True})
            if conductor_events["count"].max() > 100:
                fig.update_layout(xaxis_type="log")
            else:
                pass
            return dcc.Graph(figure=fig, id="conductor-bar", config={
                                'displayModeBar': False
                                 })
        elif value == "USA":
            year = clickData["points"][0]["customdata"][0]
            location = clickData["points"][0]["location"]
            conductor_events = \
            all_performances[(all_performances["State"] == location) & (all_performances["year"] == year)].groupby(
                'conductorName')['programID'].nunique().reset_index(name="count").sort_values(
                by='count', ascending=True).tail(20)
            fig = px.bar(conductor_events, x="count", y="conductorName", orientation='h', color="count",
                         color_continuous_scale=px.colors.cmocean.phase,
                         title=f'Number of Events per Conductor (top 20) in {location}, USA in {year}')
            fig.update_layout(xaxis={"dtick": 1, "automargin": True}, yaxis={"automargin": True})
            if conductor_events["count"].max() > 100:
                fig.update_layout(xaxis_type="log")
            else:
                pass
            return dcc.Graph(figure=fig, id="conductor-bar", config={
                'displayModeBar': False
            })
    else:
        return html.P("Select a point on the map!")


@app.callback(Output("worktitle-graph", "children"),
              [Input("location-dropdown", "value"),
               Input("location-graph", "clickData")])
def make_worktitle_figure(value, clickData):
    if clickData:
        if value == "World":
            year = clickData["points"][0]["customdata"][0]
            location = clickData["points"][0]["location"]
            worktitle_events = all_performances[(all_performances["geocode"] == location) & (all_performances["year"] == year)].groupby(
                'workTitle')['programID'].nunique().reset_index(name="count").sort_values(by='count', ascending=True).tail(20)
            fig = px.bar(worktitle_events, x="count", y="workTitle", orientation='h', color="count",
                         color_continuous_scale=px.colors.cmocean.phase,
                         title=f'Number of Events per Work title (top 20) in {location} in {year}')
            fig.update_layout(xaxis={"dtick": 1, "automargin": True}, yaxis={"automargin": True})
            if worktitle_events["count"].max() > 100:
                fig.update_layout(xaxis_type="log")
            else:
                pass
            return dcc.Graph(figure=fig, id="worktitle-bar", config={
                'displayModeBar': False
            })
        elif value == "USA":
            year = clickData["points"][0]["customdata"][0]
            location = clickData["points"][0]["location"]
            worktitle_events = \
            all_performances[(all_performances["State"] == location) & (all_performances["year"] == year)].groupby(
                'workTitle')['programID'].nunique().reset_index(name="count").sort_values(by='count',
                                                                                          ascending=True).tail(20)
            fig = px.bar(worktitle_events, x="count", y="workTitle", orientation='h', color="count",
                         color_continuous_scale=px.colors.cmocean.phase,
                         title=f'Number of Events per Work title (top 20) in {location} in {year}')
            fig.update_layout(xaxis={"dtick": 1, "automargin": True}, yaxis={"automargin": True})
            if worktitle_events["count"].max() > 100:
                fig.update_layout(xaxis_type="log")
            else:
                pass
            return dcc.Graph(figure=fig, id="worktitle-bar", config={
                'displayModeBar': False
            })
    else:
        return html.P("Select a point on a map!")


@app.callback(Output("venue-graph", "children"),
              [Input("location-dropdown", "value"),
               Input("location-graph", "clickData")])
def make_venue_figure(value, clickData):
    if clickData:
        if value == "World":
            year = clickData["points"][0]["customdata"][0]
            location = clickData["points"][0]["location"]
            venue_events = all_performances[(all_performances["geocode"] == location) & (all_performances["year"] == year)].groupby(
                'Venue')['programID'].nunique().reset_index(name="count").sort_values(by='count', ascending=True).tail(20)
            fig = px.bar(venue_events, x="count", y="Venue", orientation='h', color="count",
                         color_continuous_scale=px.colors.cmocean.phase,
                         title=f'Number of Events per Venue (top 20) in {location} in {year}')
            fig.update_layout(xaxis={"dtick": 1, "automargin": True}, yaxis={"automargin": True})
            if venue_events["count"].max() > 100:
                fig.update_layout(xaxis_type="log")
            else:
                pass
            return dcc.Graph(figure=fig, id="venue-bar", config={
                'displayModeBar': False
            })
        elif value == "USA":
            year = clickData["points"][0]["customdata"][0]
            location = clickData["points"][0]["location"]
            venue_events = \
            all_performances[(all_performances["State"] == location) & (all_performances["year"] == year)].groupby(
                'Venue')['programID'].nunique().reset_index(name="count").sort_values(by='count',
                                                                                          ascending=True).tail(20)
            fig = px.bar(venue_events, x="count", y="Venue", orientation='h', color="count",
                         color_continuous_scale=px.colors.cmocean.phase,
                         title=f'Number of Events per Work title (top 20) in {location} in {year}')
            fig.update_layout(xaxis={"dtick": 1, "automargin": True}, yaxis={"automargin": True})
            if venue_events["count"].max() > 100:
                fig.update_layout(xaxis_type="log")
            else:
                pass
            return dcc.Graph(figure=fig, id="venue-bar", config={
                'displayModeBar': False
            })
    else:
        return html.P("Select a point on a map!")


@app.callback(Output("soloist-graph", "children"),
              [Input('location-dropdown', 'value'),
               Input("location-graph", "clickData")])
def make_soloist_figure(value, clickData):
    if clickData:
        if value == "World":
            year = clickData["points"][0]["customdata"][0]
            location = clickData["points"][0]["location"]
            composer_events = all_performances[(all_performances["geocode"] == location) & (all_performances["year"] == year)].groupby(
                'soloistName')['programID'].nunique().reset_index(name="count").sort_values(
                by='count', ascending=True).tail(20)
            fig = px.bar(composer_events, x="count", y="soloistName", orientation='h', color="count",
                         color_continuous_scale=px.colors.cmocean.phase, text="count",
                         title=f'Number of Events per Soloist (top 20) in {location} in {year}')
            fig.update_layout(xaxis={"dtick": 1, "automargin": True, "autorange": True}, yaxis={"automargin": True})
            if composer_events["count"].max() > 100:
                fig.update_layout(xaxis_type="log")
            else:
                pass
            return dcc.Graph(figure=fig, id="soloist-bar", config={
                                'displayModeBar': False
                                 })
        elif value == "USA":
            year = clickData["points"][0]["customdata"][0]
            location = clickData["points"][0]["location"]
            composer_events = \
            all_performances[(all_performances["State"] == location) & (all_performances["year"] == year)].groupby(
                'soloistName')['programID'].nunique().reset_index(name="count").sort_values(
                by='count', ascending=True).tail(20)
            fig = px.bar(composer_events, x="count", y="soloistName", orientation='h', color="count",
                         color_continuous_scale=px.colors.cmocean.phase,
                         title=f'Number of Events per Soloist (top 20) in {location}, USA in {year}')
            fig.update_layout(xaxis={"dtick": 1, "automargin": True}, yaxis={"automargin": True})
            if composer_events["count"].max() > 100:
                fig.update_layout(xaxis_type="log")
            else:
                pass
            return dcc.Graph(figure=fig, id="soloist-bar", config={
                'displayModeBar': False
            })
    else:
        return html.P("Select a point on the map!")


@app.callback(Output("orchestra-graph", "children"),
              [Input('location-dropdown', 'value'),
               Input("location-graph", "clickData")])
def make_orchestra_figure(value, clickData):
    if clickData:
        if value == "World":
            year = clickData["points"][0]["customdata"][0]
            location = clickData["points"][0]["location"]
            composer_events = all_performances[(all_performances["geocode"] == location) & (all_performances["year"] == year)].groupby(
                'orchestra')['programID'].nunique().reset_index(name="count").sort_values(
                by='count', ascending=True).tail(20)
            fig = px.bar(composer_events, x="count", y="orchestra", orientation='h', color="count",
                         color_continuous_scale=px.colors.cmocean.phase, text="count",
                         title=f'Number of Events per Orchestra (top 20) in {location} in {year}')
            fig.update_layout(xaxis={"dtick": 1, "automargin": True, "autorange": True}, yaxis={"automargin": True})
            if composer_events["count"].max() > 100:
                fig.update_layout(xaxis_type="log")
            else:
                pass
            return dcc.Graph(figure=fig, id="orchestra-bar", config={
                                'displayModeBar': False
                                 })
        elif value == "USA":
            year = clickData["points"][0]["customdata"][0]
            location = clickData["points"][0]["location"]
            composer_events = \
            all_performances[(all_performances["State"] == location) & (all_performances["year"] == year)].groupby(
                'orchestra')['programID'].nunique().reset_index(name="count").sort_values(
                by='count', ascending=True).tail(20)
            fig = px.bar(composer_events, x="count", y="orchestra", orientation='h', color="count",
                         color_continuous_scale=px.colors.cmocean.phase,
                         title=f'Number of Events per Orchestra (top 20) in {location}, USA in {year}')
            fig.update_layout(xaxis={"dtick": 1, "automargin": True}, yaxis={"automargin": True})
            if composer_events["count"].max() > 100:
                fig.update_layout(xaxis_type="log")
            else:
                pass
            return dcc.Graph(figure=fig, id="orchestra-bar", config={
                'displayModeBar': False
            })
    else:
        return html.P("Select a point on the map!")


@app.callback(Output("instrument-graph", "children"),
              [Input('location-dropdown', 'value'),
               Input("location-graph", "clickData")])
def make_instrument_figure(value, clickData):
    if clickData:
        if value == "World":
            year = clickData["points"][0]["customdata"][0]
            location = clickData["points"][0]["location"]
            composer_events = all_performances[(all_performances["geocode"] == location) & (all_performances["year"] == year)].groupby(
                'soloistInstrument')['programID'].nunique().reset_index(name="count").sort_values(
                by='count', ascending=True).tail(20)
            fig = px.bar(composer_events, x="count", y="soloistInstrument", orientation='h', color="count",
                         color_continuous_scale=px.colors.cmocean.phase, text="count",
                         title=f'Number of Events per Soloist Instrument (top 20) in {location} in {year}')
            fig.update_layout(xaxis={"dtick": 1, "automargin": True, "autorange": True}, yaxis={"automargin": True})
            if composer_events["count"].max() > 100:
                fig.update_layout(xaxis_type="log")
            else:
                pass
            return dcc.Graph(figure=fig, id="instrument-bar", config={
                                'displayModeBar': False
                                 })
        elif value == "USA":
            year = clickData["points"][0]["customdata"][0]
            location = clickData["points"][0]["location"]
            composer_events = \
            all_performances[(all_performances["State"] == location) & (all_performances["year"] == year)].groupby(
                'soloistInstrument')['programID'].nunique().reset_index(name="count").sort_values(
                by='count', ascending=True).tail(20)
            fig = px.bar(composer_events, x="count", y="soloistInstrument", orientation='h', color="count",
                         color_continuous_scale=px.colors.cmocean.phase,
                         title=f'Number of Events per Soloist Instrument (top 20) in {location}, USA in {year}')
            fig.update_layout(xaxis={"dtick": 1, "automargin": True}, yaxis={"automargin": True})
            if composer_events["count"].max() > 100:
                fig.update_layout(xaxis_type="log")
            else:
                pass
            return dcc.Graph(figure=fig, id="instrument-bar", config={
                'displayModeBar': False
            })
    else:
        return html.P("Select a point on the map!")


@app.callback(Output("season-graph", "children"),
              [Input('location-dropdown', 'value'),
               Input("location-graph", "clickData")])
def make_season_figure(value, clickData):
    if clickData:
        if value == "World":
            year = clickData["points"][0]["customdata"][0]
            location = clickData["points"][0]["location"]
            composer_events = all_performances[(all_performances["geocode"] == location) & (all_performances["year"] == year)].groupby(
                'seasonOfYear')['programID'].nunique().reset_index(name="count").sort_values(
                by='count', ascending=True).tail(20)
            fig = px.bar(composer_events, x="count", y="seasonOfYear", orientation='h', color="count",
                         color_continuous_scale=px.colors.cmocean.phase, text="count",
                         title=f'Number of Events per Season of Year (top 20) in {location} in {year}')
            fig.update_layout(xaxis={"dtick": 1, "automargin": True, "autorange": True}, yaxis={"automargin": True})
            if composer_events["count"].max() > 100:
                fig.update_layout(xaxis_type="log")
            else:
                pass
            return dcc.Graph(figure=fig, id="season-bar", config={
                                'displayModeBar': False
                                 })
        elif value == "USA":
            year = clickData["points"][0]["customdata"][0]
            location = clickData["points"][0]["location"]
            composer_events = \
            all_performances[(all_performances["State"] == location) & (all_performances["year"] == year)].groupby(
                'seasonOfYear')['programID'].nunique().reset_index(name="count").sort_values(
                by='count', ascending=True).tail(20)
            fig = px.bar(composer_events, x="count", y="seasonOfYear", orientation='h', color="count",
                         color_continuous_scale=px.colors.cmocean.phase,
                         title=f'Number of Events per Season of Year (top 20) in {location}, USA in {year}')
            fig.update_layout(xaxis={"dtick": 1, "automargin": True}, yaxis={"automargin": True})
            if composer_events["count"].max() > 100:
                fig.update_layout(xaxis_type="log")
            else:
                pass
            return dcc.Graph(figure=fig, id="season-bar", config={
                'displayModeBar': False
            })
    else:
        return html.P("Select a point on the map!")


#
@app.callback(Output("location-graph", 'clickData'),
              [Input("location-dropdown", "value")])
def clear_clickdata(_):
    return None


@app.callback(Output("testing-stuff", 'children'),
              [Input("composer-bar", "clickData")])
def clear_clickdata(clickData):
    return json.dumps(clickData)


if __name__ == '__main__':
    big_location_aggregation = dw.read_country_data().sort_values("year").reset_index(drop=True)
    big_location_aggregation_state = dw.read_state_data().sort_values("year").reset_index(drop=True)
    all_performances = dw.read_all_performances().sort_values("year").reset_index(drop=True)
    app.run_server(debug=True, port=5000, host='0.0.0.0')
