#!/usr/bin/env python
'''
Jose Javier Jo Escobar - 14343
Proyecto 1 Inteligencia Artificial
'''
import argparse
import sys
import csv
from Queue import PriorityQueue
from copy import deepcopy

ALL_VALID = 511 # the bit string 111111111
VALID_DIGITS_STR = "123456789"

def popcount(x):
    """
    Función de utilidad para obtener el popcount (# de 1 bits) en una cadena de bits
    """
    return bin(x).count("1")

def get_vals_as_list(bstr):
    """
    Convierte una cadena de bits que codifica los valores posibles para una celda en una
    matriz de valores enteros

    e.g. 100000010 => [2, 9]
    """
    val = 1
    vals = []
    while bstr != 0:
        if bstr & 1:
            vals.append(val)
        bstr >>= 1
        val += 1
    return vals

class Solver(object):
    """
    Abarca la lógica del proceso de solución.
    """

    def __init__(self, initial_board):
        self.start = initial_board
        self.visited_set = set()
        self.queue = PriorityQueue()

    def solve(self):
        """
        Esta es una implementación del algoritmo A-star. El objetivo en
        Cada etapa del rompecabezas consiste en seleccionar un próximo movimiento válido que maximice
        Progreso hacia el estado objetivo en el que se resuelve el rompecabezas.
        """
        puzzle_state = self.start
        puzzle_state.fast_forward()
        dist = puzzle_state.get_dist_to_goal()
        self.queue.put((dist, puzzle_state))

        while not puzzle_state.is_complete() and self.queue.qsize():
            puzzle_state = self.queue.get()[1]
            puzzle_hash = str(puzzle_state)
            self.visited_set.add(puzzle_hash)

            for c in puzzle_state.create_children():
                if str(c) not in self.visited_set:
                    dist = c.get_dist_to_goal()
                    self.queue.put((dist, c))

        return puzzle_state

    def validate_solution(self, solution):
        """
        Realiza algunas comprobaciones rápidas de integridad para validar la solución.
        """
        ROW_TOTAL = sum(range(1,10))

        for r, row in enumerate(self.start.board):
            for c, val in enumerate(row):
                if val and val != solution.board[r][c]:
                    raise Exception("Initial board has been manipulated!")

        for row in solution.board: 
            if sum(row) != ROW_TOTAL:
                raise Exception("Row total for row %d doesn't add up!" % row)
        
        for col in range(9):
            col_total = sum([solution.board[row][col] for row in range(9)])
            if col_total != ROW_TOTAL:
                raise Exception("Col total for column %d doesn't add up!" % col)

        for row_start in range(0,9,3):
            for col_start in range(0,9,3):
                subrows = []
                for i in range(3):
                    subrows.append(solution.board[row_start+i][col_start:col_start+3])
                section_total = sum([reduce(lambda x,y: x+y, row) for row in subrows])
                if section_total != ROW_TOTAL:
                    raise Exception("Section total for section at (%d, %d) doesn't add up!" % (row_start, col_start))

