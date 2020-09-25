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
import flask
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
    routes_pathname_prefix='/dash/'
)


#server = app.server

# tell Flask to use the above defined config
# app.config.from_mapping(config)
#cache = Cache(app)


app.layout = html.Div([
    html.H1("Calculo de Preços"),
    html.Div(["Formula: ",
              dcc.Input(id='formula', value='30 ENV | CAFEINA   100MG', type='text', style=dict(
                  width='80%',
                  display='table',
              ))]),
    html.Br(),
    html.Div(["Valor Correto: ",
    dcc.Input(id='valor', value=100, type='number')]),
    html.Br(),
    html.Button('Calcular', id='button-2'),
    html.Br(),
    html.Br(),
    html.Div(id='resultado'),
    # dcc.RadioItems(
    #     id='toggle',
    #     options=[{'label': i, 'value': i} for i in ['Mostrar Detalhes', 'Esconder']],
    #     value='Show'
    # ),
    html.Br(),
    html.Details([html.Summary('Detalhes'),
    html.Div(id='detalhes')]),

])


@app.callback(
    [Output(component_id='resultado', component_property='children'),
    Output(component_id='detalhes', component_property='children')],
    [Input('button-2', 'n_clicks')],
    state=[State(component_id='formula', component_property='value'),
    State(component_id='valor', component_property='value'),
    ]
)
def update_output_div(n_clicks, formula, valor):
    ret1, ret2 = calcular_preco(formula, valor, False) 
    return '{}'.format(ret1), ret2


def UnidadePorTexto(quantidade):
    for i, c in enumerate(quantidade):
        if not c.isdigit() and c != ',' and c != '.' and c != ' ':
            break
    qtd = -1
    try:
        qtd = float(quantidade[:i])
    except ValueError:
        print("")
    unidade = quantidade[i:]

    return (qtd, unidade)


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


