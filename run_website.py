# Author: Mark Berger (https://github.com/mabergerx)
# ==============================================================================
"""Script that defines the Dash website layout.
Use:
python run_website.py

Runs a Flask server with a Dash app wrapped around it. Navigate to localhost:5000.
"""

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import data_wrangling as dw
import dash_table
import plotly.express as px
from dash.dependencies import Input, Output, State

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.config['suppress_callback_exceptions']=True

TABLE_PAGE_SIZE = 10

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
                dbc.Tab([dcc.Loading(html.Div(id="composer-graph")), html.Div(id="composer-table", style={"marginBottom": "50px"})],label="Composer", tab_id="tab-1"),
                dbc.Tab([dcc.Loading(html.Div(id="conductor-graph")), html.Div(id="conductor-table", style={"marginBottom": "50px"})], label="Conductor", tab_id="tab-2"),
                dbc.Tab([dcc.Loading(html.Div(id="worktitle-graph")), html.Div(id="worktitle-table", style={"marginBottom": "50px"})], label="WorkTitle", tab_id="tab-3"),
                dbc.Tab([dcc.Loading(html.Div(id="venue-graph")), html.Div(id="venue-table", style={"marginBottom": "50px"})], label="Venue", tab_id="tab-4"),
                dbc.Tab([dcc.Loading(html.Div(id="soloist-graph")), html.Div(id="soloist-table", style={"marginBottom": "50px"})], label="Soloist", tab_id="tab-5"),
                dbc.Tab([dcc.Loading(html.Div(id="orchestra-graph")), html.Div(id="orchestra-table", style={"marginBottom": "50px"})], label="Orchestra", tab_id="tab-6"),
                dbc.Tab([dcc.Loading(html.Div(id="instrument-graph")), html.Div(id="instrument-table", style={"marginBottom": "50px"})], label="Solo Instrument", tab_id="tab-7"),
                dbc.Tab([dcc.Loading(html.Div(id="season-graph")), html.Div(id="season-table", style={"marginBottom": "50px"})], label="Season", tab_id="tab-8"),
            ],
            id="tabs",
            active_tab="tab-1",
        ), style={"paddingTop": "20px", "marginLeft": "12%"}, width=9),
            ]
        ),
    dcc.Store(id="current-bar-clickdata")
])
#
#
# @app.callback(
#     Output('performances-table', 'data'),
#     [Input("composer-bar", "clickData"),
#      Input("conductor-bar", "clickData"),
#      Input('performances-table', "page_current"),
#      Input('performances-table', "page_size"),
#      Input('performances-table', 'sort_by')]
# )
# def update_table_data(composerClick, conductorClick, page_current, page_size, sort_by):
#     if composerClick:
#         print(composerClick)
#         # composer_name = composerClick
#         if len(sort_by):
#             dff = all_performances.sort_values(
#                 sort_by[0]['column_id'],
#                 ascending=sort_by[0]['direction'] == 'asc',
#                 inplace=False
#             )
#         else:
#             # No sort is applied
#             dff = all_performances
#
#         return dff.iloc[
#                page_current * page_size:(page_current + 1) * page_size
#                ].to_dict('records')

