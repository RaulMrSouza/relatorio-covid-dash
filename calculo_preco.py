
import pandas as pd
import difflib
import numpy as np
import time

from UnidadePorTexto import UnidadePorTexto
from ResultadoPreco import Resultado_Preco, Detalhe_Insumo

insumosDescricao = {}
insumosPreco = {}
insumosNomes = {}
farmaciasInsumosNomes = {}

def preparar_dados():
    insumosDescricao = pd.read_csv("InsumosDescricao_geral_novo.csv")
    insumosDescricao = insumosDescricao.groupby(['DESCR', 'FARMACIA', 'CDPRIN', 'CDPRO']).agg({ 'COUNT': 'sum'})
    insumosDescricao = insumosDescricao.sort_index()

    insumosPreco = pd.read_csv("InsumosPreco_geral_novo.csv")
    insumosPreco2 = insumosPreco
    insumosPreco = insumosPreco.groupby(['FARMACIA', 'CDPRIN','CDPRO', 'UNIVOL', 'UNIDA', 'CONVERSAO', 'PRECO']).agg({ 'COUNT': 'sum', 'VAR' : 'mean', 'DIST' : 'mean'})
    insumosPreco = insumosPreco.sort_index()

    insumosNomes = insumosDescricao.index.get_level_values(0).tolist()
    insumosNomes = np.unique(insumosNomes).tolist()
    farmaciasNomes = insumosDescricao.index.get_level_values(1).tolist()
    farmaciasNomes = np.unique(farmaciasNomes).tolist()

    farmaciasInsumosNomes = {}
    for f in farmaciasNomes:
        farmaciasInsumosNomes[f] = insumosDescricao[np.in1d(insumosDescricao.index.get_level_values(1), [f])].index.get_level_values(0)


def PrecoInsumoFarmacia(insumo, insumosDescricao, insumosPreco, farmacia, farmaciasInsumosNomes, insumosPreco2):
    try:
        insumoDescr = difflib.get_close_matches((''.join(insumo.split(' ')[:-1])).strip(), insumosNomes, n=1, cutoff=.6)

        if len(insumoDescr) == 0:
            print(insumo.strip() + ": Não encontrado match")
            return (False, None, "")
        elif qtd == -1:
            print("Qtd Invalida", insumoDescr, quantidade)
            return (False, None, "")
                
        #print("0",insumo)
                
        insumoDescr = insumoDescr[0]
                
        #print("1",insumoDescr)

        if not farmacia in insumosDescricao.loc[insumoDescr].index or True:
            insumoDescr = difflib.get_close_matches((''.join(insumo.split(' ')[:-1])).strip(), farmaciasInsumosNomes[farmacia], n=1, cutoff=.8)

            if not len(insumoDescr) == 0:
                insumoDescr = insumoDescr[0]
                #print("2",insumoDescr)
            else:
                return (False, None, "")
        
        insumosDesc = insumosDescricao.loc[insumoDescr, farmacia].sort_values(by=['COUNT'], ascending=False)

        if not insumosDesc.empty:
            codigos = insumosDesc.sort_values(by=['COUNT'], ascending=False).index.tolist()[0]
            try:
                insumoDf = insumosPreco.loc[farmacia, codigos[0], codigos[1], formulaUnidade.strip(), unidade.strip()].sort_values(by=['COUNT'], ascending=False)
                return (True, insumoDf, insumoDescr)
            except:
                return (False, {}, "")
        else:
            return (False, None, "")
    except ValueError:
        print("erro")
        return (False, None, "")

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

    resultado = Resultado_Preco()
    resultado.detalhes_insumos = []

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

            #print("--- %s seconds ---" % (time.time() - start_time))
            #start_time = time.time()

            insumoDescr = difflib.get_close_matches(
                (''.join(insumo.split(' ')[:-1])).strip(), insumosNomes, n=1, cutoff=.6)

            #print("match--- %s seconds ---" % (time.time() - start_time))
            #start_time = time.time()

            detalhe_insumo = Detalhe_Insumo()

            quantidade = insumo.split(' ')[-1]
            (qtd, unidade) = UnidadePorTexto(quantidade)

            if len(insumoDescr) == 0:
                print(insumo.strip() + ": Não encontrado match")
                nivelIncerteza = 3
                detalhe_insumo.nome = insumo.strip()
                detalhe_insumo.encontrado = False
            elif qtd == -1:
                print("Qtd Invalida", insumoDescr, quantidade)
                nivelIncerteza = 3
                detalhe_insumo.encontrado = False
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

                    detalhe_insumo.nome = insumoDescr
                    detalhe_insumo.valor = str(round(valor, 2))
                    detalhe_insumo.variancia = insumoDf.iloc[0].VAR 
                    detalhe_insumo.encontrado = True

                    valorInsumo += "\r\n" + insumoDescr + " " + str(qtd) + unidade + " : R$ " + str(round(valor, 2)) + " vlrUnid: R$" + str(round(
                        insumoDf.iloc[0].PRCORRETO, 4)) + " u: " + str(insumoDf.iloc[0].UNIDA) + " var " + str(insumoDf.iloc[0].VAR) + "dist preço " + str(insumoDf.iloc[0].DIST)
                    # print(valorInsumo)
                    print(insumoDescr)
                else:
                    print(insumoDescr + " " + unidade + ": Não encontrado")
                    nivelIncerteza = 3
                    detalhe_insumo.encontrado = False
                    detalhe_insumo.nome = insumoDescr
                print("calc --- %s seconds ---" % (time.time() - start_time))
                resultado.detalhes_insumos.append(detalhe_insumo)
                start_time = time.time()

        if total < 300:
            total += 30
        # if temUN:
            #total += 30

        if valorIncerto > 0 and (valorIncerto/(total/100) < 20 and valorIncerto < 40):
            nivelIncerteza = 0

        erro = round(abs(100 - (total / (float(row['Valor'])/100.0))), 2)

        erroValor = abs((total - float(row['Valor'])))

        resultado.nivel_incerteza = nivelIncerteza
        resultado.preco_calculado = total
        resultado.erro = erro
        resultado.erro_valor = erroValor
        resultado.valor_incerto = valorIncerto

        if endpoint:
            return 'Valor Incerto ' + str(valorIncerto) + '\r\n' + str(valorInsumo) + '\r\n Calculado: ' + str(round(total, 2)) + ' Correto: ' + str(row['Valor']) + " \r\n diferença % :" + str(erro) + " nível Incerteza: " + str(nivelIncerteza)
        else:
            return 'Valor :' + str(round(total, 2)), 'Valor Incerto ' + str(valorIncerto) + '\r\n' + str(valorInsumo) + '\r\n Calculado: ' + str(round(total, 2)) + ' Correto: ' + str(row['Valor']) + " \r\n diferença % :" + str(erro) + " nível Incerteza: " + str(nivelIncerteza), resultado



