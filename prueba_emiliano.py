import dash
from dash import dcc, html, Input, Output
import pandas as pd
import base64
import io
import os

# Inicia la aplicación Dash con el nombre 'prueba'
prueba2 = dash.Dash(__name__)

server=prueba2.server

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
