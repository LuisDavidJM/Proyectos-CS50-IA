import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var in self.crossword.variables:
            # Usa una copia (set) para poder eliminar elementos del original mientras itera
            for word in set(self.domains[var]):
                if len(word) != var.length:
                    self.domains[var].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        overlap = self.crossword.overlaps.get((x, y))

        # Si no hay solapamiento (no se cruzan), ya son consistentes
        if overlap is None:
            return False

        i, j = overlap

        for word_x in set(self.domains[x]):
            conflict = True
            for word_y in self.domains[y]:
                # Busca si existe al menos una palabra en Y que empate con la letra de X
                if word_x[i] == word_y[j]:
                    conflict = False
                    break
            
            # Si ninguna palabra en Y funciona con esta palabra de X, elimina la palabra de X
            if conflict:
                self.domains[x].remove(word_x)
                revised = True
                
        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs is None:
            queue = []
            # Agrega todas las combinaciones de variables que se cruzan
            for v1 in self.crossword.variables:
                for v2 in self.crossword.neighbors(v1):
                    queue.append((v1, v2))
        else:
            queue = list(arcs)

        while queue:
            x, y = queue.pop(0)
            
            # Si modifica el dominio de x, necesita revisar a sus otros vecinos
            if self.revise(x, y):
                if not self.domains[x]:
                    return False # El dominio se vació, no hay solución posible
                
                # Agrega a la cola los vecinos de x (excepto y)
                for z in self.crossword.neighbors(x) - {y}:
                    queue.append((z, x))
                    
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        # Verifica si todas las variables del crucigrama están en la asignación actual
        for var in self.crossword.variables:
            if var not in assignment:
                return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        used_words = set()

        for var, word in assignment.items():
            # 1. Todas las palabras deben ser únicas
            if word in used_words:
                return False
            used_words.add(word)

            # 2. Deben tener la longitud correcta (restricción unaria)
            if len(word) != var.length:
                return False

            # 3. No debe haber conflictos con los vecinos (restricción binaria)
            for neighbor in self.crossword.neighbors(var):
                if neighbor in assignment:
                    i, j = self.crossword.overlaps[var, neighbor]
                    if word[i] != assignment[neighbor][j]:
                        return False
                        
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        def count_ruled_out(val):
            count = 0
            for neighbor in self.crossword.neighbors(var):
                # Solo importan los vecinos que aún no tienen una palabra asignada
                if neighbor not in assignment:
                    i, j = self.crossword.overlaps[var, neighbor]
                    for neighbor_val in self.domains[neighbor]:
                        if val[i] != neighbor_val[j]:
                            count += 1
            return count

        # Ordena los valores del dominio basados en cuántas opciones eliminan para otros
        return sorted(list(self.domains[var]), key=count_ruled_out)

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned = [v for v in self.crossword.variables if v not in assignment]

        # Aplica la heurística MRV (Minimum Remaining Values) y Degree Heuristic.
        # Ordena primero por el número de vecinos de mayor a menor (Degree Heuristic)
        unassigned.sort(key=lambda var: len(self.crossword.neighbors(var)), reverse=True)
        # Luego ordena por la cantidad de palabras restantes en el dominio (MRV)
        # Python mantiene el orden relativo del sort anterior para resolver empates.
        unassigned.sort(key=lambda var: len(self.domains[var]))

        return unassigned[0] if unassigned else None

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # Caso base: Si la asignación está completa, la devuelve
        if self.assignment_complete(assignment):
            return assignment

        # Elige la siguiente variable a llenar
        var = self.select_unassigned_variable(assignment)

        # Prueba las palabras posibles para esta variable
        for val in self.order_domain_values(var, assignment):
            # Clona para simular la nueva asignación
            new_assignment = assignment.copy()
            new_assignment[var] = val

            # Si es consistente, se adentra en esa rama
            if self.consistent(new_assignment):
                assignment[var] = val
                result = self.backtrack(assignment)
                
                if result is not None:
                    return result
                
                # Si llega aquí, la elección llevó a un callejón sin salida, se retracta (backtrack)
                del assignment[var]

        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
