import nltk
import sys

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

"""
S -> N V | N V Det N P N | N V Det N
S -> N V P Det Adj N Conj N V | Det N V Det Adj N | N V P N
S -> N Adv V Det N Conj N V P Det N Adv
S -> N V Adv Conj V Det N
S -> N V Det Adj V P N Conj V N P Det Adj N
S -> N V Det Adj Adj Adj N P Det N P N
"""

NONTERMINALS = """
S -> SECTION Conj SECTION | SECTION
SECTION -> NP VP | NP Adv VP | VP | VP NP | NP VP NP
NP -> N | Det N | Det AP N | P NP | NP P NP | NP Adv
VP -> V | VP Adv | VP Det AP VP | VP Det NP
AP -> Adj | AP Adj
"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """
    #i was getting some error on check50, not sure why it needs me to download punkt, but a little searching on stackoverflow helped me figure this one out https://stackoverflow.com/questions/37101114/what-to-download-in-order-to-make-nltk-tokenize-word-tokenize-work
    nltk.download('punkt_tab')
    tokens = nltk.tokenize.word_tokenize(sentence)
    processed = []
    #checking whether there's a letter and if its a letter, we make it lowercase, ignoring numbers practically
    for word in tokens:
        word=word.lower()
        if any(char.isalpha() for char in word):
            processed.append(word)
    return processed
    

def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    #figuring this one out took a loooooong time, had to look through the nltk library for an answer :( https://www.nltk.org/howto/tree.html#parented-trees
    traversableTree = nltk.tree.ParentedTree.convert(tree)
    answer = []
    # I tried adding the verifying child subtrees logic in here directly but i couldn't make it work so i moved it to another feeder function
    for subtree in traversableTree.subtrees():
        if subtree.label() == "NP" and verifychildren(subtree):
            answer.append(subtree)
                
    return answer

def verifychildren(subtree):
    """
    we're gonna check each child of the given subtree to see whether it contains any other NP as subtrees
    Args:
        subtree (nltk tree): should be a parented subtree with children
    """
    num=0
    for child in subtree.subtrees():
        if child.label() == "NP":
            num += 1
    #this took a while but i didnt realise the condition has to be count > 1, just returning when NP hit 1 caused some issues due to how .subtree() works :(
    if num>1: return False
    return True
    

if __name__ == "__main__":
    main()
