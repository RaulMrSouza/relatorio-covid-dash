# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from plotly.graph_objs.layout.shape import Line
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output
import plotly
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

import requests
import io

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

colors = {
    'background': '#FFFFFF', #'#C0C0C0', #'#111111',
    'text': '#111111'  #'#7FDBFF'
}

# baixar csv do dataset
headers = {
    'Content-Type': 'application/json;charset=UTF-8', 'User-Agent': 'google-colab',
    'Accept': 'application/json, text/plain, */*', 'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7'
}

estados_siglas = ["AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RO", "RS", "RR", "SC", "SE", "SP", "TO"]


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

text_style = {
                'textAlign': 'center',
                'color': colors['text']
            }

drop_style = dict(
                    width='80%',
                    display='inline-block',
                    verticalAlign="middle",
                )

drop_margin = {'marginBottom': 12, 'marginTop': 12, 'marginLeft' : 25}
# fig.update_layout(
#     plot_bgcolor=colors['background'],
#     paper_bgcolor=colors['background'],
#     font_color=colors['text']
# )

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(children='Relatório Covid',
            style= text_style
            ),

    html.Div(children='''
        Teste em Dash para app de dados
    ''', style= text_style
             ),

    html.Div( [html.Label('Selecionar sigla de estado'), dcc.Dropdown(
        id='estado-dropdown',
        options=[{'label': i, 'value': i}
                 for i in estados_siglas],
        value='SP',
        style=drop_style
    )], style=drop_margin),

    html.H4(children='Cidades mais afetadas', style= text_style),
    dcc.Loading(
            id="loading-1",
            type="circle",
            children=html.Div(id="cidades", style={'marginLeft' : 12, 'marginRight' : 12})
        ),

    html.H4(children='Evolução no Estado', style= text_style),
    html.Div( [html.Label('Selecionar Campo do grafico'), dcc.Dropdown(
        id='grafico-dropdown',
        options=[{'label': i, 'value': i}
                 for i in ["Óbitos por dia", "Novos Confirmados por dia", "Casos Confirmados por 100k habitantes", "Total de Confirmados",  "Total de Óbitos", "Taxa de Mortalidade"]],
        value='Óbitos por dia',
        style=drop_style
    )]
    , style=drop_margin),

    dcc.Loading(
            id="loading-2",
            type="circle",
            children=dcc.Graph( id='grafico-barras')
    ),

    html.H4(children='Mapa Cloroplético', style= text_style),
    html.Div( [html.Label('Selecionar Campo do Mapa'),
    dcc.Dropdown(
        id='mapa-dropdown',
        options=[{'label': i, 'value': i}
                 for i in ["Casos Confirmados por 100k habitantes", "Total de Confirmados",  "Total de Óbitos", "Taxa de Mortalidade"]],
        value='Casos Confirmados por 100k habitantes',
        style=drop_style
    )]
    , style=drop_margin),

    dcc.Loading(
            id="loading-3",
            type="circle",
            children=dcc.Graph( id='mapa')
    )

    
])


@app.callback(
    [Output('grafico-barras', 'figure')
    , Output('cidades', 'children'),
    Output('mapa', 'figure') ],
    [Input('estado-dropdown', 'value'),
    Input('mapa-dropdown', 'value'),
    Input('grafico-dropdown', 'value')
    ]
    )
