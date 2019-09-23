from coderunner import CodeRunner

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
    runner = CodeRunner(code)
    # 2 - set execution environment
    runner.set_globals(a=3)
    runner.set_inputs(["3"])
    # 3 - run code in current environment
    runner.run()
    # 4 - assert about new state, outputs, etc.
    runner.assert_output("333\n")
    runner.assert_variable_values(n="3")
    # 3' - alternatively, evaluate expressions in current environment
    # (includes previous changes to global state, input consumption...)
    runner.evaluate("f(9)")
    runner.assert_result(27)  # the result of evaluating "f(9)" should be 27
    runner.assert_no_global_change()  # global variables unchanged
    # 5 - display test results
    # TODO: needs work
    for test in runner.tests:
        print(test.render())
