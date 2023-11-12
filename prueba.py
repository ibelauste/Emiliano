import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import base64
import io

# Inicia la aplicación Dash con el nombre 'prueba'
prueba = dash.Dash(__name__)

server = app.server

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
    content_type, content_string = contents.split(',')

    # Decodifica el contenido base64 en datos binarios
    decoded = base64.b64decode(content_string)

    # Lee los datos del CSV
    df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))

    # Agrupa por año y suma las ventas globales
    df_grouped = df.groupby('Year')['Global_Sales'].sum().reset_index()

    return df_grouped

# Callback para cargar el archivo y actualizar el gráfico
@prueba.callback(Output('line-chart', 'figure'),
              [Input('upload-data', 'contents'),
               Input('upload-data', 'filename')])
def update_graph(contents, filename):
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
    prueba.run_server(debug=True)
