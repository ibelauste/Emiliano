import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import base64
import io
import os
import app

# Inicia la aplicación Dash con el nombre 'prueba'
app1 = dash.Dash(__name__)

# Variable global para almacenar los datos del CSV
global_data = None

# Nombre del archivo CSV para almacenar los datos
csv_filename = 'data.csv'

# Verifica si el archivo CSV ya existe, si no, crea uno vacío
if not os.path.exists(csv_filename):
    pd.DataFrame(columns=['Year', 'Global_Sales']).to_csv(csv_filename, index=False)

# Diseño del layout
app1.layout = html.Div([
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

if __name__ == '__main__':
    app1.run_server(debug=True, port=8051)


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
from dash import dcc, html, Input, Output
import pandas as pd
import os

# Inicia la aplicación Dash con el nombre 'prueba'
prueba2 = dash.Dash(__name__)

server = prueba2.server

# Variable global para almacenar los datos
global_data = None

# Rango de años deseado
year_range = list(range(1980, 2021))  # Ajusta el rango según tu necesidad

# Nombre del archivo CSV para almacenar los datos
csv_filename = 'data.csv'

# Verifica si el archivo CSV ya existe, si no, crea uno vacío
if not os.path.exists(csv_filename):
    pd.DataFrame(columns=['Year', 'Global_Sales']).to_csv(csv_filename, index=False)

# Lee los datos del archivo CSV al inicio de la aplicación
global_data = pd.read_csv(csv_filename)

# Diseño del layout
prueba2.layout = html.Div([
    dcc.Graph(id='time-series-chart'),
    dcc.Slider(
        id='year-slider',
        min=min(year_range),
        max=max(year_range),
        step=1,
        marks={i: str(i) for i in year_range},
        value=min(year_range)
    ),
    html.Div([
        dcc.Checklist(
            id='genre-checklist',
            options=[{'label': genre, 'value': genre} for genre in global_data['Genre'].unique()],
            value=global_data['Genre'].unique(),  # Puedes establecer un valor predeterminado aquí si lo deseas
            inline=True,
            style={'width': '200px'}
        ),
    ])
])

# Callback para actualizar el gráfico de series temporales
@prueba2.callback(Output('time-series-chart', 'figure'),
                 [Input('year-slider', 'value'),
                  Input('genre-checklist', 'value')])
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
    prueba2.run_server(debug=True, port=8051)


import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd
import base64
import io
import os

# Inicia la aplicación Dash
app2 = dash.Dash(__name__, suppress_callback_exceptions=True)

# Nombre del archivo CSV para almacenar los datos
csv_filename = 'data.csv'

# Verifica si el archivo CSV ya existe, si no, crea uno vacío
if not os.path.exists(csv_filename):
    pd.DataFrame(columns=['Year', 'Global_Sales']).to_csv(csv_filename, index=False)

# Variable global para almacenar los datos del CSV
global_data = pd.read_csv(csv_filename)  # Cargar los datos iniciales desde el archivo CSV

# Nuevos colores personalizados
colors = ['#FFFC8D', '#FFC489', '#FFA99F', '#E2E2E2', '#DCDCDC']

# Diseño del layout principal con pestañas
app2.layout = html.Div([
    dcc.Tabs(id='tabs', value='tab1', children=[
        dcc.Tab(label='Gráfico de Línea', value='tab1'),
        dcc.Tab(label='Gráfico de Barras', value='tab2'),
        dcc.Tab(label='Gráfico de Semi Círculo', value='tab3'),  # Nueva pestaña
    ]),
    html.Div(id='tabs-content')
])

# Layout de la pestaña 3: Gráfico de Semi Círculo
layout_tab3 = html.Div([
    html.Div(id='output-data-upload'),
    dcc.Graph(id='sales-graph'),
    dcc.Dropdown(
        id='platform-dropdown',
        options=[{'label': platform, 'value': platform} for platform in global_data['Platform'].unique()],
        value=global_data['Platform'].unique()[0],  # Valor predeterminado seleccionado
        style={'width': '150px'}  # Establece el ancho del menú desplegable
    ),
])

# Callback para actualizar el gráfico de semi círculo (gauge)
@app2.callback(Output('sales-graph', 'figure'),
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

# Callback para cambiar entre pestañas
@app2.callback(Output('tabs-content', 'children'),
              [Input('tabs', 'value')])
def update_tab(selected_tab):
    if selected_tab == 'tab1':
        return layout_tab1
    elif selected_tab == 'tab2':
        return layout_tab2
    elif selected_tab == 'tab3':
        return layout_tab3

if __name__ == '__main__':
    app2.run_server(debug=True, port=8051)


_______________________________________________________________________________

import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd
import base64
import io
import os

# Inicia la aplicación Dash
app = dash.Dash(__name__, suppress_callback_exceptions=True)


app=app.server


# Nombre del archivo CSV para almacenar los datos
csv_filename = 'data.csv'

# Verifica si el archivo CSV ya existe, si no, crea uno vacío
if not os.path.exists(csv_filename):
    pd.DataFrame(columns=['Year', 'Global_Sales']).to_csv(csv_filename, index=False)

# Variable global para almacenar los datos del CSV
global_data = pd.read_csv(csv_filename)  # Cargar los datos iniciales desde el archivo CSV

# Nuevos colores personalizados
colors = ['#FFFC8D', '#FFC489', '#FFA99F', '#E2E2E2', '#DCDCDC']

# Diseño del layout principal con pestañas
app.layout = html.Div([
    dcc.Tabs(id='tabs', value='tab1', children=[
        dcc.Tab(label='Gráfico de Línea', value='tab1'),
        dcc.Tab(label='Gráfico de Barras', value='tab2'),
        dcc.Tab(label='Gráfico de Series Temporales', value='tab3'),
        dcc.Tab(label='Gráfico de Semi Círculo', value='tab4'),
    ]),
    html.Div(id='tabs-content')
])

# Layout de la pestaña 1: Gráfico de Línea
layout_tab1 = html.Div([
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


# Callback para cargar el archivo y actualizar el gráfico de línea
# ...

# Callback para cargar el archivo y actualizar el gráfico de línea
@app.callback(Output('line-chart', 'figure'),
              [Input('upload-data', 'contents'),
               Input('upload-data', 'filename')])
def update_line_chart(contents, filename):
    global global_data

    if contents is None:
        return dash.no_update

    df_grouped = parse_contents(contents, filename)

    # Suma las ventas globales por año
    df_sum_by_year = df_grouped.groupby('Year')['Global_Sales'].sum().reset_index()

    # Crea el gráfico de línea
    fig = {
        'data': [
            {'x': df_sum_by_year['Year'], 'y': df_sum_by_year['Global_Sales'], 'type': 'line', 'name': 'Global Sales'},
        ],
        'layout': {
            'title': f'Suma de Ventas Globales por Año ({filename})',
            'xaxis': {'title': 'Año'},
            'yaxis': {'title': 'Ventas Globales'}
        }
    }

    return fig

# Función para procesar el contenido del archivo CSV
# Función para procesar el contenido del archivo CSV
def parse_contents(contents, filename):
    try:
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        # Asegúrate de que las columnas 'Year' y 'Global_Sales' existan en el DataFrame
        if 'Year' not in df.columns or 'Global_Sales' not in df.columns:
            print("Las columnas 'Year' y 'Global_Sales' no se encontraron en el archivo. Se usarán valores predeterminados.")
            df = pd.DataFrame(columns=['Year', 'Global_Sales'])
        return df
    except Exception as e:
        print(f"Error durante el análisis del archivo: {e}")
        return pd.DataFrame(columns=['Year', 'Global_Sales'])

# Layout de la pestaña 2: Gráfico de Barras
layout_tab2 = html.Div([
    dcc.Graph(id='bar-chart'),
    dcc.Slider(
        id='year-slider',
        min=int(min(global_data['Year'])),
        max=int(max(global_data['Year'])),
        step=1,
        marks={i: str(i) for i in range(int(min(global_data['Year'])), int(max(global_data['Year'])) + 1)},
        value=1980  # Establece el valor predeterminado en 1990
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


# Layout de la pestaña 3: Gráfico de Series Temporales
layout_tab3 = html.Div([
    dcc.Graph(id='time-series-chart'),
    dcc.Slider(
        id='year-slider-ts',
        min=int(min(global_data['Year'])),
        max=int(max(global_data['Year'])),
        step=1,
        marks={i: str(i) for i in range(int(min(global_data['Year'])), int(max(global_data['Year'])) + 1)},
        value=1990  # Establece el valor predeterminado en 1990
    ),
    html.Div([
        dcc.Checklist(
            id='genre-checklist',
            options=[{'label': genre, 'value': genre} for genre in global_data['Genre'].unique()],
            value=global_data['Genre'].unique(),  # Puedes establecer un valor predeterminado aquí si lo deseas
            inline=True,
            style={'width': '200px'}
        ),
    ])
])

# Callback para actualizar el gráfico de series temporales
@app.callback(Output('time-series-chart', 'figure'),
              [Input('year-slider-ts', 'value'),
               Input('genre-checklist', 'value')])
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

# Layout de la pestaña 4: Gráfico de Semi Círculo
layout_tab4 = html.Div([
    html.Div(id='output-data-upload'),
    dcc.Graph(id='sales-graph'),
    dcc.Dropdown(
        id='platform-dropdown',
        options=[{'label': platform, 'value': platform} for platform in global_data['Platform'].unique()],
        value=global_data['Platform'].unique()[0],  # Valor predeterminado seleccionado
        style={'width': '150px'}  # Establece el ancho del menú desplegable
    ),
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
                    axis=dict(range=[None, 30000]),
                    bar=dict(color=colors[3]),  # Cambia el color de la aguja
                    steps=[
                        {'range': [0, 15000], 'color': colors[0]},  # Verde hasta el 50%
                        {'range': [15000, 22500], 'color': colors[1]},  # Amarillo hasta el 80%
                        {'range': [22500, 30000], 'color': colors[2]}  # Naranja más allá del 80%
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

# Callback para cambiar entre pestañas
@app.callback(Output('tabs-content', 'children'),
              [Input('tabs', 'value')])
def update_tab(selected_tab):
    if selected_tab == 'tab1':
        return layout_tab1
    elif selected_tab == 'tab2':
        return layout_tab2
    elif selected_tab == 'tab3':
        return layout_tab3
    elif selected_tab == 'tab4':
        return layout_tab4

if __name__ == '__main__':
    app.run_server(debug=True, port=8051)