def calcular_preco(desc, valor, endpoint):
    start_time = time.time()
    #insumos = pd.read_csv("roval2.csv")
    print("--- %s seconds ---" % (time.time() - start_time))
    start_time = time.time()
    #insumos = cache.get('insumos')
    insumos = None
    try:
        if insumos == None:
            insumos = pd.read_csv("roval2.csv")
            insumosNomes = insumos.DESCR
            insumosNomes = np.unique(insumosNomes).tolist()
            insumosPreco = pd.read_csv("InsumosPreco2.csv")
            #cache.set('insumos', insumos, timeout=5 * 60*300)
            #ache.set('insumosNomes', insumosNomes, timeout=5 * 60*300)
            insumosPreco = insumosPreco.sort_values(
                by=['COUNT'], ascending=False)
            #cache.set('insumosPreco', insumosPreco, timeout=5 * 60*300)
    except:
        pass
    #insumosNomes = cache.get('insumosNomes')
    #insumosPreco = cache.get('insumosPreco')

    insumos = insumos.sort_values(by=['COUNT'], ascending=False)

    orcamentos = pd.DataFrame(
        data={'Descricao': [desc.upper()], 'Valor': [valor]})

    orcamentos = orcamentos.dropna(subset=['Descricao'])

    orcamentos = orcamentos.head(200)

    print("--- %s Carregar ---" % (time.time() - start_time))
    start_time = time.time()

    for index, row in orcamentos.iterrows():

        formula = row['Descricao']

        formulaVolume = str(formula).split('|')[0]

        (formulaQtd, formulaUnidade) = UnidadePorTexto(formulaVolume)

        insumosFormula = str(formula).split('|')[1].split(';')

        total = 0

        nivelIncerteza = 0

        valorIncerto = 0

        valorInsumo = ""

        for insumo in insumosFormula:

            print("--- %s seconds ---" % (time.time() - start_time))
            start_time = time.time()

            insumoDescr = difflib.get_close_matches(
                (''.join(insumo.split(' ')[:-1])).strip(), insumosNomes, n=1, cutoff=.6)

            print("match--- %s seconds ---" % (time.time() - start_time))
            start_time = time.time()

            quantidade = insumo.split(' ')[-1]
            (qtd, unidade) = UnidadePorTexto(quantidade)

            if len(insumoDescr) == 0:
                print(insumo.strip() + ": Não encontrado match")
                nivelIncerteza = 3
            elif qtd == -1:
                print("Qtd Invalida", insumoDescr, quantidade)
                nivelIncerteza = 3
            else:
                insumoDescr = insumoDescr[0]

                insumosDesc = insumosPreco[(insumosPreco['DESCR'] == insumoDescr.strip())
                                           & (insumosPreco['UNIVOL'] == formulaUnidade.strip())
                                           & (insumosPreco['UNIDA'] == unidade.strip())]

                if not insumosDesc.empty:

                    insumoDf = insumosPreco[
                        (insumosPreco['UNIDA'] == unidade.strip())
                        & (insumosPreco['CDPRO'] == insumosDesc.iloc[0].CDPRO)
                        & (insumosPreco['CDPRIN'] == insumosDesc.iloc[0].CDPRIN)
                        # & (insumos['PRODUNIDA'].str.strip() == 'ML')
                        # & (insumos['QTDINS'] == 1)
                        & (insumosPreco['UNIVOL'] == formulaUnidade.strip())
                        & (insumosPreco['PRCORRETO'] != 0)
                    ]

                    #insumoDf = insumoDf.sort_values(by=['COUNT'], ascending=False)

                    valorUnit = insumoDf.iloc[0].PRCORRETO

                    valor = valorUnit * qtd

                    valor = valor * formulaQtd

                    total += valor

                    if insumoDf.iloc[0].VAR > 1 and nivelIncerteza == 0:
                        nivelIncerteza = 1
                        valorIncerto += valor

                    if insumoDf.iloc[0].DIST < 50 and insumoDf.iloc[0].VAR > 0.5:
                        nivelIncerteza = 4
                        valorIncerto += valor

                    valorInsumo += "\r\n" + insumoDescr + " " + str(qtd) + unidade + " : R$ " + str(round(valor, 2)) + " vlrUnid: R$" + str(round(
                        insumoDf.iloc[0].PRCORRETO, 4)) + " u: " + str(insumoDf.iloc[0].UNIDA) + " var " + str(insumoDf.iloc[0].VAR) + "dist preço " + str(insumoDf.iloc[0].DIST)
                    # print(valorInsumo)
                    print(insumoDescr)
                else:
                    print(insumoDescr + " " + unidade + ": Não encontrado")
                    nivelIncerteza = 3
                print("calc --- %s seconds ---" % (time.time() - start_time))
                start_time = time.time()

        if total < 300:
            total += 30
        # if temUN:
            #total += 30

        if valorIncerto > 0 and (valorIncerto/(total/100) < 20 and valorIncerto < 40):
            nivelIncerteza = 0

        erro = round(abs(100 - (total / (float(row['Valor'])/100.0))), 2)

        erroValor = abs((total - float(row['Valor'])))
        if endpoint:
            return 'Valor Incerto ' + str(valorIncerto) + '\r\n' + str(valorInsumo) + '\r\n Calculado: ' + str(round(total, 2)) + ' Correto: ' + str(row['Valor']) + " \r\n diferença % :" + str(erro) + " nível Incerteza: " + str(nivelIncerteza)
        else:
            return 'Valor :' + str(round(total, 2)), 'Valor Incerto ' + str(valorIncerto) + '\r\n' + str(valorInsumo) + '\r\n Calculado: ' + str(round(total, 2)) + ' Correto: ' + str(row['Valor']) + " \r\n diferença % :" + str(erro) + " nível Incerteza: " + str(nivelIncerteza)


@server.route('/preco')
def calcular_preco_endpoint():
    try:
        desc = request.args.get('desc', str)
        valor = request.args.get('valor', float)
        return calcular_preco(desc, valor, True)
    except Exception as e:
        return str(e)


if __name__ == '__main__':
    app.run_server(debug=True)