# @app.callback(
#     Output('performances-table', 'data'),
#     [Input("current-bar-clickdata", "data")])
# def update_table(current_data):
#     current_df = pd.read_json(current_data)
#     return current_df.to_dict('records')
    # print(len(current_df))
    # if len(sort_by):
    #     dff = current_df.sort_values(
    #         sort_by[0]['column_id'],
    #         ascending=sort_by[0]['direction'] == 'asc',
    #         inplace=False
    #     )
    # else:
    #     # No sort is applied
    #     dff = current_df
    #
    # return dff.iloc[
    #     page_current*page_size:(page_current+ 1)*page_size
    # ].to_dict('records')


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
            composer_events = composer_events[composer_events["composerName"] != "-"]
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
            composer_events = composer_events[composer_events["composerName"] != "-"]
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
            conductor_events = conductor_events[conductor_events["conductorName"] != "-"]
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
            conductor_events = conductor_events[conductor_events["conductorName"] != "-"]
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
            worktitle_events = worktitle_events[worktitle_events["workTitle"] != "-"]
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
            worktitle_events = worktitle_events[worktitle_events["workTitle"] != "-"]
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
            venue_events = venue_events[venue_events["Venue"] != "-"]
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
            venue_events = venue_events[venue_events["Venue"] != "-"]
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
            soloist_events = all_performances[(all_performances["geocode"] == location) & (all_performances["year"] == year)].groupby(
                'soloistName')['programID'].nunique().reset_index(name="count").sort_values(
                by='count', ascending=True).tail(20)
            soloist_events = soloist_events[soloist_events["soloistName"] != "-"]
            fig = px.bar(soloist_events, x="count", y="soloistName", orientation='h', color="count",
                         color_continuous_scale=px.colors.cmocean.phase, text="count",
                         title=f'Number of Events per Soloist (top 20) in {location} in {year}')
            fig.update_layout(xaxis={"dtick": 1, "automargin": True, "autorange": True}, yaxis={"automargin": True})
            if soloist_events["count"].max() > 100:
                fig.update_layout(xaxis_type="log")
            else:
                pass
            return dcc.Graph(figure=fig, id="soloist-bar", config={
                                'displayModeBar': False
                                 })
        elif value == "USA":
            year = clickData["points"][0]["customdata"][0]
            location = clickData["points"][0]["location"]
            soloist_events = \
            all_performances[(all_performances["State"] == location) & (all_performances["year"] == year)].groupby(
                'soloistName')['programID'].nunique().reset_index(name="count").sort_values(
                by='count', ascending=True).tail(20)
            soloist_events = soloist_events[soloist_events["soloistName"] != "-"]
            fig = px.bar(soloist_events, x="count", y="soloistName", orientation='h', color="count",
                         color_continuous_scale=px.colors.cmocean.phase,
                         title=f'Number of Events per Soloist (top 20) in {location}, USA in {year}')
            fig.update_layout(xaxis={"dtick": 1, "automargin": True}, yaxis={"automargin": True})
            if soloist_events["count"].max() > 100:
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
            orchestra_events = all_performances[(all_performances["geocode"] == location) & (all_performances["year"] == year)].groupby(
                'orchestra')['programID'].nunique().reset_index(name="count").sort_values(
                by='count', ascending=True).tail(20)
            orchestra_events = orchestra_events[orchestra_events["orchestra"] != "-"]
            fig = px.bar(orchestra_events, x="count", y="orchestra", orientation='h', color="count",
                         color_continuous_scale=px.colors.cmocean.phase, text="count",
                         title=f'Number of Events per Orchestra (top 20) in {location} in {year}')
            fig.update_layout(xaxis={"dtick": 1, "automargin": True, "autorange": True}, yaxis={"automargin": True})
            if orchestra_events["count"].max() > 100:
                fig.update_layout(xaxis_type="log")
            else:
                pass
            return dcc.Graph(figure=fig, id="orchestra-bar", config={
                                'displayModeBar': False
                                 })
        elif value == "USA":
            year = clickData["points"][0]["customdata"][0]
            location = clickData["points"][0]["location"]
            orchestra_events = \
            all_performances[(all_performances["State"] == location) & (all_performances["year"] == year)].groupby(
                'orchestra')['programID'].nunique().reset_index(name="count").sort_values(
                by='count', ascending=True).tail(20)
            orchestra_events = orchestra_events[orchestra_events["orchestra"] != "-"]
            fig = px.bar(orchestra_events, x="count", y="orchestra", orientation='h', color="count",
                         color_continuous_scale=px.colors.cmocean.phase,
                         title=f'Number of Events per Orchestra (top 20) in {location}, USA in {year}')
            fig.update_layout(xaxis={"dtick": 1, "automargin": True}, yaxis={"automargin": True})
            if orchestra_events["count"].max() > 100:
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
            instrument_events = all_performances[(all_performances["geocode"] == location) & (all_performances["year"] == year)].groupby(
                'soloistInstrument')['programID'].nunique().reset_index(name="count").sort_values(
                by='count', ascending=True).tail(20)
            instrument_events = instrument_events[instrument_events["soloistInstrument"] != "-"]
            fig = px.bar(instrument_events, x="count", y="soloistInstrument", orientation='h', color="count",
                         color_continuous_scale=px.colors.cmocean.phase, text="count",
                         title=f'Number of Events per Soloist Instrument (top 20) in {location} in {year}')
            fig.update_layout(xaxis={"dtick": 1, "automargin": True, "autorange": True}, yaxis={"automargin": True})
            if instrument_events["count"].max() > 100:
                fig.update_layout(xaxis_type="log")
            else:
                pass
            return dcc.Graph(figure=fig, id="instrument-bar", config={
                                'displayModeBar': False
                                 })
        elif value == "USA":
            year = clickData["points"][0]["customdata"][0]
            location = clickData["points"][0]["location"]
            instrument_events = \
            all_performances[(all_performances["State"] == location) & (all_performances["year"] == year)].groupby(
                'soloistInstrument')['programID'].nunique().reset_index(name="count").sort_values(
                by='count', ascending=True).tail(20)
            instrument_events = instrument_events[instrument_events["soloistInstrument"] != "-"]
            fig = px.bar(instrument_events, x="count", y="soloistInstrument", orientation='h', color="count",
                         color_continuous_scale=px.colors.cmocean.phase,
                         title=f'Number of Events per Soloist Instrument (top 20) in {location}, USA in {year}')
            fig.update_layout(xaxis={"dtick": 1, "automargin": True}, yaxis={"automargin": True})
            if instrument_events["count"].max() > 100:
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
            season_events = all_performances[(all_performances["geocode"] == location) & (all_performances["year"] == year)].groupby(
                'seasonOfYear')['programID'].nunique().reset_index(name="count").sort_values(
                by='count', ascending=True).tail(20)
            season_events = season_events[season_events["seasonOfYear"] != "-"]
            fig = px.bar(season_events, x="count", y="seasonOfYear", orientation='h', color="count",
                         color_continuous_scale=px.colors.cmocean.phase, text="count",
                         title=f'Number of Events per Season of Year (top 20) in {location} in {year}')
            fig.update_layout(xaxis={"dtick": 1, "automargin": True, "autorange": True}, yaxis={"automargin": True})
            if season_events["count"].max() > 100:
                fig.update_layout(xaxis_type="log")
            else:
                pass
            return dcc.Graph(figure=fig, id="season-bar", config={
                                'displayModeBar': False
                                 })
        elif value == "USA":
            year = clickData["points"][0]["customdata"][0]
            location = clickData["points"][0]["location"]
            season_events = \
            all_performances[(all_performances["State"] == location) & (all_performances["year"] == year)].groupby(
                'seasonOfYear')['programID'].nunique().reset_index(name="count").sort_values(
                by='count', ascending=True).tail(20)
            season_events = season_events[season_events["seasonOfYear"] != "-"]
            fig = px.bar(season_events, x="count", y="seasonOfYear", orientation='h', color="count",
                         color_continuous_scale=px.colors.cmocean.phase,
                         title=f'Number of Events per Season of Year (top 20) in {location}, USA in {year}')
            fig.update_layout(xaxis={"dtick": 1, "automargin": True}, yaxis={"automargin": True})
            if season_events["count"].max() > 100:
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


