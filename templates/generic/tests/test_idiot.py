from test import TestSession

if __name__ == "__main__":
    import textwrap

    code = """
    def f(n):
        b = "locale !"
        return a * n

    n = input("coucou")
    print(f(n))
    """
    code = textwrap.dedent(code)

    # 1 - create a code runner object
    s = TestSession(code)
    # 2 - set execution environment
    s.set_globals(a=3)
    s.set_inputs(["3"])
    # 3 - run code in current environment
    s.run(values={'n': 4})
    # 4 - assert about new state, outputs, etc.
    s.assert_output("333\n")
    s.assert_variable_values(n="3")
    # 3' - alternatively, evaluate expressions in current environment
    # (includes previous changes to global state, input consumption...)
    s.run("f(9)")
    s.assert_result(27)  # the result of evaluating "f(9)" should be 27
    s.assert_no_global_change()  # global variables unchanged
    # 5 - display test results
    print(s.render())
