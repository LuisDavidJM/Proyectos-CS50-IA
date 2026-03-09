import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.
    """
    prop_dist = {}
    N = len(corpus)
    links = corpus[page]

    # Caso 1: La página no tiene links salientes (Dead End).
    # Matemáticamente, se asume que tiene un link a todas las páginas (incluyéndose a sí misma).
    if len(links) == 0:
        for p in corpus:
            prop_dist[p] = 1 / N
    
    # Caso 2: La página tiene links.
    else:
        # Probabilidad base (1 - d) de saltar a CUALQUIER página al azar
        for p in corpus:
            prop_dist[p] = (1 - damping_factor) / N
        
        # Probabilidad adicional (d) de navegar hacia los links específicos de esta página
        for link in links:
            prop_dist[link] += damping_factor / len(links)

    return prop_dist


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.
    """
    # Inicializa el conteo de visitas a cada página
    counts = {p: 0 for p in corpus}
    
    # 1. El primer sample se elige de forma completamente aleatoria
    current_page = random.choice(list(corpus.keys()))
    counts[current_page] += 1

    # 2. Genera los siguientes n-1 samples basados en la Cadena de Markov
    for _ in range(n - 1):
        # Obtiene la distribución de probabilidad para el estado (página) actual
        model = transition_model(corpus, current_page, damping_factor)
        
        # random.choices permite elegir elementos basados en pesos (probabilidades)
        # Retorna una lista, por lo que se toma el índice [0]
        pages = list(model.keys())
        probabilities = list(model.values())
        
        current_page = random.choices(pages, weights=probabilities, k=1)[0]
        counts[current_page] += 1

    # Convierte los conteos brutos a una proporción (probabilidad final)
    pagerank = {p: count / n for p, count in counts.items()}
    return pagerank


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.
    """
    N = len(corpus)
    # Inicializa todos los PageRanks en 1 / N
    pr = {p: 1 / N for p in corpus}
    new_pr = {}
    
    # Umbral de convergencia
    THRESHOLD = 0.001

    while True:
        max_change = 0

        # Calcula el nuevo PageRank para cada página 'p'
        for p in corpus:
            link_sum = 0
            
            # Busca qué páginas 'i' tienen un link hacia 'p'
            for i in corpus:
                # Condición especial: Si la página 'i' no tiene links a nadie, se asume que tiene links a TODAS las páginas (incluida 'p')
                if len(corpus[i]) == 0:
                    link_sum += pr[i] / N
                # Si la página 'i' realmente enlaza a 'p'
                elif p in corpus[i]:
                    link_sum += pr[i] / len(corpus[i])

            # Aplica la fórmula matemática
            new_pr[p] = (1 - damping_factor) / N + damping_factor * link_sum

        # Verifica si alguna página superó el umbral de cambio
        for p in corpus:
            change = abs(new_pr[p] - pr[p])
            if change > max_change:
                max_change = change

        # Actualiza el diccionario principal para la siguiente iteración
        pr = new_pr.copy()

        # Si el cambio máximo en esta iteración es menor o igual al umbral, se converge
        if max_change <= THRESHOLD:
            break

    return pr


if __name__ == "__main__":
    main()