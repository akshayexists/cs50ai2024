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

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait. 
    """
    #set initial probability to 1
    probability = 1

    for person in people:

        #setting number of genes in `genenumber`
        genenumber = None
        if person in one_gene:
            genenumber = 1
        elif person in two_genes:
            genenumber = 2
        else:
            genenumber = 0
        
        #setting presence or absence of the trait in `trait`
        trait = None
        if person in have_trait:
            trait = True
        else:
            trait = False
        
        #get probability of given genenumber
        geneprob = PROBS["gene"][genenumber]
        traitprob = PROBS['trait'][trait]

        #checking for parents
        if people[person]["father"] == None:
            probability = probability * geneprob * traitprob
        else:
            #parents exist
            mother = people[person]["mother"]
            father = people[person]["father"]
            probinherit = {}

            #set up probability of inheritance
            for parent in [mother, father]:
                num = None
                if parent in one_gene:
                    num = 1
                elif parent in two_genes:
                    num = 2
                else:
                    num = 0
                percentage = 0
                if num == 0:
                    percentage += PROBS["mutation"]
                elif num == 1:
                    percentage += 0.5
                else:
                    percentage += 1-PROBS["mutation"]

                probinherit[parent] = percentage
            
            #figure out probability of given event
            if genenumber == 0:
                probability = probability * (1-probinherit[father]) * (1-probinherit[mother])
            elif genenumber == 1:
                probability = probability * ((1-probinherit[mother])*probinherit[father] + (1-probinherit[father])*probinherit[mother])
            else:
                probability = probability * probinherit[mother] * probinherit[father]
            
            probability *= traitprob
    return probability
        
            
        


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    The function accepts five values as input: probabilities, one_gene, two_genes, have_trait, and p.
        probabilities is a dictionary of people as described in the “Understanding” section. Each person is mapped to a "gene" distribution and a "trait" distribution.
        one_gene is a set of people with one copy of the gene in the current joint distribution.
        two_genes is a set of people with two copies of the gene in the current joint distribution.
        have_trait is a set of people with the trait in the current joint distribution.
        p is the probability of the joint distribution.
    For each person person in probabilities, the function should update the probabilities[person]["gene"] distribution and probabilities[person]["trait"] distribution by adding p to the appropriate value in each distribution. All other values should be left unchanged.
    For example, if "Harry" were in both two_genes and in have_trait, then p would be added to probabilities["Harry"]["gene"][2] and to probabilities["Harry"]["trait"][True].
    The function should not return any value: it just needs to update the probabilities dictionary.
    """
    for person in probabilities:
        #get number of genes for person
        genenumber = None
        if person in one_gene:
            genenumber = 1
        elif person in two_genes:
            genenumber = 2
        else:
            genenumber = 0
        probabilities[person]["gene"][genenumber] += p
        #get trait status
        if person in have_trait:
            trait = True
        else:
            trait = False
        probabilities[person]["trait"][trait] += p

def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    normalisation = probabilities.copy()
    items = ["gene", "trait"]
    for person in probabilities:
        for item in items:
            summed = sum(probabilities[person][item].values())
            for thing in probabilities[person][item]:
                val = probabilities[person][item][thing]
                normalized_val = val / summed
                normalisation[person][item][thing] = normalized_val  
        
    


if __name__ == "__main__":
    main()
