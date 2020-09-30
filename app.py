from flask import Flask
from flask import request
import pandas as pd
import difflib
import numpy as np
import time
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import flask

from UnidadePorTexto import UnidadePorTexto
from ResultadoPreco import Resultado_Preco, Detalhe_Insumo
import calculo_preco
#from werkzeug.contrib.cache import SimpleCache
#from flask_caching import Cache
#cache = SimpleCache()

config = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "simple",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300
}
#app = Flask(__name__)
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

server = flask.Flask(__name__)

app = dash.Dash(
    __name__,
    server=server,
    routes_pathname_prefix='/dash/',
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)


#server = app.server

# tell Flask to use the above defined config
# app.config.from_mapping(config)
#cache = Cache(app)


app.layout = html.Div([
    dbc.Alert([
    html.H1("Calculo de Preços", className="alert-heading")
    ]),
    html.Div(children= [
        
    dbc.Label("Formula: "),
    dbc.Textarea(className="mb-3", id='formula', value='30 ENV | CAFEINA   100MG'),



    html.Div(["Valor Correto: ",
              dcc.Input(id='valor', value=100, type='number')]),
    html.Br(),

    dbc.Button( "Calcular preço", color="primary", className="mr-1", id='button-2'),
    html.Br(),
    html.Br(),

    dcc.Loading(
        id="loading-3",
        type="circle",
        children=html.Div(id='div-resultado')
    )]
    , style={'marginLeft': 25})

])


@app.callback(
    [
        Output(component_id='div-resultado', component_property='children')
    ],
    [Input('button-2', 'n_clicks')],
    state=[State(component_id='formula', component_property='value'),
           State(component_id='valor', component_property='value'),
           ]
)
def update_output_div(n_clicks, formula, valor):
    ret1, ret2, resultado = calculo_preco.calcular_preco(formula, valor, False)

    div_detalhes = []
    for detalhe in resultado.detalhes_insumos:
        div_detalhes.append(
            dbc.Row([
                html.Div(children=[
                    html.Div(children='''
                {}
                '''.format(detalhe.nome)),
                    html.Div(children='''
                Entcontrado: {}
                '''.format(detalhe.encontrado)),

                html.Div(children='''
                Preço: {}
                '''.format(detalhe.valor)),

                html.Br()

                ]
                )
            ])
        )

    ret = [
        html.Br(),
        html.Div(children='''
        Valor Calculado R$ {:.2f}
    '''.format(resultado.preco_calculado)),
        html.Div(children='''
        Nivel Incerteza: {}
    '''.format(resultado.nivel_incerteza)),
        html.Br(),
        html.Details([html.Summary('Detalhes'),
                      html.Div(id='detalhes', children=div_detalhes)])]

    # return '{}'.format(ret1), ret2, ret
    return [ret]


@server.route('/')
def Hello():
    return 'Hi'


@server.route('/iniciar')
def iniciar():
    insumos = pd.read_csv("roval2.csv")
    insumos['PRCORRETO'] = insumos['PRCORRETO'].astype(float)
    #insumos['PRCORRETO'] = insumos['PRCORRETO'].str.replace(',', '.').astype(float)
    insumos.DESCR = insumos.DESCR.astype(str)

    insumos['DESCR'] = insumos['DESCR'].str.strip()
    insumos['UNIDA'] = insumos['UNIDA'].str.strip()
    insumos['UNIVOL'] = insumos['UNIVOL'].str.strip()

    insumosNomes = insumos.DESCR
    insumosNomes = np.unique(insumosNomes).tolist()
    insumos = insumos[insumos['ANO'] >= 2019]
    #cache.set('insumos', insumos, timeout=5 * 60*300)
    #cache.set('insumosNomes', insumosNomes, timeout=5 * 60*300)
    insumosPreco = pd.read_csv("InsumosPreco2.csv")
    insumosPreco = insumosPreco.sort_values(by=['COUNT'], ascending=False)
    #cache.set('insumosPreco', insumosPreco, timeout=5 * 60*300)
    return 'Ok'


@server.route('/preco')
def calcular_preco_endpoint():
    try:
        desc = request.args.get('desc', str)
        valor = request.args.get('valor', float)
        return calculo_preco.calcular_preco(desc, valor, True)
    except Exception as e:
        return str(e)


if __name__ == '__main__':
    app.run_server(debug=True)
