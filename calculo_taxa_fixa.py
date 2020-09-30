def calculo_taxa_fixa(valor, farmacia):
    if farmacia.str.lower == "roval":
        return valor + 30
    else:
        return valor + 30

def calcular_preco_fixo_farmacia(farmacia, total, formulaQtd):
    if farmacia == 'Rhamus':
        t = total+41
        if formulaQtd <= 30 and total < 41:
            total = 41
        elif formulaQtd > 30 and formulaQtd <= 40 and total < 51:
            total = 51
        elif formulaQtd > 40 and formulaQtd <= 50 and total < 60:
            total = 60
        elif formulaQtd > 50 and formulaQtd <= 60 and total < 71:
            total = 71
        elif formulaQtd > 60 and formulaQtd <= 70 and total < 75:
            total = 75
        elif formulaQtd > 70 and formulaQtd <= 80 and total < 81:
            total = 81
        elif formulaQtd > 80 and formulaQtd <= 90 and total < 86:
            total = 86
        elif formulaQtd > 90  and total < 95:
            total = 95
        else:
            total+=41
        if t > total:
            total = t
    elif farmacia == 'Roval':
        total += 30
    elif farmacia == 'FarmaGri':
        total += 35
    return (total)