def calcular_preco_old(desc, valor, endpoint):
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

    resultado = Resultado_Preco()
    resultado.detalhes_insumos = []

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

            detalhe_insumo = Detalhe_Insumo()

            quantidade = insumo.split(' ')[-1]
            (qtd, unidade) = UnidadePorTexto(quantidade)

            if len(insumoDescr) == 0:
                print(insumo.strip() + ": Não encontrado match")
                nivelIncerteza = 3
                detalhe_insumo.nome = insumo.strip()
                detalhe_insumo.encontrado = False
            elif qtd == -1:
                print("Qtd Invalida", insumoDescr, quantidade)
                nivelIncerteza = 3
                detalhe_insumo.encontrado = False
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

                    detalhe_insumo.nome = insumoDescr
                    detalhe_insumo.valor = str(round(valor, 2))
                    detalhe_insumo.variancia = insumoDf.iloc[0].VAR 
                    detalhe_insumo.encontrado = True

                    valorInsumo += "\r\n" + insumoDescr + " " + str(qtd) + unidade + " : R$ " + str(round(valor, 2)) + " vlrUnid: R$" + str(round(
                        insumoDf.iloc[0].PRCORRETO, 4)) + " u: " + str(insumoDf.iloc[0].UNIDA) + " var " + str(insumoDf.iloc[0].VAR) + "dist preço " + str(insumoDf.iloc[0].DIST)
                    # print(valorInsumo)
                    print(insumoDescr)
                else:
                    print(insumoDescr + " " + unidade + ": Não encontrado")
                    nivelIncerteza = 3
                    detalhe_insumo.encontrado = False
                    detalhe_insumo.nome = insumoDescr
                print("calc --- %s seconds ---" % (time.time() - start_time))
                resultado.detalhes_insumos.append(detalhe_insumo)
                start_time = time.time()

        if total < 300:
            total += 30
        # if temUN:
            #total += 30

        if valorIncerto > 0 and (valorIncerto/(total/100) < 20 and valorIncerto < 40):
            nivelIncerteza = 0

        erro = round(abs(100 - (total / (float(row['Valor'])/100.0))), 2)

        erroValor = abs((total - float(row['Valor'])))

        resultado.nivel_incerteza = nivelIncerteza
        resultado.preco_calculado = total
        resultado.erro = erro
        resultado.erro_valor = erroValor
        resultado.valor_incerto = valorIncerto

        if endpoint:
            return 'Valor Incerto ' + str(valorIncerto) + '\r\n' + str(valorInsumo) + '\r\n Calculado: ' + str(round(total, 2)) + ' Correto: ' + str(row['Valor']) + " \r\n diferença % :" + str(erro) + " nível Incerteza: " + str(nivelIncerteza)
        else:
            return 'Valor :' + str(round(total, 2)), 'Valor Incerto ' + str(valorIncerto) + '\r\n' + str(valorInsumo) + '\r\n Calculado: ' + str(round(total, 2)) + ' Correto: ' + str(row['Valor']) + " \r\n diferença % :" + str(erro) + " nível Incerteza: " + str(nivelIncerteza), resultado

