import dash
from dash import dcc, html, Input, Output
import pandas as pd
import base64
import io
import os

# Inicia la aplicación Dash con el nombre 'dashboard_combinado'
app = dash.Dash(__name__)

server=app.server

# Variables globales
csv_filename = 'data_combined.csv'
year_range = list(range(1980, 2021))
global_data_combined = None

# Verifica si el archivo CSV ya existe, si no, crea uno vacío
if not os.path.exists(csv_filename):
    pd.DataFrame(columns=['Year', 'Global_Sales']).to_csv(csv_filename, index=False)

# Lee los datos del archivo CSV al inicio de la aplicación
global_data_combined = pd.read_csv(csv_filename)

# Diseño del layout
app.layout = html.Div([
    # Sección para cargar datos CSV
    dcc.Upload(
        id='upload-data',
        children=[
            html.Button('Selecciona tu archivo CSV', id='upload-button'),
            ' o arrastra y suelta.'
        ],
        multiple=False
    ),
    html.Div(id='output-data-upload'),

    # Sección para gráfico de línea
    dcc.Graph(id='line-chart'),

    # Sección para gráfico de barras y controles
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

# Callback para cargar el archivo y actualizar el gráfico de línea
@app.callback(Output('line-chart', 'figure'),
              [Input('upload-data', 'contents'),
               Input('upload-data', 'filename')])
def update_line_chart(contents, filename):
    global global_data_combined

    if contents is None:
        return dash.no_update

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
    global_data_combined = updated_data

    # Agrupa por año y suma las ventas globales
    df_grouped = global_data_combined.groupby('Year')['Global_Sales'].sum().reset_index()

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

# Callback para actualizar el gráfico de barras
@app.callback(Output('bar-chart', 'figure'),
              [Input('year-slider', 'value'),
               Input('sales-dropdown', 'value')])
def update_bar_chart(selected_year, selected_sales):
    global global_data_combined

    if selected_year is None or global_data_combined is None:
        return dash.no_update

    # Filtra los datos por el año seleccionado
    df_filtered = global_data_combined[global_data_combined['Year'] == selected_year]

    # Handle missing values, e.g., fill NaN with 0
    df_filtered[selected_sales] = df_filtered[selected_sales].fillna(0)

    # Ensure 'Genre' column exists in the filtered DataFrame
    if 'Genre' not in df_filtered.columns:
        return dash.no_update

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
    app.run_server(debug=True, port=8051)
