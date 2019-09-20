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
                    result = eval(expression, self.current_state)

        # cleanup final state for feedback
        del self.current_state['__builtins__']

        # store generated outputs
        self.output = out_stream.getvalue()

        return result

    """Assertions."""
    # TODO: implement fail-fast mechanism

    def assert_output(self, output, cmp=None) -> NoReturn:
        if cmp is None:
            def cmp(x, y):
                return x == y

        status = cmp(output, self.output)

        self.record_test(
            Test(
                "assert_output: expected {}, got {}".format(
                    repr(output), repr(self.output)),
                status
            )
        )

    def assert_no_global_change(self) -> NoReturn:
        modified_vars = [
            var for var in self.previous_state
            if var not in self.current_state
            or self.current_state[var] != self.previous_state[var]]

        modified_vars.extend(self.current_state.keys() -
                             self.previous_state.keys())

        if modified_vars:
            msg = "changed variables: {}".format(modified_vars)
            status = False
        else:
            msg = "no changed variables"
            status = True

        self.record_test(
            Test("assert_no_global_change: {}".format(msg), status)
        )


def __main():
    import textwrap

    code = """
    def f(n):
        b = "locale !"
        return a * n
    
    n = input("coucou")
    print(f(n))
    """

    code = textwrap.dedent(code)

    runner = CodeRunner(code)

    runner.set_globals(a=3)
    runner.set_inputs(["3", "4"])

    runner.run()
    print("La sortie est :", runner.output)
    print(runner.current_state)

    print(runner.evaluate("f(9)"))
    print("La sortie est :", runner.output)
    print(runner.current_state)


if __name__ == "__main__":
    __main()
