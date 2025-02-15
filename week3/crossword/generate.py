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
        for variable in self.crossword.variables:
            for word in self.crossword.words:
                if len(word) != variable.length:
                    self.domains[variable].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        import copy
        overlapIndex = self.crossword.overlaps[x, y] #figure out what to remove
        revised = False
        doms = copy.deepcopy(self.domains)
        if overlapIndex:
            x_o, y_o = overlapIndex
            for x_val in doms[x]:
                match_ = False
                for y_val in doms[y]:
                    if x_val[x_o] == y_val[y_o]:
                        match_ = True
                        break
                if match_ == True:
                    continue
                else:
                    self.domains[x].remove(x_val)
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
        #finally read the lecture notes lol
        from collections import deque
        if arcs is None:
            arcs = deque()
            for variable in self.crossword.variables:
                for variable2 in self.crossword.neighbors(variable):
                    arcs.appendleft((variable, variable2))
        else:
            arcs = deque(arcs)

        while arcs:
            x, y = arcs.pop()
            if self.revise(x, y): 
                if len(self.domains[x]) == 0:
                    return False
                for z in self.crossword.neighbors(x) - {y}:
                    arcs.appendleft((z, x))

        return True
            


    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for variable in self.crossword.variables:
            if variable not in assignment.keys():
                return False
            elif assignment[variable] not in self.crossword.words:
                return False
        return True
        
    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        for variable in assignment:
            word = assignment[variable]
            if len(word) != variable.length:
                return False
            for variable2 in assignment:
                word2 = assignment[variable2]
                if variable != variable2:
                    if word == word2:
                        return False
                    if self.crossword.overlaps[variable, variable2] is not None:
                        x, y = self.crossword.overlaps[variable, variable2]
                        if word[x] != word2[y]:
                            return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        neighbours = self.crossword.neighbors(var)
        for variable in assignment:
            if variable in neighbours: #we do not care about it if its already done
                neighbours.remove(variable)

        number_of_words_kicked = {}
        for variable in self.domains[var]:
            booted = 0
            for neighbour in neighbours:
                for variable2 in self.domains[neighbour]:
                    overlap = self.crossword.overlaps[var, neighbour]
                    if overlap:
                        x, y = overlap
                        if variable[x] != variable2[y]:
                            booted += 1
            number_of_words_kicked[variable] = booted
        number_of_words_kicked = sorted(number_of_words_kicked.items(), key=lambda x: x[1])
        words_sorted = [key[0] for key in number_of_words_kicked]
        return words_sorted
        
    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned = []
        for variable in self.crossword.variables:
            if variable not in assignment:
                unassigned.append([variable, len(self.domains[variable]), len(self.crossword.neighbors(variable))])
        if len(unassigned)>0:
            unassigned.sort(key=lambda x: (x[1], -x[2]))
            return unassigned[0][0]

        return None

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        variable = self.select_unassigned_variable(assignment)
        for val in self.order_domain_values(variable, assignment):
            assignment[variable] = val
            if self.consistent(assignment):
                result = self.backtrack(assignment)
                if result is None: assignment[variable] = None
                else: return result
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
