import os
import random
import re
import sys
from numpy.random import choice
import matplotlib

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
    if corpus[page] == set():
        return {x: 1/len(corpus) for x in corpus}
    damping_probability = (1-damping_factor)/len(corpus)
    probabilities = {x: damping_probability for x in corpus}
    for p in corpus[page]:
        if p != page:
            probabilities[p] += damping_factor/corpus[page].__len__()
    return probabilities


def sample_pagerank(corpus, damping_factor, n):
    counter = {x: 0 for x in corpus}
    pages = list(corpus.keys())
    page = random.choice(pages)
    for r in range(n):
        counter[page] += 1
        model = transition_model(corpus, page, damping_factor)
        prob = tuple(model[x] for x in pages)
        page = pages[choice(len(pages), p=prob)]

    pageranks = {p: counter[p]/n for p in pages}
    return pageranks


def iterate_pagerank(corpus, damping_factor):
    epsilon = 0.001
    pageranks = {x: 1/len(corpus) for x in corpus}
    linkedby = {}
    damping_probability = (1-damping_factor)/len(corpus)

    for i in corpus:
        linkedby[i] = set()
        for j in corpus:
            if j != i and i in corpus[j]:
                linkedby[i].add(j)

    change = 1
    while change > epsilon:
        pageranks_cp = pageranks.copy()
        for page in corpus:
            pageranks[page] = damping_probability
            for i in linkedby[page]:
                pageranks[page] += damping_factor * pageranks_cp[i]/corpus[i].__len__()
            if abs(pageranks[page] - pageranks_cp[page]) < change:
                change = abs(pageranks[page] - pageranks_cp[page])

    return pageranks


if __name__ == "__main__":
    main()
