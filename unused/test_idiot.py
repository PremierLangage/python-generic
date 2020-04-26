from grader import grade_this

student_code = r"""
def f(n):
    b = "locale !"
    return a * n

n = input("coucou")
print(f(n))
"""

validation_code = r"""
# 1 - set execution environment
set_globals(a=3)
set_inputs(["3"])

# 2 - run code in current environment
run()

# 3 - assert about new state, outputs, etc.
assert_output("333\n")
assert_variable_values(n="3")

# 3' - alternatively, evaluate expressions in current environment
# (includes previous changes to global state, input consumption...)
run("f(9)")
assert_result(27)  # the result of evaluating "f(9)" should be 27
assert_no_global_change()  # global variables unchanged
"""


if __name__ == "__main__":
    grade, fb = grade_this(student_code, validation_code, globals())
    print(fb)
