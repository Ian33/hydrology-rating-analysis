# -*- coding: utf-8 -*-
"""
Created on Thu Sep  2 20:55:30 2021

@author: ianrh
"""
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pyodbc
import pandas as pd
import plotly.graph_objs as go
import webbrowser
from threading import Timer

#webbrowser.open("http://127.0.0.1:8050/")
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
#webbrowser.get("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s").open_new("http://127.0.0.1:8050/")
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
#webbrowser.get('chrome')
application = app.server
#webbrowser.get("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s").open_new("http://127.0.0.1:8050/")

# every query type needs its own connection string
conn_1 = pyodbc.connect('Driver={SQL Server};'
                      'Server=NRDOSQLPrX01;'
                      'Database=gData;'
                      'Trusted_Connection=yes;')

Available_Sites = pd.read_sql_query('select SITE_CODE, G_ID, FLOWLEVEL, STATUS from tblGaugeLLID;',conn_1)

Available_Sites = Available_Sites[Available_Sites['STATUS']=='Active']
print(Available_Sites)
#up is down, right is left, and false is true....
Available_Sites = Available_Sites[Available_Sites['FLOWLEVEL']== True]
Available_Sites.sort_values('SITE_CODE', inplace=True)
            #vlist.set_index('SITE_CODE', inplace=True)
vlist = Available_Sites['SITE_CODE'].values.tolist()
OFFSET_SQL = pd.read_sql_query('select Offset, Rating_Number from tblFlowRating_Stats;',conn_1)

df = pd.read_csv('https://plotly.github.io/datasets/country_indicators.csv')

available_indicators = Available_Sites['SITE_CODE'].unique()


app.layout = html.Div([
    html.Div([

        html.Div([
            #dcc.Dropdown(
            #    id='xaxis-column',
            #    options=[{'label': i, 'value': i} for i in available_indicators],
            #    value='0'
            #),
            dcc.Dropdown(
                id='Site',
                options=[{'label': i, 'value': i} for i in available_indicators],
                value='0'
            ),
            dcc.Dropdown(
                id='ratings',
                value='0'
            ),
            
            #dcc.RadioItems(
             #   id='xaxis-type',
              #  options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
               # value='Linear',
                #labelStyle={'display': 'inline-block'}
         #   ),
          dcc.RangeSlider(
          id='range_slider',
            min=0,
            max=100,
            step=1,
            value=[0, 100]
        ),
       #html.Div(id='output-container-range-slider')
            
            #dcc.Store(id='intermediate-value')

        ],
        style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            #dcc.Dropdown(
            #    id='yaxis-column',
            #    options=[{'label': i, 'value': i} for i in available_indicators],
            #    value='Life expectancy at birth, total (years)'
            #),
           # dcc.RadioItems(
            #    id='yaxis-type',
             #   options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
              #  value='Linear',
               # labelStyle={'display': 'inline-block'}
           # )
        ],style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
    ]),
    #html.Div(id='output-container-range-slider'),
    dcc.Graph(id='indicator-graphic'),

    #dcc.Slider(
    #    id='year--slider',
    #    min=df['Year'].min(),
    #    max=df['Year'].max(),
    #    value=df['Year'].max(),
    #    marks={str(year): str(year) for year in df['Year'].unique()},
    #    step=None
    #),
    #html.Div(id='slider-output-container'),
])


  


    
@app.callback(
    Output(component_id='ratings', component_property='options'),
    [Input(component_id='Site', component_property='value')]
)
def update_dp(value):
    
    search = Available_Sites.loc[Available_Sites['SITE_CODE'].isin([value])]
    G_ID_Lookup = search.iloc[0,1]
    
    ##G_Type = search.iloc[0,3]
    conn_3 = pyodbc.connect('Driver={SQL Server};'
                      'Server=NRDOSQLPrX01;'
                      'Database=gData;'
                      'Trusted_Connection=yes;')
    Rating_Number = pd.read_sql_query('select G_ID, RatingNumber from tblFlowRatings WHERE G_ID = '+str(G_ID_Lookup)+';',conn_3)
      
    Rating_Number.sort_values('RatingNumber', inplace=True)
            #vlist.set_index('SITE_CODE', inplace=True)
    available_ratings = Rating_Number['RatingNumber'].unique()
    
    # GET MEASUREMENT NUMBERS
    #conn_3B = pyodbc.connect('Driver={SQL Server};'
    #                  'Server=NRDOSQLPrX01;'
    #                  'Database=gData;'
    #                  'Trusted_Connection=yes;')
    #Field_OBS = pd.read_sql_query('Measurement_Number WHERE G_ID = '+str(G_ID_Lookup)+';',conn_3B)
    #min_rating = Field_OBS['Measurement_Number'].column.min()
    #max_rating = Field_OBS['Measurement_Number'].column.max()
    return [{'label': i, 'value': i} for i in available_ratings]
    #return max_rating
   # return min_rating

