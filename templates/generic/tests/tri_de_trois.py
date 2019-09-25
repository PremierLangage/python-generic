from grader import grade_this

student_code = r"""
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

validation_code = r"""
from itertools import permutations

begin_test_group("Tris d'éléments distincts")
for x, y, z in permutations((1, 2, 3)):
    d = {'a': x, 'b': y, 'c': z}
    run(title="tri avec a, b, c = {}, {}, {}".format(x, y, z),
          globals=d,
          output="1 2 3\n",
          allow_global_change=False)
end_test_group()

begin_test_group("Tris avec un doublon et un plus petit")
for x, y, z in set(permutations(("un", "un", "deux"))):
    set_globals(a=x, b=y, c=z)
    run()
    assert_output("deux un un\n")
    assert_no_global_change()
end_test_group()

begin_test_group("Tris avec un doublon et un plus grand")
for x, y, z in set(permutations((1, 1, 2))):
    set_globals(a=x, b=y, c=z)
    run()
    assert_output("1 1 2\n")
    assert_no_global_change()
end_test_group()

begin_test_group("Tri de trois valeurs identiques")
set_globals(a=1, b=1, c=1)
run()
assert_output("1 1 1\n")
assert_no_global_change()
end_test_group()
"""


if __name__ == "__main__":
    grade, fb = grade_this(student_code, validation_code)
    print(fb)
