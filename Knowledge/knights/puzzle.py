from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# --- CONOCIMIENTO GENERAL (Reglas del Juego) ---

# Reglas para A: (Es Caballero O Bribón) Y (No es ambos)
general_knowledge_A = And(
    Or(AKnight, AKnave),
    Not(And(AKnight, AKnave))
)

# Reglas para B
general_knowledge_B = And(
    Or(BKnight, BKnave),
    Not(And(BKnight, BKnave))
)

# Reglas para C
general_knowledge_C = And(
    Or(CKnight, CKnave),
    Not(And(CKnight, CKnave))
)


# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And(
    general_knowledge_A,

    # Lo que dijo A.
    # A es Caballero SI Y SOLO SI lo que dijo es verdad.
    # Dijo: "And(AKnight, AKnave)"
    Biconditional(AKnight, And(AKnight, AKnave))
)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
knowledge1 = And(
    general_knowledge_A,
    general_knowledge_B,

    # Lo que dijo A
    # Dijo: "And(AKnave, BKnave)"
    Biconditional(AKnight, And(AKnave, BKnave))
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
knowledge2 = And(
    general_knowledge_A,
    general_knowledge_B,

    # Lo que dijo A ("Somos del mismo tipo")
    # Significa: (Ambos Caballeros) O (Ambos Bribones)
    Biconditional(AKnight, Or(And(AKnight, BKnight), And(AKnave, BKnave))),

    # Lo que dijo B ("Somos de tipos diferentes")
    # Significa: (A Caballero y B Bribón) O (A Bribón y B Caballero)
    Biconditional(BKnight, Or(And(AKnight, BKnave), And(AKnave, BKnight)))
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B then says "C is a knave."
# C says "A is a knight."
knowledge3 = And(
    general_knowledge_A,
    general_knowledge_B,
    general_knowledge_C,

    # Lo que dijo B: "A dijo 'Soy un Bribón'"
    # Nadie puede decir realmente "Soy un Bribón".
    # - Un Caballero no mentiría diciendo que es Bribón.
    # - Un Bribón no diría la verdad diciendo que es Bribón.
    # Por lo tanto, A nunca pudo haber dicho esa frase.
    # La frase "A dijo que es Bribón" implica que A afirmó: (AKnight si y solo si AKnave)
    # B es Caballero SI Y SOLO SI (A es Caballero <-> A es Bribón)
    Biconditional(BKnight, Biconditional(AKnight, AKnave)),

    # Lo que dijo B: "C es un Bribón"
    Biconditional(BKnight, CKnave),

    # Lo que dijo C: "A es un Caballero"
    Biconditional(CKnight, AKnight),
    
    # Aunque A dijo ("Soy Caballero" o "Soy Bribón"), esa información ya está implícita en la lógica de que B está mintiendo o diciendo la verdad sobre lo que A dijo
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