# @app.callback(Output("current-bar-clickdata", "data"),
#               [Input("composer-bar", "clickData")],
#               [State('location-dropdown', 'value'),
#                State("location-graph", "clickData")]
#               )
# def store_composer_clickdata(clickData, value, locationData):
#     composer_name = clickData['points'][0]['y']
#     if value == "World":
#         year = locationData["points"][0]["customdata"][0]
#         location = locationData["points"][0]["location"]
#         filtered_df = all_performances[(all_performances["composerName"] == composer_name) & (all_performances["year"] == year) & (all_performances["geocode"] == location)]
#         return filtered_df.to_json()
#     elif value == "USA":
#         year = locationData["points"][0]["customdata"][0]
#         location = locationData["points"][0]["location"]
#         filtered_df = all_performances[
#             (all_performances["composerName"] == composer_name) & (all_performances["year"] == year) & (
#                         all_performances["State"] == location)]
#         return filtered_df.to_json()


@app.callback(Output("composer-table", "children"),
              [Input("composer-bar", "clickData")],
              [State('location-dropdown', 'value'),
               State("location-graph", "clickData")]
              )
def create_composer_table(clickData, value, locationData):
    composer_name = clickData['points'][0]['y']
    if value == "World":
        year = locationData["points"][0]["customdata"][0]
        location = locationData["points"][0]["location"]
        filtered_df = all_performances[(all_performances["composerName"] == composer_name) & (all_performances["year"] == year) & (all_performances["geocode"] == location)].drop_duplicates()
        return dash_table.DataTable(
        columns=[
            {'name': i, 'id': i, 'deletable': True} for i in ['Venue', 'eventType', 'id', 'composerName', 'conductorName', 'movement',
       'workTitle', 'soloistInstrument', 'soloistName', 'programID',
       'orchestra', 'year', 'month', 'day', 'Country', 'City', 'State',
       'startingHour', 'startingMinute', 'paperProgram', 'seasonOfYear',
       'geocode']
        ],
        page_current=0,
        page_size=TABLE_PAGE_SIZE,
        data=filtered_df.to_dict('records'),
        row_deletable=False,
        page_action='native',
        sort_action='native',
        sort_mode='single',
        style_table={'overflowX': 'scroll'},
        sort_by=[],
        style_cell={'font-size': 13, 'font-family':'Avenir, sans-serif', 'height': "25px"},
        style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                }
            ],
        style_header={
            "backgroundColor": "rgb(213,86,81)",
            "color": "white",
            "textAlign": "center",
            'font-family':'Avenir, sans-serif'
        }
    )
    elif value == "USA":
        year = locationData["points"][0]["customdata"][0]
        location = locationData["points"][0]["location"]
        filtered_df = all_performances[
            (all_performances["composerName"] == composer_name) & (all_performances["year"] == year) & (
                        all_performances["State"] == location)].drop_duplicates()
        return dash_table.DataTable(
            columns=[
                {'name': i, 'id': i, 'deletable': True} for i in
                ['Venue', 'eventType', 'id', 'composerName', 'conductorName', 'movement',
                 'workTitle', 'soloistInstrument', 'soloistName', 'programID',
                 'orchestra', 'year', 'month', 'day', 'Country', 'City', 'State',
                 'startingHour', 'startingMinute', 'paperProgram', 'seasonOfYear',
                 'geocode']
            ],
            page_current=0,
            page_size=TABLE_PAGE_SIZE,
            data=filtered_df.to_dict('records'),
            page_action='native',
            sort_action='native',
            sort_mode='single',
            style_table={'overflowX': 'scroll'},
            sort_by=[],
            style_cell={'font-size': 13, 'font-family': 'Avenir, sans-serif', 'height': "25px"},
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                }
            ],
            style_header={
                "backgroundColor": "rgb(213,86,81)",
                "color": "white",
                "textAlign": "center",
                'font-family': 'Avenir, sans-serif'
            }
        )


