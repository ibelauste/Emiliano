import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import base64
import io
import os
import app

# Inicia la aplicación Dash con el nombre 'prueba'
prueba = dash.Dash(__name__)

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
