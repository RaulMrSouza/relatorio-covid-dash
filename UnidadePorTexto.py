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