@app.callback(Output("conductor-table", "children"),
              [Input("conductor-bar", "clickData")],
              [State('location-dropdown', 'value'),
               State("location-graph", "clickData")]
              )
def create_conductor_table(clickData, value, locationData):
    conductor_name = clickData['points'][0]['y']
    if value == "World":
        year = locationData["points"][0]["customdata"][0]
        location = locationData["points"][0]["location"]
        filtered_df = all_performances[(all_performances["conductorName"] == conductor_name) & (all_performances["year"] == year) & (all_performances["geocode"] == location)].drop_duplicates()
        return dash_table.DataTable(
        columns=[
            {'name': i, 'id': i, 'deletable': True} for i in ['Venue', 'eventType', 'id', 'composerName', 'conductorName', 'movement',
       'workTitle', 'soloistInstrument', 'soloistName', 'programID',
       'orchestra', 'year', 'month', 'day', 'Country', 'City', 'State',
       'startingHour', 'startingMinute', 'paperProgram', 'seasonOfYear',
       'geocode']
        ],
        page_current=0,
        page_size=TABLE_PAGE_SIZE,
        data=filtered_df.to_dict('records'),
        page_action='native',
        sort_action='native',
        sort_mode='single',
        style_table={'overflowX': 'scroll'},
        sort_by=[],
        style_cell={'font-size': 13, 'font-family':'Avenir, sans-serif', 'height': "25px"},
        style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                }
            ],
        style_header={
            "backgroundColor": "rgb(213,86,81)",
            "color": "white",
            "textAlign": "center",
            'font-family':'Avenir, sans-serif'
        }
    )
    elif value == "USA":
        year = locationData["points"][0]["customdata"][0]
        location = locationData["points"][0]["location"]
        filtered_df = all_performances[
            (all_performances["conductorName"] == conductor_name) & (all_performances["year"] == year) & (
                        all_performances["State"] == location)].drop_duplicates()
        return dash_table.DataTable(
            columns=[
                {'name': i, 'id': i, 'deletable': True} for i in
                ['Venue', 'eventType', 'id', 'composerName', 'conductorName', 'movement',
                 'workTitle', 'soloistInstrument', 'soloistName', 'programID',
                 'orchestra', 'year', 'month', 'day', 'Country', 'City', 'State',
                 'startingHour', 'startingMinute', 'paperProgram', 'seasonOfYear',
                 'geocode']
            ],
            page_current=0,
            page_size=TABLE_PAGE_SIZE,
            data=filtered_df.to_dict('records'),
            page_action='native',
            sort_action='native',
            sort_mode='single',
            style_table={'overflowX': 'scroll'},
            sort_by=[],
            style_cell={'font-size': 13, 'font-family': 'Avenir, sans-serif', 'height': "25px"},
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                }
            ],
            style_header={
                "backgroundColor": "rgb(213,86,81)",
                "color": "white",
                "textAlign": "center",
                'font-family': 'Avenir, sans-serif'
            }
        )


