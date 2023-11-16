import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import base64
import io
import plotly.express as px

# Create the Dash application
app = dash.Dash(__name__)

# List of "Product line" options
product_line_options = [
    'Health and beauty',
    'Sports and travel',
    'Fashion accessories',
    'Home and lifestyle',
    'Food and beverages',
]

# List of "City" options
city_options = [
    'Yangon',
    'Mandalay',
    'Naypyitaw',
]

# Data source
data = None  # Initially, the data is empty

# Layout of the dashboard with tabs
app.layout = html.Div([
    dcc.Store(id='data-store'), 
     dcc.Tabs([
        dcc.Tab(label='Dashboard 1', children=[
            html.Div([
                html.Div([
                    dcc.Upload(
                        id='upload-data',
                        children=[
                            'Drag and drop or ',
                            html.A('select a CSV file'),
                        ],
                        style={
                            'width': '150px',
                            'padding': '5px 10px',
                            'border': '2px solid gray',
                            'border-radius': '3px',
                            'cursor': 'pointer',
                            'font-size': '14px',
                            'background-color': 'lightgray',
                            'color': 'black',
                        },
                        multiple=False
                    ),
                ], style={'display': 'flex', 'justify-content': 'space-between'}),

                # Division for dropdown menus
                html.Div([
                    # Dropdown menu for "Product line"
                    dcc.Dropdown(
                        id='product-line-dropdown',
                        options=[{'label': pl, 'value': pl} for pl in product_line_options],
                        value='Health and beauty',
                        style={'width': '220px'},
                    ),
                ], style={'width': '25%', 'display': 'inline-block', 'vertical-align': 'top'}),

                # Division for line chart
                html.Div([
                    dcc.Graph(id='line-chart'),
                ]),

                # Division for bar charts and map
                html.Div([
                    # Division for bar charts
                    html.Div([
                        # Dropdown menu for "City" (above bar charts but not at the top)
                        dcc.Dropdown(
                            id='city-dropdown',
                            options=[{'label': city, 'value': city} for city in city_options],
                            value='Yangon',
                            style={'width': '220px'},
                        ),

                        # Bar chart for total gross income by Product line
                        dcc.Graph(id='bar-chart-product-line'),

                        # Bar chart for total gross income by City
                        dcc.Graph(id='bar-chart-city'),
                    ], style={'width': '45%', 'display': 'inline-block', 'vertical-align': 'top'}),

                    # Division for the map
                    html.Div([
                        dcc.Graph(id='map-chart'),
                    ], style={'width': '35%', 'display': 'inline-block', 'vertical-align': 'top'}),
                ], style={'display': 'flex'}),
            ]),
        ]),
        dcc.Tab(label='Dashboard 2', children=[
            html.Div([
                html.Div([
                    dcc.Dropdown(
                        id='product-line-dropdown-2',
                        options=[{'label': pl, 'value': pl} for pl in product_line_options],
                        value='Health and beauty',
                        style={'width': '50%'}
                    ),
                    dcc.Graph(id='pie-chart')
                ], style={'display': 'inline-block', 'width': '50%'}),

                html.Div([
                    dcc.Dropdown(
                        id='city-dropdown-2',
                        options=[{'label': city, 'value': city} for city in city_options],
                        value='Yangon',
                        style={'width': '50%'}
                    ),
                    dcc.Graph(id='payment-count')
                ], style={'display': 'inline-block', 'width': '50%'}),

                html.Div([
                    dcc.Graph(id='gross-margin-bar')
                ], style={'width': '100%'})
            ]),
        ]),
    ]),
])