#@app.callback(
#    dash.dependencies.Output('slider-output-container', 'children'),
#    [dash.dependencies.Input('my-slider', 'value')])
#def update_output(value):
 #   return 'You have selected "{}"'.format(value)

@app.callback(
    Output('indicator-graphic', 'figure'),
    [Input('Site', 'value'),
     Input('ratings', 'value'),
     Input('range_slider', 'value')])
def update_graph(Site, ratings, range_slider):
    #dff = df[df['Year'] == year_value]
    search = Available_Sites.loc[Available_Sites['SITE_CODE'].isin([Site])]
    G_ID_Lookup = search.iloc[0,1]
    
    conn_4 = pyodbc.connect('Driver={SQL Server};'
                      'Server=NRDOSQLPrX01;'
                      'Database=gData;'
                      'Trusted_Connection=yes;')
    DF1 = pd.read_sql_query('select G_ID, RatingNumber, WaterLevel, Discharge from tblFlowRatings WHERE G_ID = '+str(G_ID_Lookup)+';',conn_4)
    DF1 = DF1[DF1['RatingNumber'] == str(ratings)]
    DF1.set_index('WaterLevel', inplace=True)
    DF1.sort_index(ascending=True, inplace=True)
    # not quite sure when this index got reset but this fixes it
    DF1.reset_index(inplace=True)
    
    ### FIELD OBSERVATIONS ###
    # Get all field observations #    
    DF1_PARAMETER_OBS = pd.read_sql_query('select G_ID, FieldVisit_ID, AutoDTStamp, Parameter, Parameter_Value from tblFieldData WHERE G_ID = '+str(G_ID_Lookup)+';',conn_4)
    # Filter for discharge observations for specific site #
    DF1_Site_Q = DF1_PARAMETER_OBS[DF1_PARAMETER_OBS['Parameter'] == 2].copy()
    
    # get stage and discharge
    DF1_Field_OBS = pd.read_sql_query('select Stage_Feet, Measurement_Number, FieldVisit_ID from tblFieldVisitInfo WHERE G_ID = '+str(G_ID_Lookup)+';',conn_4)
    DF1_FLOW_MATCHES = pd.merge(DF1_Field_OBS, DF1_Site_Q[['FieldVisit_ID', 'Parameter_Value']], on='FieldVisit_ID')
    
    range_min = range_slider[0] 
    range_max = range_slider[1] 
    
    
    
    
    LAST_MEASURE = DF1_FLOW_MATCHES
    ### GET last measurement
    DF1_FLOW_MATCHES = DF1_FLOW_MATCHES[DF1_FLOW_MATCHES['Measurement_Number'] >= range_min]
    DF1_FLOW_MATCHES = DF1_FLOW_MATCHES[DF1_FLOW_MATCHES['Measurement_Number'] <= range_max]
    
    
    LAST_MEASURE.dropna()
    LAST_MEASURE.set_index('Measurement_Number', inplace=True)
    print(LAST_MEASURE)
    LAST_MEASURE = LAST_MEASURE.tail(1)
    print(LAST_MEASURE)
    LAST_MEASURE.reset_index(inplace=True)
    print(LAST_MEASURE)
    DF1_FLOW_MATCHES.reset_index(inplace=True)
    
    DF1_FLOW_MATCHES['opacity']=DF1_FLOW_MATCHES.index/DF1_FLOW_MATCHES.index[-1]
    
    #GET OFFSET
    
    #OFFSET reads out with a bunch of extra blank spaces
    count = OFFSET_SQL.count()
    for i in range (0, count[1]):
        OFFSET_SQL['Rating_Number'].iloc[i] = OFFSET_SQL['Rating_Number'].iloc[i].strip()
    
    #filters OFFSET, since offset is stored with a bunch of blank spaces we cannot query buy rating number
    search_1 = OFFSET_SQL[OFFSET_SQL.Rating_Number == ratings]
    search_offset = search_1.iloc[0,0]
    DF1['WaterLevel'] = DF1['WaterLevel']+search_offset.astype(float)

    layout1 = go.Layout(width=1010, height=750, yaxis_title='Stage', plot_bgcolor='rgba(0,0,0,0)')
    fig = go.Figure(layout=layout1)

    fig.add_trace(go.Scatter(
                    x=DF1['Discharge'],
                    #x=DF58A['WaterLevel']+.3,
                    y=DF1['WaterLevel'],
                    line_color='Blue',
                    opacity=0.5,
                    name=str(ratings)))
    
    fig.add_trace(go.Scatter(
                    x=DF1['Discharge']*1.05,
                    #x=DF58A['WaterLevel']+.3,
                    y=DF1['WaterLevel'],
                    line_color='Blue',
                    opacity=0.1,
                    line=dict(dash='dash'),
                    name=str(ratings)))
    
    fig.add_trace(go.Scatter(
                    x=DF1['Discharge']-(DF1['Discharge']*.05),
                    #x=DF58A['WaterLevel']+.3,
                    y=DF1['WaterLevel'],
                    line_color='Blue',
                    opacity=0.1,
                    line=dict(dash='dash'),
                    name=str(ratings)))
    
    fig.add_trace(go.Scatter(
                    x=DF1_FLOW_MATCHES['Parameter_Value'],
                   # x=DF58F['WaterLevel']+.6,
                    #y=DF1_FLOW_MATCHES['Stage_Feet']-search_offset.astype(float),
                    y=DF1_FLOW_MATCHES['Stage_Feet'],
                    mode='markers',
                   marker=dict(
                            color='Blue',
                            size=5,
                            opacity=DF1_FLOW_MATCHES['opacity']),
                    text=DF1_FLOW_MATCHES['Measurement_Number'],
                    name="Site",  ))
                                 
    
    fig.add_trace(go.Scatter(
                    x=LAST_MEASURE['Parameter_Value'],
                   # x=DF58F['WaterLevel']+.6,
                    #y=LAST_MEASURE['Stage_Feet']-search_offset.astype(float),
                    y=LAST_MEASURE['Stage_Feet'],
                    mode='markers',
                   marker=dict(
                            color='Red',
                            size=6,
                            opacity=.9),
                    text='',
                    name="Last Measurement",  ))
    
    
    fig.update_xaxes(showline=True, linewidth=.5, linecolor='black', mirror=True)
    fig.update_yaxes(showline=True, linewidth=.5, linecolor='black', mirror=True)
    
    
    fig.update_layout(xaxis_type="log", yaxis_type="log")
    fig.update_xaxes(ticks="outside")
    fig.update_yaxes(ticks="outside")
    return fig
   


if __name__ == '__main__':
    app.run_server(debug=False, port=8080)