@app.callback(Output("worktitle-table", "children"),
              [Input("worktitle-bar", "clickData")],
              [State('location-dropdown', 'value'),
               State("location-graph", "clickData")]
              )
def create_worktitle_table(clickData, value, locationData):
    worktitle_name = clickData['points'][0]['y']
    if value == "World":
        year = locationData["points"][0]["customdata"][0]
        location = locationData["points"][0]["location"]
        filtered_df = all_performances[(all_performances["workTitle"] == worktitle_name) & (all_performances["year"] == year) & (all_performances["geocode"] == location)].drop_duplicates()
        return dash_table.DataTable(
        columns=[
            {'name': i, 'id': i, 'deletable': True} for i in ['Venue', 'eventType', 'id', 'composerName', 'conductorName', 'movement',
       'workTitle', 'soloistInstrument', 'soloistName', 'programID',
       'orchestra', 'year', 'month', 'day', 'Country', 'City', 'State',
       'startingHour', 'startingMinute', 'paperProgram', 'seasonOfYear',
       'geocode']
        ],
        page_current=0,
        page_size=TABLE_PAGE_SIZE,
        data=filtered_df.to_dict('records'),
        page_action='native',
        sort_action='native',
        sort_mode='single',
        style_table={'overflowX': 'scroll'},
        sort_by=[],
        style_cell={'font-size': 13, 'font-family':'Avenir, sans-serif', 'height': "25px"},
        style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                }
            ],
        style_header={
            "backgroundColor": "rgb(213,86,81)",
            "color": "white",
            "textAlign": "center",
            'font-family':'Avenir, sans-serif'
        }
    )
    elif value == "USA":
        year = locationData["points"][0]["customdata"][0]
        location = locationData["points"][0]["location"]
        filtered_df = all_performances[
            (all_performances["workTitle"] == worktitle_name) & (all_performances["year"] == year) & (
                        all_performances["State"] == location)].drop_duplicates()
        return dash_table.DataTable(
            columns=[
                {'name': i, 'id': i, 'deletable': True} for i in
                ['Venue', 'eventType', 'id', 'composerName', 'conductorName', 'movement',
                 'workTitle', 'soloistInstrument', 'soloistName', 'programID',
                 'orchestra', 'year', 'month', 'day', 'Country', 'City', 'State',
                 'startingHour', 'startingMinute', 'paperProgram', 'seasonOfYear',
                 'geocode']
            ],
            page_current=0,
            page_size=TABLE_PAGE_SIZE,
            data=filtered_df.to_dict('records'),
            page_action='native',
            sort_action='native',
            sort_mode='single',
            style_table={'overflowX': 'scroll'},
            sort_by=[],
            style_cell={'font-size': 13, 'font-family': 'Avenir, sans-serif', 'height': "25px"},
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                }
            ],
            style_header={
                "backgroundColor": "rgb(213,86,81)",
                "color": "white",
                "textAlign": "center",
                'font-family': 'Avenir, sans-serif'
            }
        )


@app.callback(Output("venue-table", "children"),
              [Input("venue-bar", "clickData")],
              [State('location-dropdown', 'value'),
               State("location-graph", "clickData")]
              )
