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

def get_info(person, one_gene, two_genes, have_trait):
    trait = person in have_trait
    gene = 0
    if person in one_gene:
        gene = 1
    elif person in two_genes:
        gene = 2
    return gene, trait


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """

    def generate_prob(m_gene, f_gene, gene_combination):
        if m_gene == 1:
            m_prob = 0.5
        else:
            m_prob = 0.99 if m_gene/2 == gene_combination[0] else 0.01

        if f_gene == 1:
            f_prob = 0.5
        else:
            f_prob = 0.99 if f_gene/2 == gene_combination[1] else 0.01
        return m_prob * f_prob

    probabilities = []

    for person in people:
        gene, trait = get_info(person, one_gene, two_genes, have_trait)
        if people[person]["mother"] and people[person]["father"]:
            mother_gene, foo = get_info(people[person]["mother"], one_gene, two_genes, have_trait)
            father_gene, foo = get_info(people[person]["father"], one_gene, two_genes, have_trait)
            if gene == 1:
                gene_prob = generate_prob(mother_gene, father_gene, (0, 1)) + generate_prob(mother_gene, father_gene, (1, 0))
            else:
                gene_prob = generate_prob(mother_gene, father_gene, (gene/2, gene/2))
        else:
            gene_prob = PROBS["gene"][gene]
        probabilities.append(gene_prob * PROBS["trait"][gene][trait])

    joint_prob = 1
    for p in probabilities:
        joint_prob *= p

    return joint_prob


def update(probabilities, one_gene, two_genes, have_trait, p):
    for person in probabilities:
        gene, trait = get_info(person, one_gene, two_genes, have_trait)
        probabilities[person]["gene"][gene] += p
        probabilities[person]["trait"][trait] += p


def normalize(probabilities):
    for person in probabilities:
        psum = 0
        for gene in probabilities[person]["gene"]:
            psum += probabilities[person]["gene"][gene]
        gene_ratio = 1/psum
        for gene in probabilities[person]["gene"]:
            probabilities[person]["gene"][gene] *= gene_ratio

        psum = 0
        for trait in probabilities[person]["trait"]:
            psum += probabilities[person]["trait"][trait]
        trait_ratio = 1/psum
        for trait in probabilities[person]["trait"]:
            probabilities[person]["trait"][trait] *= trait_ratio


if __name__ == "__main__":
    main()