@app.callback(
    [Output('line-chart', 'figure'),
     Output('map-chart', 'figure'),
     Output('bar-chart-product-line', 'figure'),
     Output('bar-chart-city', 'figure')],
    [Input('upload-data', 'contents'),
     Input('product-line-dropdown', 'value'),
     Input('city-dropdown', 'value')],
    prevent_initial_call=True
)
def update_charts(contents, selected_product_line, selected_city):
    global data  # Access the global data variable

    if contents is None:
        raise dash.exceptions.PreventUpdate

    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    data = pd.read_csv(io.StringIO(decoded.decode('utf-8')))

    data['Date'] = pd.to_datetime(data['Date'])
    data = data.sort_values('Date')

    line_fig = go.Figure()

    filtered_data = data[data['Product line'] == selected_product_line]
    grouped_data = filtered_data.groupby('Date')['gross income'].sum().reset_index()
    line_fig.add_trace(go.Scatter(x=grouped_data['Date'], y=grouped_data['gross income'], mode='lines', name=selected_product_line))

    line_fig.update_layout(
        title=f'Sales in the {selected_product_line} department',
        xaxis_title='Date',
        yaxis_title='Total'
    )

    map_fig = go.Figure()

    grouped_data = filtered_data.groupby(['Latitude', 'Longitude', 'City'])['gross income'].sum().reset_index()
    grouped_data['gross income'] = grouped_data['gross income'].round(2)

    for _, row in grouped_data.iterrows():
        city = row['City']
        total = row['gross income']
        color = '#63feb9'  # Default color

        if city == 'Mandalay':
            color = '#E9967A'
        elif city == 'Naypyitaw':
            color = '#E9967A'
        elif city == 'Yangon':
            color = '#E9967A'

        size = max(15, total / 200)  # Adjust the size calculation as needed

        map_fig.add_trace(go.Scattermapbox(
            lat=[row['Latitude']],
            lon=[row['Longitude']],
            mode='markers+text',
            marker=dict(
                size=size,
                color=color,
                opacity=0.7  # Set marker opacity to 50%
            ),
            text=f'{city}: {total}',  # Label with city name and total
            name=city,  # City name for legend
            hoverinfo='text'
        ))

    map_fig.update_layout(
        title=f'Presence in the country',
        showlegend=False,  # Remove the legend from the map
        mapbox_style="open-street-map",
        mapbox_center={"lat": filtered_data['Latitude'].mean(), "lon": filtered_data['Longitude'].mean()},
        mapbox_zoom=5,
        width=800,
        height=920,
    )

    # Bar chart for total gross income by Product line
    filtered_data_bar_product_line = data[data['City'] == selected_city].dropna(subset=['Product line', 'gross income'])
    bar_fig_product_line = go.Figure()

    # Sort categories by descending total
    sorted_categories_product_line = filtered_data_bar_product_line.groupby('Product line')['gross income'].sum().sort_values(ascending=False).index

    for product_line in sorted_categories_product_line:
        filtered_data_line_product_line = filtered_data_bar_product_line[filtered_data_bar_product_line['Product line'] == product_line]
        total_income_product_line = filtered_data_line_product_line['gross income'].sum()
        bar_fig_product_line.add_trace(go.Bar(x=[product_line], y=[total_income_product_line], name=product_line))

    bar_fig_product_line.update_layout(
        title=f'Gross income by product line in {selected_city}',
        xaxis_title='Product line',
        yaxis_title='Gross income'
    )

    # Bar chart for total gross income by City
    filtered_data_bar_city = data.groupby('City')['gross income'].sum().reset_index()
    bar_fig_city = go.Figure()

    # Define custom colors for each city
    colors = {'Yangon': '#F5BBBB', 'Mandalay': '#D4ECA0', 'Naypyitaw': '#B8D2E9'}

    bar_fig_city.add_trace(go.Bar(
        x=filtered_data_bar_city['City'],
        y=filtered_data_bar_city['gross income'],
        marker=dict(
            color=[colors[city] for city in filtered_data_bar_city['City']]  # Assign colors based on city
        )
    ))

    bar_fig_city.update_layout(
        title='Gross income by city',
        xaxis_title='City',
        yaxis_title='Gross income'
    )

    return line_fig, map_fig, bar_fig_product_line, bar_fig_city

@app.callback(
    Output('pie-chart', 'figure'),
    Input('product-line-dropdown-2', 'value')
)
def update_pie_chart(selected_product_line):
    try:
        if data is None:
            raise dash.exceptions.PreventUpdate  # Prevent callback execution if data is None

        if 'Gender' not in data.columns:
            fig = go.Figure(data=[], layout={})
            return fig

        filtered_data = data[data['Product line'] == selected_product_line]
        gender_counts = filtered_data['Gender'].value_counts()
        total_count = gender_counts.sum()
        gender_percentages = {gender: count / total_count * 100 for gender, count in gender_counts.items()}

        fig = px.pie(values=list(gender_percentages.values()),
                     names=list(gender_percentages.keys()),
                     title=f"Distribution of Gender in {selected_product_line}")

        fig.update_traces(marker=dict(colors=['#DBADD0', '#778BDB']))

        return fig
    except Exception as e:
        return go.Figure(data=[], layout={})

@app.callback(
    Output('payment-count', 'figure'),
    Input('city-dropdown-2', 'value')
)
def update_payment_count(selected_city):
    try:
        if data is None:
            raise dash.exceptions.PreventUpdate  # Prevent callback execution if data is None

        filtered_data = data[data['City'] == selected_city]
        payment_counts = filtered_data['Payment'].value_counts()

        fig = px.bar(
            x=payment_counts.index,
            y=payment_counts.values,
            labels={'x': 'Payment Method', 'y': 'Count'},
            title=f"Payment Method Distribution in {selected_city}"
        )

        return fig
    except Exception as e:
        return go.Figure(data=[], layout={})

@app.callback(
    Output('gross-margin-bar', 'figure'),
    Input('product-line-dropdown-2', 'value'),
    Input('city-dropdown-2', 'value')
)
def update_gross_margin_bar(selected_product_line, selected_city):
    try:
        if data is None:
            raise dash.exceptions.PreventUpdate  # Prevent callback execution if data is None

        filtered_data = data[(data['Product line'] == selected_product_line) & (data['City'] == selected_city)]

        fig = px.bar(
            x=filtered_data['Date'],
            y=filtered_data['gross margin'],
            labels={'x': 'Date', 'y': 'Gross Margin'},
            title=f"Gross Margin for {selected_product_line} in {selected_city}"
        )

        return fig
    except Exception as e:
        return go.Figure(data=[], layout={})

if __name__ == '__main__':
    app.run_server(debug=True, port=8051)