def update_graph(estado, campo_mapa, campo_grafico):
    #Carregar informacões de cada cidade
    url = "https://brasil.io/dataset/covid19/caso_full/?state="+estado+"&is_last=true&place_type=city&format=csv"
    response = requests.get(url, headers=headers)
    file_object = io.StringIO(response.content.decode('utf-8'))
    covid = pd.read_csv(file_object)

    #carregar informações do estado
    url = "https://brasil.io/dataset/covid19/caso_full/?state="+estado+"&place_type=state&format=csv"
    response = requests.get(url, headers=headers)
    file_object = io.StringIO(response.content.decode('utf-8'))
    estado = pd.read_csv(file_object)

    covid = covid.rename(columns={"last_available_confirmed_per_100k_inhabitants": "Casos Confirmados por 100k habitantes", "last_available_confirmed": "Total de Confirmados", "last_available_deaths": "Total de Óbitos",
                                "estimated_population_2019": "População Estimada em 2019", "city": "Nome", "new_deaths": "Óbitos por dia", "last_available_death_rate": "Taxa de Mortalidade", "new_confirmed": "Novos Confirmados por dia"})

    estado = estado.rename(columns={"last_available_confirmed_per_100k_inhabitants": "Casos Confirmados por 100k habitantes", "last_available_confirmed": "Total de Confirmados", "last_available_deaths": "Total de Óbitos",
                                    "estimated_population_2019": "População Estimada em 2019", "city": "Nome", "new_deaths": "Óbitos por dia", "last_available_death_rate": "Taxa de Mortalidade", "new_confirmed": "Novos Confirmados por dia"})
    # remover nulos
    covid = covid[covid['Casos Confirmados por 100k habitantes'] > 0]
    idEstado = int(estado['city_ibge_code'].iloc[0])

    covid['Casos Confirmados por 100k habitantes'] = covid['Casos Confirmados por 100k habitantes'].round(2)

    tabelaDF = covid[['Nome', 'Casos Confirmados por 100k habitantes', 'Total de Confirmados', 'Total de Óbitos', 'Taxa de Mortalidade',
                    'População Estimada em 2019']].sort_values(by=['Casos Confirmados por 100k habitantes'], ascending=False).head(10)

    estado = estado.sort_values(by=['date'])
    estado = estado.tail(90)

    estado = estado.set_index('date')
    estado['data'] = estado.index
    estado['Media 7 dias'] = estado[campo_grafico].rolling(window=7).mean()

    fig2 = px.line(estado, x='data', y="Media 7 dias", title=campo_grafico)
    fig2.add_bar(x=estado.index, y=estado[campo_grafico], name=campo_grafico)
    #fig2.add
    fig2.update_layout(
     plot_bgcolor=colors['background'],
     paper_bgcolor=colors['background'],
     font_color=colors['text']
    )

    data = tabelaDF.to_dict('rows')
    columns =  [{"name": i, "id": i,} for i in (tabelaDF.columns)]

    cidades = requests.get("https://servicodados.ibge.gov.br/api/v2/malhas/"+str(idEstado)+"/?formato=application/vnd.geo+json&resolucao=5", headers=headers)
    cidades = cidades.json()

    covid['codarea'] = covid['city_ibge_code']
    covid = covid.set_index('codarea')
    covid['codarea'] = covid.index.astype(int).astype(str)

    covid['hover'] = covid['Nome'] + '<br>' + \
    'casos por 100k h. :' + covid['Casos Confirmados por 100k habitantes'].astype(str) + '<br>' + \
    'Taxa Letalidade: ' + covid['Taxa de Mortalidade'].astype(str) + '<br>' + \
    'Total de Óbitos: ' + covid['Total de Óbitos'].astype(str) + '<br>' + \
    'População Est. 2019: ' + covid['População Estimada em 2019'].astype(str)

    tabela = dash_table.DataTable(data=data, columns=columns,
        style_cell_conditional=[
        {
            'if': {'column_id': c},
            'textAlign': 'left'
        } for c in ['Date', 'Region']
    ],
    style_data_conditional=[
        {
            'if': {'row_index': 'odd'},
            'backgroundColor': 'rgb(248, 248, 248)'
        }
    ],
    style_header={
        'backgroundColor': 'rgb(230, 230, 230)',
        'fontWeight': 'bold'
    })

    # html.Table([
    #     html.Thead(
    #         html.Tr([html.Th(col) for col in tabelaDF.columns])
    #     ),
    #     html.Tbody([
    #         html.Tr([
    #             html.Td(tabelaDF.iloc[i][col]) for col in tabelaDF.columns
    #         ]) for i in range(min(len(tabelaDF)))
    #     ])
    # ])

    mapa = px.choropleth(covid, geojson=cidades, locations='codarea', color=campo_mapa,
                           color_continuous_scale="Viridis",
                           range_color=(covid[campo_mapa].min(), covid[campo_mapa].max()),
                           featureidkey="properties.codarea",
                            projection="mercator",
                            hover_name="hover",
                            labels={campo_mapa: campo_mapa}
                          )
    mapa.update_geos(fitbounds="locations", visible=False)
    mapa.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    mapa.update_layout(
     plot_bgcolor=colors['background'],
     paper_bgcolor=colors['background'],
     font_color=colors['text']
    )

    return fig2, tabela, mapa

if __name__ == '__main__':
    app.run_server(debug=True)
