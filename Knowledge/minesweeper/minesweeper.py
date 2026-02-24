import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        # Si el número de celdas es igual a la cuenta de minas, todas esas celdas son minas.
        if len(self.cells) == self.count and self.count != 0:
            return self.cells
        return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        # Si la cuenta de minas es 0, todas las celdas son seguras.
        if self.count == 0:
            return self.cells
        return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        # Si la celda está en esta sentencia:
        # 1. Se quitan del set.
        # 2. Resta 1 a la cuenta (porque se acaban de encontrar una de las minas que se buscan).
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        # Si la celda está en esta sentencia:
        # 1. Se quitan del set.
        # 2. No cambia la cuenta (porque esta celda no era mina, así que las minas deben estar en las celdas restantes).
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.
        """
        # 1) Mark the cell as a move that has been made
        self.moves_made.add(cell)

        # 2) Mark the cell as safe
        self.mark_safe(cell)

        # 3) Add a new sentence to the AI's knowledge base based on neighbors
        # Recopilar vecinos indeterminados
        cells = set()
        mine_count = count
        
        # Iterar sobre vecinos (3x3 grid alrededor de la celda)
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                
                # Ignorar la celda central
                if (i, j) == cell:
                    continue

                # Verificar límites
                if 0 <= i < self.height and 0 <= j < self.width:
                    # Si ya se sabe que es mina, se resta a la cuenta y no se agrega a la sentencia
                    if (i, j) in self.mines:
                        mine_count -= 1
                    # Si ya se sabe que es segura, se ignora
                    elif (i, j) in self.safes:
                        continue
                    # Si no se sabe nada, es una incógnita para la nueva sentencia
                    else:
                        cells.add((i, j))

        # Crear y agregar la nueva sentencia
        new_sentence = Sentence(cells, mine_count)
        self.knowledge.append(new_sentence)

        # 4) & 5) Inference Loop (Bucle de Inferencia)
        # Se repite esto hasta que no se pueda deducir nada nuevo para asegurar que se propago todo el conocimiento en cadena.
        knowledge_changed = True
        while knowledge_changed:
            knowledge_changed = False
            
            # Parte A: Buscar minas y seguros obvios en las sentencias existentes
            safes_to_mark = set()
            mines_to_mark = set()

            for sentence in self.knowledge:
                safes = sentence.known_safes()
                mines = sentence.known_mines()
                
                if safes:
                    safes_to_mark.update(safes)
                if mines:
                    mines_to_mark.update(mines)

            # Si se encuentra algo, se actualiza y marca el flag de cambio
            if safes_to_mark:
                for safe in safes_to_mark:
                    if safe not in self.safes:
                        self.mark_safe(safe)
                        knowledge_changed = True
            
            if mines_to_mark:
                for mine in mines_to_mark:
                    if mine not in self.mines:
                        self.mark_mine(mine)
                        knowledge_changed = True

            # Limpieza: Eliminar sentencias vacías para no procesar basura
            self.knowledge = [x for x in self.knowledge if len(x.cells) > 0]

            # Parte B: Inferencia de Subconjuntos (Subset Inference)
            # Si Sentencia A es subconjunto de Sentencia B, entonces B - A = ConteoB - ConteoA
            new_sentences = []
            
            for sentenceA in self.knowledge:
                for sentenceB in self.knowledge:
                    # Evitar compararse a sí mismo
                    if sentenceA == sentenceB:
                        continue
                        
                    # Verificar si A es subconjunto estricto de B
                    if sentenceA.cells.issubset(sentenceB.cells):
                        new_cells = sentenceB.cells - sentenceA.cells
                        new_count = sentenceB.count - sentenceA.count
                        
                        inferred_sentence = Sentence(new_cells, new_count)
                        
                        # Agregar solo si es información nueva
                        if inferred_sentence not in self.knowledge and inferred_sentence not in new_sentences:
                            new_sentences.append(inferred_sentence)
                            knowledge_changed = True

            self.knowledge.extend(new_sentences)

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.
        """
        for cell in self.safes:
            if cell not in self.moves_made:
                return cell
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        # Generar todas las posibles celdas disponibles
        available_moves = []
        for i in range(self.height):
            for j in range(self.width):
                if (i, j) not in self.moves_made and (i, j) not in self.mines:
                    available_moves.append((i, j))

        if not available_moves:
            return None

        return random.choice(available_moves)