class BoardState(object):
    """
    Describe una sola instancia del tablero de juego. Estructura de datos subyacente
    Es una matriz 2D.
    """
    
    def __init__(self, csvdata):
        """
        Constructor de un solo uso para traducir datos CSV al tablero de juego.
        """
        board_char_data = list(csv.reader(csvdata))
        # Convert CSV of char strings into csv of ints
        char2int = lambda c: int(c) if c in VALID_DIGITS_STR else 0
        self.board = []
        for row in board_char_data:
            self.board.append(map(char2int, row))

        # Calcula posibles valores para cada celda vacia
        self.possible_vals = [[ALL_VALID for j in range(9)] for i in range(9)]
        for r, row in enumerate(self.board):
            for c, val in enumerate(row):
                if val:
                    self.mark_value_invalid(r,c,val)

    def place_value(self, row, col, val):
        """
        Coloca el valor `val` en (` fila`, `col`) y marque el valor como no válido
        selección en otro lugar en el rompecabezas.
        """
        self.board[row][col] = val
        self.mark_value_invalid(row, col, val)

    def mark_value_invalid(self, row, col, val):
        """
        Marque el valor `val` colocado en (` fila`, `col`) para las celdas donde` val` es
        Ya no es una opción válida.
        """
        self.possible_vals[row][col] = 0
        val_mask = (511 - (1 << val-1))

        # Marque este valor como no válido para todas las celdas en la fila especificada
        for c in range(9):
            self.possible_vals[row][c] &= val_mask

        # Marque este valor como no válido para todas las celdas en la columna especificada
        for r in range(9):
            self.possible_vals[r][col] &= val_mask

        # Marque este valor como no válido para todas las celdas en el mismo cuadrado de 3x3
        start_row, start_col = 3*(row/3), 3*(col/3)
        end_row, end_col = start_row + 3, start_col + 3
        for r in range(start_row, end_row):
            for c in range(start_col, end_col):
                self.possible_vals[r][c] &= val_mask

    def get_dist_to_goal(self):
        """
        El objetivo de esta función es establecer una medida cuantitativa de
        distancia desde el estado final (resuelto). Actualmente usa un conteo ingenuo de
        El número de celdas rellenas en el tablero.
        """
        bool_map = [map(bool, row) for row in self.board]
        return sum([sum(r) for r in bool_map])
        
    def is_complete(self):
        return self.get_dist_to_goal() == 0 

    def get_scored_next_steps(self):
        """
        Crear una instancia y devolver una cola de prioridad donde las celdas tienen prioridad
        Según el número de valores posibles que puedan tomar. Menos es mejor,
        bc significa una mayor probabilidad de seleccionar el valor correcto.
        """
        scored_steps = PriorityQueue()
        for r, row in enumerate(self.possible_vals):
            for c, val in enumerate(row):
                pc = popcount(val)
                # Agregar celdas con # vals posibles> 0 a la cola
                if pc:
                    poss_vals = get_vals_as_list(self.possible_vals[r][c])
                    scored_steps.put((pc, r, c, poss_vals))
        return scored_steps

    def fast_forward(self):
        """
        Escanee el tablero en busca de próximos movimientos obvios, y siga adelante y haga esos.

        En particular, esto significa buscar repetidamente las celdas que hemos marcado.
        como tener un solo valor posible y realmente colocar ese valor en el
        tablero.
        """
        cells_need_updating = True
        while cells_need_updating:
            cells_need_updating = False
            for r, row in enumerate(self.possible_vals):
                for c, poss_vals in enumerate(row):
                    pc = popcount(poss_vals)
                    if pc == 1: 
                        if not cells_need_updating: cells_need_updating = True
                        val = get_vals_as_list(poss_vals)[0]
                        self.place_value(r, c, val)

    def create_children(self):
        """
        Aquí examinamos las alternativas disponibles para nuestro próximo paso, según lo calificado
        utilizando la función get_scored_next_steps. Simplemente tomamos uno de los mejores
        las celdas clasificadas (la menor cantidad de valores posibles) y crear estados de tablero donde cada
        de los posibles valores es seleccionado.
        """

        next_steps = self.get_scored_next_steps()
        if next_steps.qsize():
            pc, row, col, choices = self.get_scored_next_steps().get()
            children = []
            for val in choices:
                child = deepcopy(self)
                child.place_value(row, col, val)
                child.fast_forward()
                children.append(child)

            return children
        else:
            return []

    def pretty_print(self):
        int2str = lambda s: str(s).replace('0', ' ')
        rows = [','.join(map(int2str, row)) for row in self.board]
        print '\n'.join(rows)

    def __str__(self):
        """
        Devuelve un identificador de picadura único para este tablero
        """
        return ''.join([''.join(map(str, row)) for row in self.board])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="nombre del formato CSV que contiene el tablero de sudoku")
    args = parser.parse_args()

    try:
        csvdata = open(args.file, 'rb')
    except IOError:
        print "No se logro leer el archivo.  '%s' tiene algun path valido??" % args.file
        sys.exit(-1)

    start = BoardState(csvdata)
    print "\nTablero ingresado:"
    start.pretty_print()
    print "\nResolviendo...\n"
    solver = Solver(start)
    fin = solver.solve()
    solver.validate_solution(fin)
    print "Completado! esta es la solucion:\n"
    fin.pretty_print()

