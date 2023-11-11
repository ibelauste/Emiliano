import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import base64
import io
import os

# Inicia la aplicación Dash con el nombre 'prueba'
prueba = dash.Dash(__name__)

server = app.server

# Variable global para almacenar los datos del CSV
global_data = None

# Nombre del archivo CSV para almacenar los datos
csv_filename = 'data.csv'

# Verifica si el archivo CSV ya existe, si no, crea uno vacío
if not os.path.exists(csv_filename):
    pd.DataFrame(columns=['Year', 'Global_Sales']).to_csv(csv_filename, index=False)

# Diseño del layout
prueba.layout = html.Div([
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

# Callback para cargar el archivo y actualizar el gráfico
@prueba.callback(Output('line-chart', 'figure'),
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

if __name__ == '__main__':
    prueba.run_server(debug=True, port=8051)

import dash
from dash import dcc, html, Input, Output
import pandas as pd
import base64
import io
import os

# Inicia la aplicación Dash con el nombre 'prueba'
prueba2 = dash.Dash(__name__)

# Variable global para almacenar los datos
global_data = None

# Rango de años deseado
year_range = list(range(1980, 2021))

# Nombre del archivo CSV para almacenar los datos
csv_filename = 'data.csv'

# Verifica si el archivo CSV ya existe, si no, crea uno vacío
if not os.path.exists(csv_filename):
    pd.DataFrame(columns=['Year', 'Global_Sales']).to_csv(csv_filename, index=False)

# Lee los datos del archivo CSV al inicio de la aplicación
global_data = pd.read_csv(csv_filename)

# Diseño del layout
prueba2.layout = html.Div([
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

# Callback para actualizar el gráfico de barras
@prueba2.callback(Output('bar-chart', 'figure'),
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

if __name__ == '__main__':
    prueba2.run_server(debug=True, port=8051)

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd
import base64
import io
import os

# Inicia la aplicación Dash con el nombre 'prueba'
app = dash.Dash(__name__)

# Nombre del archivo CSV para almacenar los datos
csv_filename = 'data.csv'

# Verifica si el archivo CSV ya existe, si no, crea uno vacío
if not os.path.exists(csv_filename):
    pd.DataFrame(columns=['Year', 'Global_Sales']).to_csv(csv_filename, index=False)

# Variable global para almacenar los datos del CSV
global_data = pd.read_csv(csv_filename)  # Cargar los datos iniciales desde el archivo CSV

# Nuevos colores personalizados
colors = ['#3fb5d8', '#996cc4', '#de96c0', '#abde98', '#f2be8a']

# Diseño del layout
app.layout = html.Div([
    dcc.Upload(
        id='upload-data',
        children=[
            html.Button('Selecciona tu archivo CSV', id='upload-button'),
            ' o arrastra y suelta.'
        ],
        multiple=False
    ),
    html.Div(id='output-data-upload'),
    dcc.Graph(id='sales-graph'),
    dcc.RangeSlider(
        id='year-slider',
        min=1980,
        max=2020,
        step=1,
        marks={i: str(i) for i in range(1980, 2021, 10)},
        value=[2000, 2020]  # Establece el rango inicial
    ),
    dcc.Checklist(
        id='genre-checklist',
        options=[
            {'label': 'Role-Playing', 'value': 'Role-Playing'},
            {'label': 'Racing', 'value': 'Racing'},
            {'label': 'Misc', 'value': 'Misc'},
            {'label': 'Sports', 'value': 'Sports'},
            {'label': 'Action', 'value': 'Action'},
            {'label': 'Shooter', 'value': 'Shooter'},
            {'label': 'Simulation', 'value': 'Simulation'},
            {'label': 'Platform', 'value': 'Platform'},
            {'label': 'Puzzle', 'value': 'Puzzle'}
            # Agrega más opciones según tus géneros
        ],
        value=['Shooter'],  # Valores predeterminados seleccionados
        style={'width': '150px'}  # Establece el ancho del menú desplegable
    ),
])

# Función para cargar el archivo CSV y procesar los datos
def parse_contents(contents, filename):
    global global_data

    if contents is None:
        return pd.DataFrame(columns=['Year', 'Global_Sales'])

    content_type, content_string = contents.split(',')

    # Decodifica el contenido base64 en datos binarios
    decoded = base64.b64decode(content_string)

    # Lee los datos del CSV
    new_data = pd.read_csv(io.StringIO(decoded.decode('utf-8')))

    # Guarda los nuevos datos en el archivo CSV
    updated_data = pd.concat([global_data, new_data], ignore_index=True)
    updated_data.to_csv(csv_filename, index=False)

    # Actualiza la variable global con los datos combinados
    global_data = updated_data

    return new_data

# Callback para actualizar el gráfico de dispersión
@app.callback(Output('sales-graph', 'figure'),
              [Input('year-slider', 'value'),
               Input('genre-checklist', 'value')])
def update_scatter_plot(year_range, selected_genres):
    # Utiliza la función load_data() para obtener los datos filtrados
    df = load_data(year_range, selected_genres)

    if df is not None:
        # Create figure
        fig = go.Figure()

        # Agrega una traza para cada género seleccionado
        for i, genre in enumerate(selected_genres):
            df_genre = df[df['Genre'] == genre]
            fig.add_trace(
                go.Scatter(x=df_genre['Year'], y=df_genre['Global_Sales'],
                           mode='lines+markers', name=f'{genre}',
                           line=dict(color=colors[i]))
            )

        # Set title
        fig.update_layout(
            title_text=f'Ventas globales de juegos a lo largo del tiempo'
        )

        return fig
    else:
        return go.Figure()

# Función para cargar los datos directamente desde el DataFrame global
def load_data(year_range, selected_genres):
    global global_data

    # Filtra los datos para incluir solo juegos de los géneros seleccionados dentro del rango de años seleccionado
    df_filtered = global_data[(global_data['Genre'].isin(selected_genres)) &
                              (global_data['Year'] >= year_range[0]) &
                              (global_data['Year'] <= year_range[1])]

    # Agrupa por año y suma las ventas globales
    df_aggregated = df_filtered.groupby(['Year', 'Genre'])['Global_Sales'].sum().reset_index()

    return df_aggregated

if __name__ == '__main__':
    app.run_server(debug=True, port=8051)