def create_venue_table(clickData, value, locationData):
    venue_name = clickData['points'][0]['y']
    if value == "World":
        year = locationData["points"][0]["customdata"][0]
        location = locationData["points"][0]["location"]
        filtered_df = all_performances[(all_performances["Venue"] == venue_name) & (all_performances["year"] == year) & (all_performances["geocode"] == location)].drop_duplicates()
        return dash_table.DataTable(
        columns=[
            {'name': i, 'id': i, 'deletable': True} for i in ['Venue', 'eventType', 'id', 'composerName', 'conductorName', 'movement',
       'workTitle', 'soloistInstrument', 'soloistName', 'programID',
       'orchestra', 'year', 'month', 'day', 'Country', 'City', 'State',
       'startingHour', 'startingMinute', 'paperProgram', 'seasonOfYear',
       'geocode']
        ],
        page_current=0,
        page_size=TABLE_PAGE_SIZE,
        data=filtered_df.to_dict('records'),
        page_action='native',
        sort_action='native',
        sort_mode='single',
        style_table={'overflowX': 'scroll'},
        sort_by=[],
        style_cell={'font-size': 13, 'font-family':'Avenir, sans-serif', 'height': "25px"},
        style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                }
            ],
        style_header={
            "backgroundColor": "rgb(213,86,81)",
            "color": "white",
            "textAlign": "center",
            'font-family':'Avenir, sans-serif'
        }
    )
    elif value == "USA":
        year = locationData["points"][0]["customdata"][0]
        location = locationData["points"][0]["location"]
        filtered_df = all_performances[
            (all_performances["Venue"] == venue_name) & (all_performances["year"] == year) & (
                        all_performances["State"] == location)].drop_duplicates()
        return dash_table.DataTable(
            columns=[
                {'name': i, 'id': i, 'deletable': True} for i in
                ['Venue', 'eventType', 'id', 'composerName', 'conductorName', 'movement',
                 'workTitle', 'soloistInstrument', 'soloistName', 'programID',
                 'orchestra', 'year', 'month', 'day', 'Country', 'City', 'State',
                 'startingHour', 'startingMinute', 'paperProgram', 'seasonOfYear',
                 'geocode']
            ],
            page_current=0,
            page_size=TABLE_PAGE_SIZE,
            data=filtered_df.to_dict('records'),
            page_action='native',
            sort_action='native',
            sort_mode='single',
            style_table={'overflowX': 'scroll'},
            sort_by=[],
            style_cell={'font-size': 13, 'font-family': 'Avenir, sans-serif', 'height': "25px"},
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                }
            ],
            style_header={
                "backgroundColor": "rgb(213,86,81)",
                "color": "white",
                "textAlign": "center",
                'font-family': 'Avenir, sans-serif'
            }
        )


@app.callback(Output("soloist-table", "children"),
              [Input("soloist-bar", "clickData")],
              [State('location-dropdown', 'value'),
               State("location-graph", "clickData")]
              )
def create_soloist_table(clickData, value, locationData):
    soloist_name = clickData['points'][0]['y']
    if value == "World":
        year = locationData["points"][0]["customdata"][0]
        location = locationData["points"][0]["location"]
        filtered_df = all_performances[(all_performances["soloistName"] == soloist_name) & (all_performances["year"] == year) & (all_performances["geocode"] == location)].drop_duplicates()
        return dash_table.DataTable(
        columns=[
            {'name': i, 'id': i, 'deletable': True} for i in ['Venue', 'eventType', 'id', 'composerName', 'conductorName', 'movement',
       'workTitle', 'soloistInstrument', 'soloistName', 'programID',
       'orchestra', 'year', 'month', 'day', 'Country', 'City', 'State',
       'startingHour', 'startingMinute', 'paperProgram', 'seasonOfYear',
       'geocode']
        ],
        page_current=0,
        page_size=TABLE_PAGE_SIZE,
        data=filtered_df.to_dict('records'),
        page_action='native',
        sort_action='native',
        sort_mode='single',
        style_table={'overflowX': 'scroll'},
        sort_by=[],
        style_cell={'font-size': 13, 'font-family':'Avenir, sans-serif', 'height': "25px"},
        style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                }
            ],
        style_header={
            "backgroundColor": "rgb(213,86,81)",
            "color": "white",
            "textAlign": "center",
            'font-family':'Avenir, sans-serif'
        }
    )
    elif value == "USA":
        year = locationData["points"][0]["customdata"][0]
        location = locationData["points"][0]["location"]
        filtered_df = all_performances[
            (all_performances["soloistName"] == soloist_name) & (all_performances["year"] == year) & (
                        all_performances["State"] == location)].drop_duplicates()
        return dash_table.DataTable(
            columns=[
                {'name': i, 'id': i, 'deletable': True} for i in
                ['Venue', 'eventType', 'id', 'composerName', 'conductorName', 'movement',
                 'workTitle', 'soloistInstrument', 'soloistName', 'programID',
                 'orchestra', 'year', 'month', 'day', 'Country', 'City', 'State',
                 'startingHour', 'startingMinute', 'paperProgram', 'seasonOfYear',
                 'geocode']
            ],
            page_current=0,
            page_size=TABLE_PAGE_SIZE,
            data=filtered_df.to_dict('records'),
            page_action='native',
            sort_action='native',
            sort_mode='single',
            style_table={'overflowX': 'scroll'},
            sort_by=[],
            style_cell={'font-size': 13, 'font-family': 'Avenir, sans-serif', 'height': "25px"},
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                }
            ],
            style_header={
                "backgroundColor": "rgb(213,86,81)",
                "color": "white",
                "textAlign": "center",
                'font-family': 'Avenir, sans-serif'
            }
        )


@app.callback(Output("orchestra-table", "children"),
              [Input("orchestra-bar", "clickData")],
              [State('location-dropdown', 'value'),
               State("location-graph", "clickData")]
              )
