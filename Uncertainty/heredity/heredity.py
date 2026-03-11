import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.
    """
    # Empiezar con una probabilidad total del 100% (1.0)
    probability = 1.0

    # Evaluar a cada persona en el diccionario 'people'
    for person in people:
        
        # 1. Averiguar cuántos genes mutados tiene esta persona
        if person in two_genes:
            gene_count = 2
        elif person in one_gene:
            gene_count = 1
        else:
            gene_count = 0

        # 2. Averiguar si la persona tiene el rasgo (trait) o no
        has_trait = person in have_trait

        # 3. Calcular la probabilidad de que tenga esa cantidad de genes
        if people[person]["mother"] is None and people[person]["father"] is None:
            # Si no se conoce a sus padres, se usa la probabilidad general de la población
            gene_prob = PROBS["gene"][gene_count]
        else:
            # Si se conoce a sus padres, se ve que probabilidad hay de que le pasen el gen
            mother = people[person]["mother"]
            father = people[person]["father"]
            
            passing_probs = {}
            for parent in [mother, father]:
                # Probabilidad de que este padre pase el gen mutado
                if parent in two_genes:
                    # Si tiene 2, casi seguro lo pasa (menos el 1% de que mute y no lo pase)
                    passing_probs[parent] = 1 - PROBS["mutation"]
                elif parent in one_gene:
                    # Si tiene 1, es un volado (50%)
                    passing_probs[parent] = 0.5
                else:
                    # Si no tiene el gen, solo lo pasa si ocurre la mala suerte de una mutación (1%)
                    passing_probs[parent] = PROBS["mutation"]

            m_prob = passing_probs[mother]
            f_prob = passing_probs[father]

            # Ahora se calcula la probabilidad exacta dependiendo de los genes que tiene el hijo
            if gene_count == 2:
                # Recibe el gen de la madre Y del padre
                gene_prob = m_prob * f_prob
            elif gene_count == 1:
                # Lo recibe de la madre y no del padre, O del padre y no de la madre
                gene_prob = (m_prob * (1 - f_prob)) + ((1 - m_prob) * f_prob)
            else:
                # No lo recibe ni de la madre ni del padre
                gene_prob = (1 - m_prob) * (1 - f_prob)

        # 4. Calcular la probabilidad de mostrar el rasgo, dado el número de genes que tiene
        trait_prob = PROBS["trait"][gene_count][has_trait]

        # 5. Multiplicar estas probabilidades al total
        probability *= (gene_prob * trait_prob)

    return probability


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    """
    # Recorrer a cada persona en nuestro diccionario de probabilidades
    for person in probabilities:
        
        # Ver cuántos genes tiene en este escenario
        if person in two_genes:
            gene_count = 2
        elif person in one_gene:
            gene_count = 1
        else:
            gene_count = 0

        # Ver si tiene el rasgo en este escenario
        has_trait = person in have_trait

        # Sumar la probabilidad 'p' al contador de esta persona
        probabilities[person]["gene"][gene_count] += p
        probabilities[person]["trait"][has_trait] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:
        
        # Ajustar las probabilidades de los genes para que sumen 1 (100%)
        gene_total = sum(probabilities[person]["gene"].values())
        for g in probabilities[person]["gene"]:
            probabilities[person]["gene"][g] /= gene_total

        # Ajustar las probabilidades de los rasgos para que sumen 1 (100%)
        trait_total = sum(probabilities[person]["trait"].values())
        for t in probabilities[person]["trait"]:
            probabilities[person]["trait"][t] /= trait_total


if __name__ == "__main__":
    main()
