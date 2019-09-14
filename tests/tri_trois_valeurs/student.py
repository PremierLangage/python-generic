from graders.ap1_grader import CodeGrader
from itertools import permutations

code = """
if a < b:
    if b < c:
        print(a, b, c)
    else:
        if a < c:
            print(a, c, b)
        else:
            print(c, a, b)
else:
    if a < c:
        print(b, a, c)
    else:
        if b < c:
            print(b, c, a)
        else:
            print(c, b, a)
"""

# TODO: nettoyer et rendre plus générique (fonctions auxiliaires permettant
#  de lancer des tests entrée/sortie plus facilement), structurer le feedback

g = CodeGrader(code)

all_permutations = (list(permutations([1, 2, 3]))
                    + list(permutations([1, 1, 2]))
                    + list(permutations([1, 2, 2]))
                    + [[1, 1, 1]])

for p in all_permutations:
    g.exec_preamble('a, b, c = {}'.format(p))
    res, state = g.exec_with_inputs([])
    assert(res.strip() == " ".join(map(str, sorted(p))))

print("done")