def create_orchestra_table(clickData, value, locationData):
    orchestra_name = clickData['points'][0]['y']
    if value == "World":
        year = locationData["points"][0]["customdata"][0]
        location = locationData["points"][0]["location"]
        filtered_df = all_performances[(all_performances["orchestra"] == orchestra_name) & (all_performances["year"] == year) & (all_performances["geocode"] == location)].drop_duplicates()
        return dash_table.DataTable(
        columns=[
            {'name': i, 'id': i, 'deletable': True} for i in ['Venue', 'eventType', 'id', 'composerName', 'conductorName', 'movement',
       'workTitle', 'soloistInstrument', 'soloistName', 'programID',
       'orchestra', 'year', 'month', 'day', 'Country', 'City', 'State',
       'startingHour', 'startingMinute', 'paperProgram', 'seasonOfYear',
       'geocode']
        ],
        page_current=0,
        page_size=TABLE_PAGE_SIZE,
        data=filtered_df.to_dict('records'),
        page_action='native',
        sort_action='native',
        sort_mode='single',
        style_table={'overflowX': 'scroll'},
        sort_by=[],
        style_cell={'font-size': 13, 'font-family':'Avenir, sans-serif', 'height': "25px"},
        style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                }
            ],
        style_header={
            "backgroundColor": "rgb(213,86,81)",
            "color": "white",
            "textAlign": "center",
            'font-family':'Avenir, sans-serif'
        }
    )
    elif value == "USA":
        year = locationData["points"][0]["customdata"][0]
        location = locationData["points"][0]["location"]
        filtered_df = all_performances[
            (all_performances["orchestra"] == orchestra_name) & (all_performances["year"] == year) & (
                        all_performances["State"] == location)].drop_duplicates()
        return dash_table.DataTable(
            columns=[
                {'name': i, 'id': i, 'deletable': True} for i in
                ['Venue', 'eventType', 'id', 'composerName', 'conductorName', 'movement',
                 'workTitle', 'soloistInstrument', 'soloistName', 'programID',
                 'orchestra', 'year', 'month', 'day', 'Country', 'City', 'State',
                 'startingHour', 'startingMinute', 'paperProgram', 'seasonOfYear',
                 'geocode']
            ],
            page_current=0,
            page_size=TABLE_PAGE_SIZE,
            data=filtered_df.to_dict('records'),
            page_action='native',
            sort_action='native',
            sort_mode='single',
            style_table={'overflowX': 'scroll'},
            sort_by=[],
            style_cell={'font-size': 13, 'font-family': 'Avenir, sans-serif', 'height': "25px"},
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                }
            ],
            style_header={
                "backgroundColor": "rgb(213,86,81)",
                "color": "white",
                "textAlign": "center",
                'font-family': 'Avenir, sans-serif'
            }
        )


@app.callback(Output("instrument-table", "children"),
              [Input("instrument-bar", "clickData")],
              [State('location-dropdown', 'value'),
               State("location-graph", "clickData")]
              )
def create_instrument_table(clickData, value, locationData):
    instrument_name = clickData['points'][0]['y']
    if value == "World":
        year = locationData["points"][0]["customdata"][0]
        location = locationData["points"][0]["location"]
        filtered_df = all_performances[(all_performances["soloistInstrument"] == instrument_name) & (all_performances["year"] == year) & (all_performances["geocode"] == location)].drop_duplicates()
        return dash_table.DataTable(
        columns=[
            {'name': i, 'id': i, 'deletable': True} for i in ['Venue', 'eventType', 'id', 'composerName', 'conductorName', 'movement',
       'workTitle', 'soloistInstrument', 'soloistName', 'programID',
       'orchestra', 'year', 'month', 'day', 'Country', 'City', 'State',
       'startingHour', 'startingMinute', 'paperProgram', 'seasonOfYear',
       'geocode']
        ],
        page_current=0,
        page_size=TABLE_PAGE_SIZE,
        data=filtered_df.to_dict('records'),
        page_action='native',
        sort_action='native',
        sort_mode='single',
        style_table={'overflowX': 'scroll'},
        sort_by=[],
        style_cell={'font-size': 13, 'font-family':'Avenir, sans-serif', 'height': "25px"},
        style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                }
            ],
        style_header={
            "backgroundColor": "rgb(213,86,81)",
            "color": "white",
            "textAlign": "center",
            'font-family':'Avenir, sans-serif'
        }
    )
    elif value == "USA":
        year = locationData["points"][0]["customdata"][0]
        location = locationData["points"][0]["location"]
        filtered_df = all_performances[
            (all_performances["soloistInstrument"] == instrument_name) & (all_performances["year"] == year) & (
                        all_performances["State"] == location)].drop_duplicates()
        return dash_table.DataTable(
            columns=[
                {'name': i, 'id': i, 'deletable': True} for i in
                ['Venue', 'eventType', 'id', 'composerName', 'conductorName', 'movement',
                 'workTitle', 'soloistInstrument', 'soloistName', 'programID',
                 'orchestra', 'year', 'month', 'day', 'Country', 'City', 'State',
                 'startingHour', 'startingMinute', 'paperProgram', 'seasonOfYear',
                 'geocode']
            ],
            page_current=0,
            page_size=TABLE_PAGE_SIZE,
            data=filtered_df.to_dict('records'),
            page_action='native',
            sort_action='native',
            sort_mode='single',
            style_table={'overflowX': 'scroll'},
            sort_by=[],
            style_cell={'font-size': 13, 'font-family': 'Avenir, sans-serif', 'height': "25px"},
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                }
            ],
            style_header={
                "backgroundColor": "rgb(213,86,81)",
                "color": "white",
                "textAlign": "center",
                'font-family': 'Avenir, sans-serif'
            }
        )


