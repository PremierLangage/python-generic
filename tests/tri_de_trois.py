from graders.ap1_grader import CodeRunner
from itertools import permutations

student_code = """
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

g = CodeRunner(student_code)

g.begin_test_group("Tris d'éléments distincts")
for x, y, z in permutations((1, 2, 3)):
    # TODO: display global change in feedback
    g.set_globals(a=x, b=y, c=z)
    g.run()
    g.assert_output("1 2 3\n")
    g.assert_no_global_change()
g.end_test_group()

"""
g.begin_test_group("Tris avec un doublon (1/2)")
for x, y, z in permutations(("un", "un", "deux")):
    g.set_globals(a=x, b=y, c=z)
    g.run()
    g.assert_output("deux un un\n")
    g.assert_no_global_change()
g.end_test_group()

g.begin_test_group("Tris avec un doublon (2/2)")
for x, y, z in permutations((1, 2, 2)):
    g.set_globals(a=x, b=y, c=z)
    g.run()
    g.assert_output("1 2 2\n")
    g.assert_no_global_change()
g.end_test_group()

g.begin_test_group("Tris de trois valeurs identiques")
g.set_globals(a=1, b=1, c=1)
g.run()
g.assert_output("1 1 1\n")
g.assert_no_global_change()
g.end_test_group()
"""

print(g.tests)
