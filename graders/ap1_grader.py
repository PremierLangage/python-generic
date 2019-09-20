#!/usr/bin/env python3
#
# Authors:
#   Quentin Coumes <coumes.quentin@gmail.com>
#   Antoine Meyer <antoine.meyer@u-pem.fr>

import sys
from io import StringIO
from unittest import mock
from typing import *
from copy import deepcopy

from utils.ap1_utils import mock_input


# TODO: separate test results information from feedback formatting


def default_cmp(x, y):
    return x == y


class Test:
    def __init__(self, title: str, status: bool):
        self.title = title
        self.status = status

    def __str__(self):
        msg = "[OK] " if self.status else "[KO] "
        return msg + self.title


class TestGroup:
    def __init__(self, title: str):
        self.title = title
        self.tests = []

    def __str__(self):
        res = self.title + '\n'
        res += "\n".join(str(test) for test in self.tests)
        return res

    def append(self, test_or_test_group: Union[Test, 'TestGroup']):
        self.tests.append(test_or_test_group)


class CodeRunner:
    """Code runner for Python exercises.

    Instances store a piece of student code.
    Provides methods for code execution, simulating standard input and output
    if necessary and keeping track of global state changes.
    """
    
    def __init__(self, code: str):
        """Build CodeRunner object.

        :param code: student code to evaluate.
        """
        self.code = code

        # execution context
        self.previous_state = None
        self.current_state = {}
        self.inputs = []
        self.argv = []
        self.output = None
        self.result = None

        # history and feedback
        self.tests = TestGroup("main test group")
        self.test_group_stack = []

    """Setters for execution context."""

    def exec_preamble(self, preamble: str, **kwargs) -> NoReturn:
        exec(preamble, self.current_state, **kwargs)
        del self.current_state['__builtins__']

    def set_globals(self, **kwargs) -> NoReturn:
        self.previous_state = None
        self.current_state.update(kwargs)

    def set_state(self, state: dict) -> NoReturn:
        self.previous_state = None
        self.current_state = state

    def set_argv(self, argv: List[str]) -> NoReturn:
        self.argv = argv

    def set_inputs(self, inputs: List[str]) -> NoReturn:
        self.inputs = inputs

    """Feedback management."""

    def begin_test_group(self, title: str) -> NoReturn:
        tg = TestGroup(title)
        if self.test_group_stack:
            self.test_group_stack[-1].append(tg)
        else:
            self.tests.append(tg)
        self.test_group_stack.append(tg)

    def end_test_group(self) -> NoReturn:
        self.test_group_stack.pop()

    def record_test(self, test: Test) -> NoReturn:
        if self.test_group_stack:
            self.test_group_stack[-1].append(test)
        else:
            self.tests.append(test)

    """Code execution."""

    def run(self) -> NoReturn:
        """
        Run the student code with the specified lines of input available on
        standard input.

        :return: String printed on standard output, modified state.
        """
        self.previous_state = deepcopy(self.current_state)
        out_stream = StringIO()

        # TODO: check whether other stuff should be patched and possibly use
        #  a new patch-decorated function
        with mock_input(self.inputs, self.current_state):
            with mock.patch.object(sys, 'argv', self.argv):
                with mock.patch.object(sys, 'stdout', out_stream):
                    exec(self.code, self.current_state)

        # cleanup final state for feedback
        del self.current_state['__builtins__']

        # store generated outputs
        self.output = out_stream.getvalue()

    def evaluate(self, expression: str) -> Any:
        """
        Evaluate the provided expression in the context of the student's code,
        with the specified lines of input available on standard input.

        :param expression: expression to be evaluated.
        :return: the expression's value.
        """
        self.previous_state = deepcopy(self.current_state)
        out_stream = StringIO()

        # evaluate the expression mocking sys.argv and stdout printing
        with mock_input(self.inputs, self.current_state):
            with mock.patch.object(sys, 'argv', self.argv):
                with mock.patch.object(sys, 'stdout', out_stream):
                    self.result = eval(expression, self.current_state)

        # cleanup final state for feedback
        del self.current_state['__builtins__']

        # store generated outputs
        self.output = out_stream.getvalue()

    """Assertions."""
    # TODO: implement fail-fast mechanism

    def assert_output(self, output, _cmp=default_cmp) -> NoReturn:
        status = _cmp(output, self.output)

        msg = "assert_output: "
        if status:
            msg += "got correct output {}".format(repr(output))
        else:
            msg += "expected {}, got {}".format(repr(output), repr(self.output))

        self.record_test(Test(msg, status))

    def assert_result(self, value, _cmp: Callable = default_cmp):
        status = _cmp(value, self.result)

        msg = "assert_result: "
        if status:
            msg += "got correct result {}".format(repr(value))
        else:
            msg += "expected {}, got {}".format(repr(value), repr(self.result))

        self.record_test(Test(msg, status))

    def assert_variable_values(self, _cmp: Callable = default_cmp, **kwargs):
        missing_variables = []
        incorrect_msg_list = []

        for ident, value in kwargs.items():
            if ident not in self.current_state:
                missing_variables.append(ident)
            elif not _cmp(value, self.current_state[ident]):
                incorrect_msg_list.append(
                    "{} has value {} (should be {})".format(
                        ident, self.current_state[ident], value))

        msg = "assert_variable_values: "
        msg_list = []
        status = True
        if missing_variables:
            status = False
            msg_list.append("variable(s) {} missing".format(
                ", ".join(missing_variables)))
        if incorrect_msg_list:
            status = False
            msg_list.append("; ".join(incorrect_msg_list))
        if status:
            msg_list.append("; ".join("{} has value {}".format(ident, value)
                            for ident, value in kwargs.items()))
        msg += "; ".join(msg_list)

        self.record_test(Test(msg, status))

    def assert_no_global_change(self) -> NoReturn:
        modified_vars = [
            var for var in self.previous_state
            if var not in self.current_state
            or self.current_state[var] != self.previous_state[var]]

        modified_vars.extend(self.current_state.keys() -
                             self.previous_state.keys())

        msg = "assert_no_global_change: "
        status = len(modified_vars) == 0
        if status:
            msg += "no changed variables"
        else:
            msg += "changed variables: {}".format(modified_vars)

        self.record_test(Test(msg, status))


def _main():
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
    print(runner.tests)


if __name__ == "__main__":
    _main()
