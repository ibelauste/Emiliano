import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objects as go
import base64
import io
import os

# Inicia la aplicación Dash con el nombre 'prueba'
app = dash.Dash(__name__)

app=app.server

# Nombre del archivo CSV para almacenar los datos
csv_filename = 'data.csv'

# Verifica si el archivo CSV ya existe, si no, crea uno vacío
if not os.path.exists(csv_filename):
    pd.DataFrame(columns=['Global_Sales', 'Platform']).to_csv(csv_filename, index=False)

# Variable global para almacenar los datos del CSV
global_data = pd.read_csv(csv_filename)  # Cargar los datos iniciales desde el archivo CSV

# Nuevos colores personalizados
colors = ['#FFFC8D', '#FFC489', '#FFA99F', '#E2E2E2', '#DCDCDC']

# Rango de años deseado
year_range = list(range(1980, 2021))

# Opciones de género
Genre = ['Action', 'Adventure', 'Role-Playing', 'Sports', 'Shooter', 'Simulation', 'Strategy', 'Puzzle', 'Misc']

# Diseño del layout
app.layout = html.Div([
    dcc.Tabs(id='tabs', value='tab2', children=[
        dcc.Tab(label='Ventas 💹', value='tab2'),
        dcc.Tab(label='Presupuesto 💰', value='tab1'),
        dcc.Tab(label='Finanzas 💹', value='tab3'),
        dcc.Tab(label='Crédito 💹', value='tab4')
    ]),
    html.Div(id='tabs-content')
])

# Callback para cambiar entre las pestañas
@app.callback(Output('tabs-content', 'children'),
              [Input('tabs', 'value')])
def render_content(tab):
    if tab == 'tab1':
        return html.Div([
            dcc.Graph(id='sales-graph'),
            dcc.Dropdown(
                id='platform-dropdown',
                options=[{'label': str(platform), 'value': str(platform)} for platform in global_data['Platform'].unique()],
                value=global_data['Platform'].unique()[0],  # Valor predeterminado seleccionado
                style={'width': '150px'}  # Establece el ancho del menú desplegable
            )
        ])
    elif tab == 'tab2':
        return html.Div([
            dcc.Upload(
                id='upload-data',
                children=[
                    html.Button('Selecciona tu archivo CSV', id='upload-button'),
                    ' o arrastra y suelta.'
                ],
                multiple=False
            ),
            html.Div(id='output-data-upload'),
            dcc.Graph(id='line-chart')
        ])
    elif tab == 'tab3':
        return html.Div([
            dcc.Graph(id='bar-chart'),
            dcc.Slider(
                id='year-slider',
                min=min(year_range),
                max=max(year_range),
                step=1,
                marks={i: str(i) for i in year_range},
                value=min(year_range)
            ),
            dcc.Dropdown(
                id='sales-dropdown',
                options=[
                    {'label': 'Global_Sales', 'value': 'Global_Sales'},
                    {'label': 'NA_Sales', 'value': 'NA_Sales'},
                    {'label': 'EU_Sales', 'value': 'EU_Sales'},
                    {'label': 'JP_Sales', 'value': 'JP_Sales'},
                    {'label': 'Other_Sales', 'value': 'Other_Sales'}
                ],
                value='Global_Sales',
                multi=False,
                style={'width': '150px'}
            )
        ])
    elif tab == 'tab4':
        return html.Div([
            dcc.Graph(id='time-series-chart'),
            dcc.Slider(
                id='year-slider-ts',
                min=min(year_range),
                max=max(year_range),
                step=1,
                marks={i: str(i) for i in year_range},
                value=min(year_range)
            ),
            html.Div([
                dcc.Checklist(
                    id='genre-checklist-ts',
                    options=[{'label': genre, 'value': genre} for genre in Genre],
                    value=Genre,  # Puedes establecer un valor predeterminado aquí si lo deseas
                    inline=True,
                    style={'width': '200px'}
                ),
            ])
        ])

# Callback para actualizar el gráfico de semi círculo (gauge)
@app.callback(Output('sales-graph', 'figure'),
              [Input('platform-dropdown', 'value')])
def update_gauge_chart(selected_platform):
    # Utiliza la función load_data() para obtener los datos filtrados
    df = load_data(selected_platform)

    if df is not None:
        # Group by platform and sum global sales
        total_sales = df['Global_Sales'].sum()

        # Create figure
        fig = go.Figure()

        # Add gauge chart with needle
        fig.add_trace(
            go.Indicator(
                mode="number+gauge",
                value=total_sales,
                title={'text': f'Total de ventas globales para {selected_platform}'},
                                gauge=dict(
                    axis=dict(range=[None, 12000]),
                    bar=dict(color=colors[3]),  # Cambia el color de la aguja
                    steps=[
                        {'range': [0, 6000], 'color': colors[0]},  # Verde hasta el 50%
                        {'range': [6000, 9600], 'color': colors[1]},  # Amarillo hasta el 80%
                        {'range': [9600, 12000], 'color': colors[2]}  # Naranja más allá del 80%
                    ],
                )
            )
        )

        return fig
    else:
        return go.Figure()

# Función para cargar los datos directamente desde el DataFrame global
def load_data(selected_platform):
    global global_data

    # Filtra los datos para incluir solo juegos de la plataforma seleccionada
    df_filtered = global_data[global_data['Platform'] == selected_platform]

    return df_filtered

