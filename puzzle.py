'''
    Proyecto # 1 Inteligencia Artificial
    Busqueda utilizando algoritmos como A *
'''
import pprint
pp = pprint.PrettyPrinter(indent=4)

def ei_star(__ASTART,__END):
    """
    Definicion de Algoritmo A*
    """
    estados = [[manhattan(__ASTART), __ASTART]]
    expansiones = []
    nodos_expandidos = 0
    while estados:
        i = 0
        for j in range(1, len(estados)):
            if estados[i][0] > estados[j][0]:
                i = j
        path = estados[i]
        estados = estados[:i] + estados[i+1:]
        endnode = path[-1]
        if endnode == __END:
            break
        if endnode in expansiones:
            continue
        for k in actions(endnode):
            if k in expansiones:
                continue
            newpath = [path[0] + manhattan(k) - manhattan(endnode)] + path[1:] + [k]
            estados.append(newpath)
            expansiones.append(endnode)
        nodos_expandidos += 1
    print "SOLUCION:"
    pp.pprint(path)
    print "EXPANSIONES DEL GRAFO:", nodos_expandidos




def actions(__INPUT):
    """
    Regresamos una lista de los posibles movimientos de la matriz
    """
    MOVIMIENTOS = []
    m = eval(__INPUT)
    i = 0
    while 0 not in m[i]:
        i += 1
    # Espacio en blanco (#0)
    j = m[i].index(0);

    if i > 0:
    #ACCION MOVER ARRIBA
      m[i][j], m[i-1][j] = m[i-1][j], m[i][j];
      MOVIMIENTOS.append(str(m))
      m[i][j], m[i-1][j] = m[i-1][j], m[i][j];

    if i < 3:
    # ACCION MOVER ABAJO
      m[i][j], m[i+1][j] = m[i+1][j], m[i][j]
      MOVIMIENTOS.append(str(m))
      m[i][j], m[i+1][j] = m[i+1][j], m[i][j]

    if j > 0:
    # ACCION MOVER IZQUIERDA
      m[i][j], m[i][j-1] = m[i][j-1], m[i][j]
      MOVIMIENTOS.append(str(m))
      m[i][j], m[i][j-1] = m[i][j-1], m[i][j]

    if j < 3:
    # ACCION MOVER DERECHA
      m[i][j], m[i][j+1] = m[i][j+1], m[i][j]
      MOVIMIENTOS.append(str(m))
      m[i][j], m[i][j+1] = m[i][j+1], m[i][j]

    return MOVIMIENTOS



def manhattan(puzz):
    """
    Calculo de distancia manhattan entre nodos, se busca la menor distancia del estado deseado
    """
    distancia_nodos = 0
    m = eval(puzz)
    for i in range(4):
        for j in range(4):
            if m[i][j] == 0:
                continue
            distancia_nodos += abs(i - (m[i][j]/4)) + abs(j -  (m[i][j]%4));
    return distancia_nodos

if __name__ == '__main__':
    __INICIAL = str([[1, 8, 6, 3],[4, 9, 5, 12], [2, 13, 11, 15],[7, 14, 0, 10]])
    _FINAL = str([[0, 1, 2, 3],[4, 5, 6, 7], [8, 9, 10, 11],[12, 13, 14, 15]])
    ei_star(__INICIAL,_FINAL)

'''
Se tomo como referencia el video https://www.youtube.com/watch?v=GuCzYxHa7iA 
y el codigo de github https://github.com/JaneHJY/8_puzzle 

'''