import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import data_wrangling as dw
import plotly.express as px
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import json


# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__)

# print(big_location_aggregation.head(5))

# df = pd.read_csv(
#     'https://gist.githubusercontent.com/chriddyp/'
#     'cb5392c35661370d95f300086accea51/raw/'
#     '8e0768211f6b747c0db42a9ce9a0937dafcbd8b2/'
#     'indicators.csv')

# available_indicators = df['Indicator Name'].unique()

app.layout = html.Div([

    html.Div([
        html.Div([
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
            ], style={"width": "50%", "display": "inline-block"}),
            # html.Div([dcc.Loading(dcc.Graph(id="example-graph", config={
            #                     'displayModeBar': False
            #                      }))], style={"width": "40%", "display": "inline-block"})
        ], style={"width": "100%"})

])


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


@app.callback(Output("example-graph", "figure"),
              [Input('location-dropdown', 'value')])
def make_example_figure(value):
    if value == "World":
        composer_events = all_performances.groupby('composerName')['programID'].nunique().reset_index(name="count").sort_values(
            by='count', ascending=True).tail(20)
        fig = px.bar(composer_events, x="count", y="composerName", orientation='h',
                     title='Number of Events by Composer (top 20)')
        fig.update_layout(xaxis_type="log")
        return fig



@app.callback(Output("placeholder-text", 'children'),
              [Input("location-graph", "clickData")])
def show_clickdata(data):
    return json.dumps(data)



# app.layout = html.Div([
#     html.Div([
#
#         html.Div([
#             dcc.Dropdown(
#                 id='crossfilter-xaxis-column',
#                 options=[{'label': i, 'value': i} for i in available_indicators],
#                 value='Fertility rate, total (births per woman)'
#             ),
#             dcc.RadioItems(
#                 id='crossfilter-xaxis-type',
#                 options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
#                 value='Linear',
#                 labelStyle={'display': 'inline-block'}
#             )
#         ],
#         style={'width': '49%', 'display': 'inline-block'}),
#
#         html.Div([
#             dcc.Dropdown(
#                 id='crossfilter-yaxis-column',
#                 options=[{'label': i, 'value': i} for i in available_indicators],
#                 value='Life expectancy at birth, total (years)'
#             ),
#             dcc.RadioItems(
#                 id='crossfilter-yaxis-type',
#                 options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
#                 value='Linear',
#                 labelStyle={'display': 'inline-block'}
#             )
#         ], style={'width': '49%', 'float': 'right', 'display': 'inline-block'})
#     ], style={
#         'borderBottom': 'thin lightgrey solid',
#         'backgroundColor': 'rgb(250, 250, 250)',
#         'padding': '10px 5px'
#     }),
#
#     html.Div([
#         dcc.Graph(
#             id='crossfilter-indicator-scatter',
#             hoverData={'points': [{'customdata': 'Japan'}]}
#         )
#     ], style={'width': '49%', 'display': 'inline-block', 'padding': '0 20'}),
#     html.Div([
#         dcc.Graph(id='x-time-series'),
#         dcc.Graph(id='y-time-series'),
#     ], style={'display': 'inline-block', 'width': '49%'}),
#
#     html.Div(dcc.Slider(
#         id='crossfilter-year--slider',
#         min=df['Year'].min(),
#         max=df['Year'].max(),
#         value=df['Year'].max(),
#         marks={str(year): str(year) for year in df['Year'].unique()}
#     ), style={'width': '49%', 'padding': '0px 20px 20px 20px'})
# ])
#
#
# @app.callback(
#     dash.dependencies.Output('crossfilter-indicator-scatter', 'figure'),
#     [dash.dependencies.Input('crossfilter-xaxis-column', 'value'),
#      dash.dependencies.Input('crossfilter-yaxis-column', 'value'),
#      dash.dependencies.Input('crossfilter-xaxis-type', 'value'),
#      dash.dependencies.Input('crossfilter-yaxis-type', 'value'),
#      dash.dependencies.Input('crossfilter-year--slider', 'value')])
# def update_graph(xaxis_column_name, yaxis_column_name,
#                  xaxis_type, yaxis_type,
#                  year_value):
#     dff = df[df['Year'] == year_value]
#
#     return {
#         'data': [go.Scatter(
#             x=dff[dff['Indicator Name'] == xaxis_column_name]['Value'],
#             y=dff[dff['Indicator Name'] == yaxis_column_name]['Value'],
#             text=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name'],
#             customdata=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name'],
#             mode='markers',
#             marker={
#                 'size': 15,
#                 'opacity': 0.5,
#                 'line': {'width': 0.5, 'color': 'white'}
#             }
#         )],
#         'layout': go.Layout(
#             xaxis={
#                 'title': xaxis_column_name,
#                 'type': 'linear' if xaxis_type == 'Linear' else 'log'
#             },
#             yaxis={
#                 'title': yaxis_column_name,
#                 'type': 'linear' if yaxis_type == 'Linear' else 'log'
#             },
#             margin={'l': 40, 'b': 30, 't': 10, 'r': 0},
#             height=450,
#             hovermode='closest'
#         )
#     }
#
#
# def create_time_series(dff, axis_type, title):
#     return {
#         'data': [go.Scatter(
#             x=dff['Year'],
#             y=dff['Value'],
#             mode='lines+markers'
#         )],
#         'layout': {
#             'height': 225,
#             'margin': {'l': 20, 'b': 30, 'r': 10, 't': 10},
#             'annotations': [{
#                 'x': 0, 'y': 0.85, 'xanchor': 'left', 'yanchor': 'bottom',
#                 'xref': 'paper', 'yref': 'paper', 'showarrow': False,
#                 'align': 'left', 'bgcolor': 'rgba(255, 255, 255, 0.5)',
#                 'text': title
#             }],
#             'yaxis': {'type': 'linear' if axis_type == 'Linear' else 'log'},
#             'xaxis': {'showgrid': False}
#         }
#     }
#
#
# @app.callback(
#     dash.dependencies.Output('x-time-series', 'figure'),
#     [dash.dependencies.Input('crossfilter-indicator-scatter', 'hoverData'),
#      dash.dependencies.Input('crossfilter-xaxis-column', 'value'),
#      dash.dependencies.Input('crossfilter-xaxis-type', 'value')])
# def update_y_timeseries(hoverData, xaxis_column_name, axis_type):
#     country_name = hoverData['points'][0]['customdata']
#     dff = df[df['Country Name'] == country_name]
#     dff = dff[dff['Indicator Name'] == xaxis_column_name]
#     title = '<b>{}</b><br>{}'.format(country_name, xaxis_column_name)
#     return create_time_series(dff, axis_type, title)
#
#
# @app.callback(
#     dash.dependencies.Output('y-time-series', 'figure'),
#     [dash.dependencies.Input('crossfilter-indicator-scatter', 'hoverData'),
#      dash.dependencies.Input('crossfilter-yaxis-column', 'value'),
#      dash.dependencies.Input('crossfilter-yaxis-type', 'value')])
# def update_x_timeseries(hoverData, yaxis_column_name, axis_type):
#     dff = df[df['Country Name'] == hoverData['points'][0]['customdata']]
#     dff = dff[dff['Indicator Name'] == yaxis_column_name]
#     return create_time_series(dff, axis_type, yaxis_column_name)


if __name__ == '__main__':
    big_location_aggregation = dw.read_country_data().sort_values("year").reset_index(drop=True)
    big_location_aggregation_state = dw.read_state_data().sort_values("year").reset_index(drop=True)
    all_performances = dw.read_all_performances().sort_values("year").reset_index(drop=True)
    app.run_server(debug=True)
