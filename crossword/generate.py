import sys
from copy import deepcopy

from crossword import *

# I did this project during vacation with a bunch of kids screaming around me, so it is
# very possible that some parts of the code is sub-optimal and not particularly pretty
# I do not accept any responsibility if you suffer brain damage or have an
# aneurysm while reading the code below

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
        print()
        print("_"*self.crossword.width*2)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="|")
                else:
                    print("■", end="|")
            print()
        print("-"*self.crossword.width*2)

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
                        w, h = draw.textsize(letters[i][j], font=font)
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
        for var in self.domains:
            new_domain = self.domains[var].copy()
            for word in self.domains[var]:
                if var.length != len(word):
                    new_domain -= {word}
            self.domains[var] = new_domain

    def revise(self, x, y):
        revised = False

        def search_in_domain(domain, index, char, disallow):
            for word in domain:
                if word[index] == char and word != disallow:
                    return True
            return False

        if (x, y) in self.crossword.overlaps:
            new_domain = self.domains[x].copy()
            overlap = self.crossword.overlaps[(x, y)]
            for i in self.domains[x]:
                if not search_in_domain(self.domains[y], overlap[1], i[overlap[0]], i):
                    new_domain -= {i}
                    revised = True
            self.domains[x] = new_domain
        return revised

    def ac3(self, arcs=None):
        if arcs:
            queue = arcs
        else:
            queue = []
            for i in self.crossword.overlaps:
                if self.crossword.overlaps[i]:
                    queue.append(i)
            while queue:
                (x, y) = queue[-1]
                queue = queue[:-1]
                if self.revise(x, y):
                    if len(self.domains[x]) == 0:
                        return False
                    for i in self.crossword.neighbors(x) - {y}:
                        queue.append((i, x))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        return len(assignment) == len(self.domains)

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        if not assignment:
            return False
        for i in assignment:
            if i.length != len(assignment[i]):
                return False
            for j in assignment:
                if j == i:
                    continue
                overlap = self.crossword.overlaps[(i, j)]
                if overlap:
                    if assignment[i][overlap[0]] != assignment[j][overlap[1]]:
                        return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        domain = []
        for i in self.domains[var]:
            discarded = 0
            for j in self.crossword.neighbors(var):
                if j not in assignment:
                    overlap = self.crossword.overlaps[(var, j)]
                    for k in self.domains[j]:
                        if k[overlap[1]] != i[overlap[0]]:
                            discarded += 1
            domain.append((discarded, i))
        domain.sort(key = lambda x: x[0])
        final = []
        for i in domain:
            final.append(i[1])
        return final

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        best = [len(self.crossword.words) + 1, 0, []]
        for i in self.domains:
            if i not in assignment:
                length = self.domains[i].__len__()
                if best[0] > length:
                    neighbors = self.crossword.neighbors(i)
                    best[0] = length
                    best[2].append(i)
                    best[1] = len(neighbors)
                elif best[0] == length:
                    neighbors = self.crossword.neighbors(i)
                    if len(neighbors) == best[1]:
                        best[2].append(self.domains[i])
                    elif len(neighbors) < best[1]:
                        best[2] = [i]
                        best[1] = len(neighbors)

        return best[2][0]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        var = self.select_unassigned_variable(assignment)
        domain_values = self.order_domain_values(var, assignment)
        inferences = []
        domains_backup = deepcopy(self.domains)
        for i in domain_values:
            assignment[var] = i
            arcs = []
            self.domains[var] = {i}
            for j in self.crossword.neighbors(var):
                arcs.append(self.crossword.overlaps[(j, var)])
            if not self.ac3(arcs=arcs):
                continue
            inferences = self.infer(assignment)
            if self.consistent(assignment):
                result = self.backtrack(assignment)
                if result:
                    return result
            for j in inferences:
                assignment.pop(j)
        assignment.pop(var)
        self.domains = domains_backup
        return None

    def infer(self, assignment):
        inferred = []
        for i in self.domains:
            if i in assignment:
                continue
            val = self.domains[i]
            if len(val) == 1:
                inferred.append(i)
                assignment[i] = next(iter(val))
        return inferred

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
