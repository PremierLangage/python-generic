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


class CodeGrader:
    """Grader for python exercises.

    Receives a single piece of student code. Allows providing reference code
    for result or side effect comparison, and specifying initial global
    state.
    """
    
    def __init__(self, student_code: str,
                 reference_code: str = None,
                 initial_context: dict = None):
        """Build grader object.

        :param student_code: student code to evaluate.
        :param reference_code: (optional) reference code for comparison.
        :param initial_context: (optional) initial global namespace.
        """
        self.context = deepcopy(initial_context) if initial_context else {}
        self.student_code = student_code
        self.reference_code = reference_code

        # prepare variable for future global state (after code execution)
        self.state = None

    def exec_preamble(self, preamble):
        exec(preamble, self.context)
        del self.context['__builtins__']

    def exec_with_inputs(self, input_lines: Optional[List[str]] = None):
        """
        Run the student code with the specified lines of input available on
        standard input.

        :param input_lines: Lines of text available on standard input.
        :return: String printed on standard output.
        """
        self.state = deepcopy(self.context)
        out_stream = StringIO()
        self.state['input'] = lambda _: CodeGrader.my_input(input_lines)

        # TODO: check whether other stuff should be patched and possibly use
        #  a new patch-decorated function
        with mock.patch.object(sys, 'stdout', out_stream):
            exec(self.student_code, self.state)
        del self.state['__builtins__']
        return out_stream.getvalue(), self.state

    def eval_expression(self, expression, input_lines=None):
        """
        Evaluate the provided expression in the context of the stundent's code,
        with the specified lines of input available on standard input.

        :param expression: Expression to be evaluated.
        :param input_lines: Lines of text available on standard input.
        :return: tuple containing the expression's value, the string printed on
        standard output, and the final state.
        """

        # only execute the whole code if it has never been done
        # WARNING: assumes the code can be run with no input
        if self.state is None:
            self.exec_with_inputs(None)

        # mock the input function
        self.state['input'] = lambda _: CodeGrader.my_input(input_lines)

        # evaluate the expression mocking stdout printing
        out_stream = StringIO()
        with mock.patch.object(sys, 'stdout', out_stream):
            result = eval(expression, self.state)

        # cleanup final state for feedback
        del self.state['__builtins__']
        return result, out_stream.getvalue(), self.state

    @staticmethod
    def my_input(input_lines: List[str]):
        # TODO: check if it's better to mock sys.stdin directly
        if not input_lines:
            raise ValueError("No input to be read.")
        return input_lines.pop(0)


def __main():
    import textwrap

    code = """
    def f(n):
        b = "locale !"
        return a * n
    
    n = input("coucou")
    print(f(n))
    """

    preamble = """
    a = 3
    """

    code = textwrap.dedent(code)
    grader = CodeGrader(code)

    preamble = textwrap.dedent(preamble)
    grader.exec_preamble(preamble)

    outputs, final_state = grader.exec_with_inputs(["3"])
    print("La sortie est :", outputs)
    print(final_state)

    print(grader.eval_expression("f(9)"))


if __name__ == "__main__":
    __main()