@app.callback(Output("season-table", "children"),
              [Input("season-bar", "clickData")],
              [State('location-dropdown', 'value'),
               State("location-graph", "clickData")]
              )
def create_season_table(clickData, value, locationData):
    season_name = clickData['points'][0]['y']
    if value == "World":
        year = locationData["points"][0]["customdata"][0]
        location = locationData["points"][0]["location"]
        filtered_df = all_performances[(all_performances["seasonOfYear"] == season_name) & (all_performances["year"] == year) & (all_performances["geocode"] == location)].drop_duplicates()
        return dash_table.DataTable(
        columns=[
            {'name': i, 'id': i, 'deletable': True} for i in ['Venue', 'eventType', 'id', 'composerName', 'conductorName', 'movement',
       'workTitle', 'soloistInstrument', 'soloistName', 'programID',
       'orchestra', 'year', 'month', 'day', 'Country', 'City', 'State',
       'startingHour', 'startingMinute', 'paperProgram', 'seasonOfYear',
       'geocode']
        ],
        page_current=0,
        page_size=TABLE_PAGE_SIZE,
        data=filtered_df.to_dict('records'),
        page_action='native',
        sort_action='native',
        sort_mode='single',
        style_table={'overflowX': 'scroll'},
        sort_by=[],
        style_cell={'font-size': 13, 'font-family':'Avenir, sans-serif', 'height': "25px"},
        style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                }
            ],
        style_header={
            "backgroundColor": "rgb(213,86,81)",
            "color": "white",
            "textAlign": "center",
            'font-family':'Avenir, sans-serif'
        }
    )
    elif value == "USA":
        year = locationData["points"][0]["customdata"][0]
        location = locationData["points"][0]["location"]
        filtered_df = all_performances[
            (all_performances["seasonOfYear"] == season_name) & (all_performances["year"] == year) & (
                        all_performances["State"] == location)].drop_duplicates()
        return dash_table.DataTable(
            columns=[
                {'name': i, 'id': i, 'deletable': True} for i in
                ['Venue', 'eventType', 'id', 'composerName', 'conductorName', 'movement',
                 'workTitle', 'soloistInstrument', 'soloistName', 'programID',
                 'orchestra', 'year', 'month', 'day', 'Country', 'City', 'State',
                 'startingHour', 'startingMinute', 'paperProgram', 'seasonOfYear',
                 'geocode']
            ],
            page_current=0,
            page_size=TABLE_PAGE_SIZE,
            data=filtered_df.to_dict('records'),
            page_action='native',
            sort_action='native',
            sort_mode='single',
            style_table={'overflowX': 'scroll'},
            sort_by=[],
            style_cell={'font-size': 13, 'font-family': 'Avenir, sans-serif', 'height': "25px"},
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                }
            ],
            style_header={
                "backgroundColor": "rgb(213,86,81)",
                "color": "white",
                "textAlign": "center",
                'font-family': 'Avenir, sans-serif'
            }
        )


if __name__ == '__main__':
    big_location_aggregation = dw.read_country_data().sort_values("year").reset_index(drop=True)
    big_location_aggregation_state = dw.read_state_data().sort_values("year").reset_index(drop=True)
    all_performances = dw.read_all_performances().sort_values("year").reset_index(drop=True)
    app.run_server(debug=False, port=5000, host='0.0.0.0')