# Callback para cargar el archivo CSV y actualizar el gráfico de línea
@app.callback(Output('line-chart', 'figure'),
              [Input('upload-data', 'contents'),
               Input('upload-data', 'filename')])
def update_graph(contents, filename):
    global global_data

    if contents is None:
        return dash.no_update

    df_grouped = parse_contents(contents, filename)

    # Crea el gráfico de línea
    fig = {
        'data': [
            {'x': df_grouped['Year'], 'y': df_grouped['Global_Sales'], 'type': 'line', 'name': 'Global Sales'},
        ],
        'layout': {
            'title': 'Línea de tiempo de Ventas Globales',
            'xaxis': {'title': 'Año'},
            'yaxis': {'title': 'Ventas Globales'}
        }
    }

    return fig

# Función para cargar el archivo CSV y procesar los datos
def parse_contents(contents, filename):
    global global_data

    content_type, content_string = contents.split(',')

    # Decodifica el contenido base64 en datos binarios
    decoded = base64.b64decode(content_string)

    # Lee los datos del CSV
    new_data = pd.read_csv(io.StringIO(decoded.decode('utf-8')))

    # Guarda los nuevos datos en el archivo CSV
    current_data = pd.read_csv(csv_filename)
    updated_data = pd.concat([current_data, new_data], ignore_index=True)
    updated_data.to_csv(csv_filename, index=False)

    # Actualiza la variable global con los datos combinados
    global_data = updated_data

    # Agrupa por año y suma las ventas globales
    df_grouped = global_data.groupby('Year')['Global_Sales'].sum().reset_index()

    return df_grouped

# Callback para actualizar el gráfico de barras
@app.callback(Output('bar-chart', 'figure'),
              [Input('year-slider', 'value'),
               Input('sales-dropdown', 'value')])
def update_bar_chart(selected_year, selected_sales):
    global global_data

    if selected_year is None or global_data is None:
        return dash.no_update

    # Filtra los datos por el año seleccionado
    df_filtered = global_data[global_data['Year'] == selected_year]

    # Rellena los valores NA con 0
    df_filtered[selected_sales] = df_filtered[selected_sales].fillna(0)

    # Calcula la suma de las ventas por género
    df_sum_by_genre = df_filtered.groupby('Genre')[selected_sales].sum().reset_index()

    # Redondea los valores a 2 dígitos decimales
    df_sum_by_genre[selected_sales] = df_sum_by_genre[selected_sales].round(2)

    # Define los nuevos colores personalizados
    custom_colors = ['#6793ac', '#b0dbe0', '#e6f3cf', '#70af76', '#dcae7e']

    # Asigna los nuevos colores a cada barra
    bar_colors = [custom_colors[i % len(custom_colors)] for i in range(len(df_sum_by_genre['Genre']))]

    # Crea el gráfico de barras con tooltips y colores personalizados
    fig = {
        'data': [
            {
                'x': df_sum_by_genre['Genre'],
                'y': df_sum_by_genre[selected_sales],
                'type': 'bar',
                'name': selected_sales,
                'marker': {'color': bar_colors},
                'text': df_sum_by_genre[selected_sales].astype(str),
                'hoverinfo': 'x+text',
            },
        ],
        'layout': {
            'title': f'Ventas por Género en el Año {selected_year}',
            'xaxis': {'title': 'Género'},
            'yaxis': {'title': 'Ventas'},
            'bargap': 0.2,
            'bargroupgap': 0,
            'showdividers': 'hide'
        }
    }

    return fig

# Callback para actualizar el gráfico de series temporales
@app.callback(Output('time-series-chart', 'figure'),
              [Input('year-slider-ts', 'value'),
               Input('genre-checklist-ts', 'value')])
def update_time_series_chart(selected_year, selected_genres):
    global global_data

    if selected_year is None or global_data is None:
        return dash.no_update

    # Filtra los datos por el año seleccionado y géneros seleccionados
    df_filtered = global_data[(global_data['Year'] <= selected_year) & (global_data['Genre'].isin(selected_genres))]

    # Agrupa los datos por año y género, y calcula la suma de las ventas
    df_sum_by_year = df_filtered.groupby(['Year', 'Genre'])['Global_Sales'].sum().reset_index()

    # Redondea los valores a 2 dígitos decimales
    df_sum_by_year['Global_Sales'] = df_sum_by_year['Global_Sales'].round(2)

    # Crea el gráfico de series temporales
    fig = {
        'data': [
            {
                'x': df_sum_by_year[df_sum_by_year['Genre'] == genre]['Year'],
                'y': df_sum_by_year[df_sum_by_year['Genre'] == genre]['Global_Sales'],
                'type': 'line',
                'mode': 'lines+markers',
                'name': genre,
                'text': df_sum_by_year[df_sum_by_year['Genre'] == genre]['Global_Sales'].astype(str),
                'hoverinfo': 'x+text',
            } for genre in selected_genres
        ],
        'layout': {
            'title': 'Ventas de Géneros a lo largo del tiempo',
            'xaxis': {'title': 'Año'},
            'yaxis': {'title': 'Ventas'},
            'showdividers': 'hide'
        }
    }

    return fig

if __name__ == '__main__':
    app.run_server(debug=True, port=8051)

