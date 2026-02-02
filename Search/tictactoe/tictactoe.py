"""
Tic Tac Toe Player
"""

import math
import copy  # Necesario para crear copias independientes de los tableros

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    
    # Contar cuántas X y O hay en el tablero
    x_count = sum(row.count(X) for row in board)
    o_count = sum(row.count(O) for row in board)

    # X siempre empieza. Si hay igualdad, le toca a X. Si X tiene uno más, le toca a O.
    if x_count <= o_count:
        return X
    else:
        return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    possible_moves = set()
    
    # Recorre la matriz 3x3 buscando celdas vacías
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                # Añade la tupla (fila, columna) al set de acciones
                possible_moves.add((i, j))
                
    return possible_moves


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    # 1. Validación defensiva: Asegura que la acción sea válida
    if action not in actions(board):
        raise Exception("Invalid Action")

    # 2. Inmutabilidad (Concepto Clave en IA):
    # No se puede modificar el tablero original ('board'), porque el algoritmo Minimax necesita reutilizar ese estado para explorar otras ramas del árbol.
    # Se usa deepcopy para clonar la estructura completa en memoria nueva.
    new_board = copy.deepcopy(board)
    
    # 3. Ejecución del movimiento
    row, col = action
    # Determina de quién es el turno en el estado original y coloca su ficha
    new_board[row][col] = player(board)
    
    return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    Devuelve X, O, o None si no hay ganador aún.
    """
    # Verificación Horizontal (Filas)
    for row in board:
        # Si los 3 elementos de la fila son iguales y no son EMPTY
        if row[0] == row[1] == row[2] and row[0] is not None:
            return row[0]

    # Verificación Vertical (Columnas)
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] and board[0][col] is not None:
            return board[0][col]

    # Verificación Diagonal Principal (Top-Left a Bottom-Right)
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] is not None:
        return board[0][0]
    
    # Verificación Diagonal Secundaria (Top-Right a Bottom-Left)
    if board[0][2] == board[1][1] == board[2][0] and board[0][2] is not None:
        return board[0][2]

    # Si nadie ganó
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    # El juego termina bajo dos condiciones:
    # 1. Alguien ganó.
    if winner(board) is not None:
        return True
    
    # 2. No hay ganador, pero el tablero está lleno (Empate).
    # Si queda al menos una celda EMPTY, el juego NO ha terminado.
    for row in board:
        if EMPTY in row:
            return False
            
    # Hasta aquí, hay empate y tablero lleno.
    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    Esta función asigna un valor numérico al estado final para que Minimax pueda comparar.
    """
    win_player = winner(board)
    
    if win_player == X:
        return 1  # X busca maximizar, por eso es positivo
    elif win_player == O:
        return -1 # O busca minimizar, por eso es negativo
    else:
        return 0  # Empate


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    # Si resulta un tablero ya terminado, no hay movimiento posible
    if terminal(board):
        return None

    current_player = player(board)

    # CASO 1: Persona es el jugador X (MAXIMIZER)
    if current_player == X:
        v = -math.inf
        best_move = None
        
        # Se pruevan todas las acciones posibles
        for action in actions(board):
            # Se simula el movimiento en min_value
            move_val = min_value(result(board, action))
            
            # Si este movimiento es mejor que el que se tiene, se guarda
            if move_val > v:
                v = move_val
                best_move = action
        return best_move

    # CASO 2: Persona es el jugador O (MINIMIZER)
    else:
        v = math.inf
        best_move = None
        
        for action in actions(board):
            # Se simula el movimiento en max_value
            move_val = max_value(result(board, action))
            
            if move_val < v:
                v = move_val
                best_move = action
        return best_move


# --- Funciones Auxiliares (El motor recursivo) ---

def max_value(board):
    """
    Calcula el valor máximo posible desde este estado.
    Usada por X para ver sus opciones, o por O para predecir a X.
    """
    # Caso Base: Si el juego terminó, devolve el puntaje (-1, 0, 1)
    if terminal(board):
        return utility(board)
    
    # Inicializa con el peor valor posible para un maximizador (-infinito)
    v = -math.inf
    
    # Recursión: Itera sobre las acciones posibles
    for action in actions(board):
        # "v" será el máximo entre lo que se tiene y lo que devuelve el nivel inferior
        v = max(v, min_value(result(board, action)))
    return v


def min_value(board):
    """
    Calcula el valor mínimo posible desde este estado.
    Usada por O para ver sus opciones, o por X para predecir a O.
    """
    # Caso Base
    if terminal(board):
        return utility(board)
    
    # Inicializa con el peor valor posible para un minimizador (+infinito)
    v = math.inf
    
    # Recursión
    for action in actions(board):
        # "v" será el mínimo entre lo que se tiene y lo que devuelve el nivel inferior
        v = min(v, max_value(result(board, action)))
    return v