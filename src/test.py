import importlib.util

import jinja2
import operator
import sys

from ast_analyzer import AstAnalyzer
from copy import deepcopy
from inspect import getfullargspec
from io import StringIO
from mockinput import mock_input
from recursion_detector import performs_recursion
from typing import *
from unittest import mock

# _default_template_dir = ''
_default_template_dir = 'templates/jinja/'
_default_test_template = _default_template_dir + 'testitem.html'
_default_group_template = _default_template_dir + 'testgroup.html'

_default_params = {
    "verbose_inputs": True,
    "report_success": True,
    "group_fail_fast": True,
    "test_fail_fast": True,
}

_excluded_globals = {"__name__", "__doc__", "__package__",
                     "__loader__", "__spec__", "__builtins__"}


def _unidiff_output(expected, actual):
    """
    Helper function. Returns a string containing the unified diff of two
    multiline strings. Thanks https://stackoverflow.com/a/845432/4206331
    """

    import difflib
    expected = expected.splitlines(1)
    actual = actual.splitlines(1)
    diff = difflib.unified_diff(actual, expected,
                                fromfile='Affichage obtenu',
                                tofile='Affichage attendu')
    return ''.join(diff)


def _compare_namespaces(previous, current):
    """
    Computes the difference between two namespaces received as dicts.

    Dictionary `previous` represents an initial namespace, `current` a current
    one. 

    :return: tuple `(added, deleted, modified, inputs)`, where:
        - `added` is a dictionary mapping new identifiers to their values;
        - `deleted` is a list of deleted identifiers;
        - `modified` is a dictionary mapping existing identifiers to their
        (new) values.
    """
    deleted = list(previous.keys() - current.keys())
    modified = {var: (previous[var], current[var])
                for var in previous.keys() & current.keys() - _excluded_globals
                if previous[var] != current[var]}
    added = {var: current[var]
             for var in current.keys() - previous.keys() - _excluded_globals}
    return added, deleted, modified


def _argument_dict(argnames, args, kwargs):
    dic = {name: deepcopy(value)
           for name, value in zip(argnames, args)}
    dic.update({name: deepcopy(value)
                for name, value in kwargs.items()})
    return dic


def _expression_from_call(funcname, args, kwargs):
    argstr = ", ".join(str(arg) for arg in args)
    if kwargs:
        argstr += ", " + ", ".join(f'{name}={val}'
                                   for name, val in kwargs.items())
    return f"{funcname}({argstr})"


class GraderError(Exception):
    """Exception raised when an unforeseen error due to the exercise author
    occurs. """
    pass


class StopGrader(Exception):
    """Exception raised when the fail_fast parameter is set for some Test
    instance and an assertion fails."""
    pass


class TestSession:
    """
    Gather Test or TestGroup instances inside a session.

    TestSession instances manage test succession, group creation and closure,
    global parameters, and global grading.
    """

    def __init__(self, code: str, **params):
        """
        Initialize TestSession instance.

        :param code: Main code to test.
        :param params: Global session parameters. Currently allowed keys are:
            - report_success (bool, defaults to True): whether or not to
              report passed assertions;
            - fail_fast (bool, defaults to True): whether or not to stop after
              the first error.
        """
        self.history: List[Union[Test, TestGroup]] = []
        self.current_test: Optional[Test] = None
        self.previous_test: Optional[Test] = None
        self.current_test_group: Optional[TestGroup] = None
        self.analyzer: Optional[AstAnalyzer] = None
        self.test_number = 0

        self.code = code
        self.module = None

        self.params = _default_params.copy()
        self.params.update(params)

    """Group /test management."""

    def begin_test_group(self, title: str, **params) -> NoReturn:
        """
        Open a new test group.

        :param title: New test group's title.
        """
        self.cleanup()
        group_params = dict(self.params)
        group_params.update(params)
        self.current_test_group = TestGroup(title, **group_params)
        self.history.append(self.current_test_group)

    def end_test_group(self) -> NoReturn:
        """
        Close the current test group.
        """
        self.current_test_group = None

    def begin_test(self, title="", weight=1, keep_state=True, **params):
        if self.current_test is not None:
            self.end_test()

        self.test_number += 1

        if "state" not in params or params["state"] is None:
            params["state"] = {}
        if self.previous_test is not None and keep_state:
            previous_state = self.previous_test.current_state
            params["state"].update({key: deepcopy(val)
                                    for key, val in previous_state.items()})

        test_params = dict(self.params)
        if self.current_test_group is not None:
            test_params.update(self.current_test_group.params)
        test_params.update(params)

        self.current_test = Test(self, self.test_number,
                                 weight=weight, title=title,
                                 **test_params)

    def end_test(self):
        if self.current_test is None:
            raise GraderError("No test to end")

        if self.current_test_group:
            self.current_test_group.append(self.current_test)
            self.current_test_group.update_status(self.current_test.status)
        else:
            self.history.append(self.current_test)

        self.previous_test = self.current_test
        self.current_test = None

    def cleanup(self):
        if self.current_test is not None:
            self.end_test()
        if self.current_test_group is not None:
            self.end_test_group()

    """ Predefined tests """

    def test(self,
             # execution target
             expression=None, force_reload=False,
             funcname=None, args=None, kwargs=None,
             # description args
             title="", descr="", hint="", weight=1,
             # context args
             state=None, inputs=None, argv=None,
             # assertion args
             exception=None, values=None, types=None,
             output=None, outcmp=operator.eq,
             result=NoReturn, rescmp=operator.eq,
             allow_arg_change=True, allow_global_change=True,
             detect_recursion=False):
        """
        Starts a new test based on provided parameters.
        
        This method manages multiple optional arguments allowing it to
        control many execution settings. Arguments are of three kinds:
        context arguments which modify the execution's context, description
        arguments, and assertion arguments which entail automatic assertions
        on the execution.

        For details on the allowed arguments, see `parse_description_args`,
        `parse_context_args` and `parse_assertion_args`.

        :param expression: Expression to be evaluated (optional).
        """
        if self.current_test is not None:
            self.end_test()

        if state is None:
            state = {}
        if (self.previous_test is not None
                and self.params.get("keep_state", True)):
            pre = self.previous_test.current_state
            state.update(deepcopy(pre))

        test_params = self.params.copy()
        if self.current_test_group is not None:
            test_params.update(self.current_test_group.params)

        self.test_number += 1
        self.current_test = Test(self, self.test_number,
                                 weight=weight, title=title,
                                 **test_params)

        test = Test(self, self.test_number,
                    title=title, descr=descr, hint=hint, weight=weight,
                    state=state, inputs=inputs, argv=argv,
                    **self.params)
        self.current_test = test

        # Execute student code if required
        if force_reload or self.module is None:
            self.current_test.execute_source()

        # What should we do?
        if expression and funcname:
            raise GraderError(
                "Ne pas spécifier à la fois expression et funcname")
        elif expression:
            if not title:
                test.set_default_title(expression)
            test.expression = expression
            test.evaluate(expression)
        elif funcname:
            if kwargs is None:
                kwargs = {}
            expression = _expression_from_call(funcname, args, kwargs)
            if not title:
                test.set_default_title(expression)
            test.expression = expression
            test.call_function(funcname, args, kwargs)
        elif result is not NoReturn:
            raise GraderError("Vérification du résultat demandée, "
                              "mais pas d'expression ni d'appel à évaluer")

        # manage exceptions
        if exception is not None:
            # if parameter exception=SomeExceptionClass is passed, silently
            # check it is indeed raised
            self.assert_exception(exception)
        else:
            # unless some exception is explicitly expected, forbid them
            self.assert_no_exception()
        # check for evaluation or call result
        if result is not NoReturn:
            self.assert_result(result, rescmp)
        # check for standard output
        if output is not None:
            self.assert_output(output, outcmp)
        # check global values
        if values is not None:
            # for now we have no facility to check that some variable was
            # deleted, we only check that some variables exist
            self.assert_variable_values(**values)
        if types is not None:
            # for now we have no facility to check that some variable was
            # deleted, we only check that some variables exist
            self.assert_variable_types(**types)
        if not allow_global_change:
            # forbid changes to global variables
            self.assert_no_global_change()
        if funcname and not allow_arg_change:
            # forbid changes to mutable arguments (only valid for calls)
            self.assert_no_arg_change()
        if (funcname or expression) and detect_recursion:
            # detect recursion (only valid for calls or expressions)
            self.current_test.detect_recursion(funcname, args, kwargs)
            self.assert_previous_recursion()

    def test_call(self, funcname, *args,
                  kwargs=None,
                  reffunc=None,
                  result=...,
                  **params):
        """
        Test the call `funcname(*args, **kwargs)`.

        The call's result is either compared to `result` or to the result of
        the function `reffunc`. One or the other must be provided.

        Parameter `reffunc` should be a callable object with no side-effects
        **at all**.

        Unless otherwise specified in `params`, asserts the absence of
        side-effects of the following kind:
        - no input read and no output printed ;
        - no modification of global variables (including mutable parameters) ;
        - no exception raised ;
        """
        params.setdefault("allow_global_change", False)
        params.setdefault("allow_arg_change", False)

        if kwargs is None:
            kwargs = {}
        if reffunc is None and result is ...:
            raise GraderError("Test impossible, fournir l'un ou l'autre de "
                              "result ou reffunc")
        elif reffunc:
            result = reffunc(*args, **kwargs)
        self.test(funcname=funcname, args=args, kwargs=kwargs, result=result,
                  **params)

    """ Grading """

    def get_grade(self):
        total_grade = total_weight = 0
        for test in self.history:
            total, weight = test.get_grade()
            total_grade += total
            total_weight += weight
        return total_grade / total_weight * 100

    """Rendering"""

    def render(self):
        return "\n".join(test.render() for test in self.history)

    """Getters."""

    def get_analyzer(self):
        if self.analyzer is None:
            self.analyzer = AstAnalyzer(self.code)
        return self.analyzer

    def get_state(self) -> dict:
        return deepcopy(self.current_test.current_state)

    """Setters for execution context."""

    def exec_preamble(self, preamble: str, **kwargs) -> NoReturn:
        exec(preamble, self.current_test.current_state, **kwargs)
        # del self.next_test.current_state['__builtins__']

    def set_globals(self, **variables) -> NoReturn:
        self.current_test.current_state = variables

    def set_state(self, state: dict) -> NoReturn:
        self.current_test.current_state = state

    def update_state(self, state: dict) -> NoReturn:
        self.current_test.current_state.update(state)

    def set_argv(self, argv: List[str]) -> NoReturn:
        self.current_test.argv = argv.copy()

    def set_inputs(self, inputs: List[str]) -> NoReturn:
        self.current_test.current_inputs = inputs.copy()

    """Execution"""

    def execute_source(self):
        if self.current_test is None:
            self.begin_test()
        self.current_test.execute_source()

    def evaluate(self, expression):
        if self.current_test is None:
            self.begin_test()
        self.current_test.evaluate(expression)

    """Assertions."""

    def assert_output(self, expected: str, cmp: Callable = operator.eq):
        """
        Assert that the last run's output equals `expected` (using `cmp` as
        comparison operator).

        :param expected: Expected value of the output.
        :param cmp: Output comparison function.
        """
        if self.current_test is None:
            raise GraderError("No current test, assertion impossible.")
        output = self.current_test.stdout
        status = cmp(expected, output)
        self.current_test.record_assertion(
            OutputAssert(status, expected, output))

    def assert_result(self, expected, cmp: Callable = operator.eq):
        """
        Assert that the last run's result equals `expected` (using `cmp` as
        comparison operator).

        :param expected: Expected value of the result.
        :param cmp: Output comparison function.
        :return: Assertion status.
        """
        if self.current_test is None:
            raise GraderError("No current test, assertion impossible.")
        expr = self.current_test.expression
        if expr is None:
            raise GraderError("No expression was evaluated")
        res = self.current_test.result
        status = cmp(expected, res)
        self.current_test.record_assertion(
            ResultAssert(status, expr, expected, res))

    def assert_variable_values(self, cmp=operator.eq, **expected):
        """
        Assert that the values of some variables after the last run equal
        their values in the `expected` dictionary (using `cmp` as comparison
        operator).

        :param expected: Expected value of the variables.
        :param cmp: Value comparison function.
        :return: Assertion status.
        """
        if self.current_test is None:
            raise GraderError("No current test, assertion impossible.")
        if not expected:
            raise GraderError("No expected values provided.")
        state = self.current_test.current_state
        missing = list(expected.keys() - state.keys())
        incorrect = {var: state[var] for var in expected.keys() & state.keys()
                     if not cmp(expected[var], state[var])}
        status = not (missing or incorrect)
        self.current_test.record_assertion(
            VariableValuesAssert(status, expected, missing, incorrect))

    def assert_variable_types(self, cmp=operator.eq, **expected):
        """
        Assert that the types of some variables after the last run equal
        their values in the `expected` dictionary (using `cmp` as comparison
        operator).

        :param expected: Expected type of the variables.
        :param cmp: Value comparison function.
        """
        if self.current_test is None:
            raise GraderError("No current test, assertion impossible.")
        if not expected:
            raise GraderError("No expected types provided.")
        state = self.current_test.current_state
        missing = list(expected.keys() - state.keys())
        incorrect = {var: state[var] for var in expected.keys() & state.keys()
                     if not cmp(expected[var], type(state[var]))}

        status = not (missing or incorrect)
        self.current_test.record_assertion(
            VariableTypesAssert(status, expected, missing, incorrect))

    def assert_no_global_change(self):
        """
        Assert that no global variables changed during the last run.
        """
        if self.current_test is None:
            raise GraderError("No current test, assertion impossible.")
        previous = self.current_test.previous_state
        current = self.current_test.current_state
        added, deleted, modified = _compare_namespaces(previous, current)
        status = not (added or deleted or modified)
        self.current_test.record_assertion(NoGlobalChangeAssert(status))

    def assert_no_arg_change(self):
        """
        Assert that no argument changed during the last run.
        """
        if self.current_test is None:
            raise GraderError("No current test, assertion impossible.")
        previous = self.current_test.pre_args
        current = self.current_test.post_args
        added, deleted, modified = _compare_namespaces(previous, current)
        status = not (added or deleted or modified)
        self.current_test.record_assertion(NoArgsChangeAssert(status))

    def assert_no_exception(self, **params):
        """
        Assert that no exception was raised during the last run.
        """
        if self.current_test is None:
            raise GraderError("No current test, assertion impossible.")
        status = self.current_test.exception is None
        self.current_test.record_assertion(
            NoExceptionAssert(status, self.current_test.exception, **params))

    def assert_exception(self, exception_type) -> NoReturn:
        """
        Assert that an exception of type `exception_type` was raised during the
        last expression evaluation or program execution.
        """
        if self.current_test is None:
            raise GraderError("No current test, assertion impossible.")
        status = isinstance(self.current_test.exception, exception_type)
        self.current_test.record_assertion(
            ExceptionAssert(status, exception_type))

    def assert_no_loop(self, funcname, keywords=("while", "for")):
        if self.current_test is None:
            raise GraderError("No current test, assertion impossible.")
        status = not self.get_analyzer().has_loop(funcname, keywords)
        self.current_test.record_assertion(
            NoLoopAssert(status, funcname, keywords))

    def assert_recursion(self, expr):
        # TODO : fix this, should be controlled
        if self.current_test is None:
            raise GraderError("No current test, assertion impossible.")
        call = eval("lambda: " + expr, deepcopy(self.module.__dict__))
        status = performs_recursion(call)
        self.current_test.record_assertion(RecursionAssert(status, expr))

    def assert_previous_recursion(self):
        if self.current_test is None:
            raise GraderError("No current test, assertion impossible.")
        self.current_test.record_assertion(
            RecursionAssert(self.current_test.recursion,
                            self.current_test.expression))

    def assert_defines_function(self, funcname):
        """
        Assert that the current session's contains a definition for a function
        named `funcname`.

        :param funcname: Function name.
        """
        if self.current_test is None:
            raise GraderError("No current test, assertion impossible.")
        status = self.get_analyzer().defines_function(funcname)
        self.current_test.record_assertion(
            FunctionDefinitionAssert(status, funcname))

    def assert_returns_none(self, funcname):
        if self.current_test is None:
            raise GraderError("No current test, assertion impossible.")
        status = self.get_analyzer().returns_none(funcname)
        self.current_test.record_assertion(NoReturnAssert(status, funcname))
        return status

    def assert_calls_function(self, caller, callee):
        if self.current_test is None:
            raise GraderError("No current test, assertion impossible.")
        status = callee in self.get_analyzer().calls_list(caller)
        self.current_test.record_assertion(CallAssert(status, caller, callee))


class Test:
    """
    Test runner. Manages execution context, effects,
    assertions about the execution's outcome, and test decription.
    """

    def __init__(self, session: TestSession, number: int,
                 title: str = "", descr: str = "",
                 hint: str = "", weight: int = 1,
                 state: Optional[dict] = None,
                 inputs: Optional[list] = None,
                 argv: Optional[list] = None,
                 **params: dict) -> NoReturn:
        """Test instance initializaton.

        :param code: Code to test.
        :param weight: Weight of the test on total grade.
        :param title: Test title.
        :param title: Test description.
        :param title: Test hint.
        :param params: Additional test control parameters. Currently
            allowed keys are:
            - report_success (bool): whether or not to report passed assertions;
            - fail_fast (bool): whether or not to stop after the first error.
        """
        self.session: TestSession = session
        self.params: dict = _default_params.copy()
        self.params.update(params)
        self.number: int = number

        # execution context (backup)
        self.previous_state: Dict[str, Any] = {}
        self.previous_inputs: List[str] = []

        # execution context (current)
        if self.session.module is not None:
            self.current_state = self.session.module.__dict__
        else:
            self.current_state = {}
        if state is not None:
            self.current_state.update(state)
        self.current_inputs: List[str] = [] if inputs is None else inputs
        self.argv: List[str] = [] if argv is None else argv
        self.pre_args = None

        # test state (last run expression, code execution flag)
        self.executed: bool = False
        self.expression: Optional[str] = None

        # execution effects
        self.stdout: str = ""
        self.stderr: str = ""
        self.post_args = None
        self.exception: Optional[Exception] = None
        self.result: Any = None
        self.recursion = False

        # test description
        self.title: str = title
        if title == "":
            self.title = "Test {}".format(self.number)
        self.descr: str = descr
        self.hint: str = hint
        self.weight: int = weight

        # assertions
        self.assertions: List[Assert] = []
        self.status: bool = True

    """Code execution."""

    def backup_state(self):
        if self.session.module is not None:
            self.previous_state = deepcopy(self.session.module.__dict__)
        else:
            self.previous_state = {}
        self.previous_inputs = self.current_inputs.copy()

    def execute_source(self) -> NoReturn:

        if self.session.module is None:
            modname = 'studentmod'
            spec = importlib.util.spec_from_loader(modname, loader=None)
            self.session.module = importlib.util.module_from_spec(spec)
            self.current_state = self.session.module.__dict__
            sys.modules[modname] = self.session.module

            def runnable():
                exec(self.session.code, self.current_state)
        else:
            def runnable():
                importlib.reload(self.session.module)

        self.controlled_run(runnable)
        self.executed = True

    def evaluate(self, expression) -> NoReturn:
        def runnable():
            return eval(expression, self.current_state)

        self.backup_state()
        self.expression = expression
        self.result = self.controlled_run(runnable)

    def call_function(self, funcname, args, kwargs):
        # get function object and argument names
        function = getattr(self.session.module, funcname)
        argnames = getfullargspec(function)[0]

        # store argument values pre-call
        self.pre_args = _argument_dict(argnames, args, kwargs)

        # perform the call
        def runnable():
            return function(*args, **kwargs)
        self.result = self.controlled_run(runnable)

        # store argument values post-call
        self.post_args = _argument_dict(argnames, args, kwargs)

    def detect_recursion(self, funcname, args, kwargs):
        # get function object and argument names
        function = getattr(self.session.module, funcname)

        # perform the call
        def runnable():
            return performs_recursion(lambda: function(*args, **kwargs))
        self.recursion = self.controlled_run(runnable)

    def controlled_run(self, runnable):
        # backup previous state
        self.backup_state()

        # prepare StringIO for stdout simulation
        stdout_stream = StringIO()
        stderr_stream = StringIO()

        # run the code while mocking input, sys.argv and stdout printing
        try:
            with mock_input(self.current_inputs, self.current_state,
                            verbose=self.params['verbose_inputs']):
                with mock.patch.object(sys, 'argv', self.argv):
                    with mock.patch.object(sys, 'stdout', stdout_stream):
                        with mock.patch.object(sys, 'stderr', stderr_stream):
                            res = runnable()
        except Exception as e:
            self.exception = e
            res = None

        # store generated output
        self.stdout = stdout_stream.getvalue()
        self.stderr = stderr_stream.getvalue()

        # return result
        return res

    """Assertions."""

    def record_assertion(self, assertion: 'Assert') -> NoReturn:
        """
        Record an assertion (using an Assertion object) in the test's history.
        """
        self.assertions.append(assertion)
        self.status = self.status and assertion.status
        if self.params.get('test_fail_fast', False) and not self.status:
            raise StopGrader("Failed assert during fail-fast test")

    """Feedback"""

    def describe_context(self) -> str:
        """
        Returns a HTML-formatted string describing a test's previous
        execution context.

        Includes existing global variables and their values, available input
        lines, and command-line arguments.

        :return: Full-text HTML formatted description of context.
        """
        res = []

        if self.previous_state:
            tmp = ", ".join(self.previous_state.keys() - _excluded_globals)
            res.append(f"Variables globales : <code>{tmp}</code>")
        if self.previous_inputs:
            tmp = "\n".join(self.previous_inputs)
            res.append(f"Entrées disponibles : <pre>{tmp}</pre>")
        if self.argv:
            tmp = " ".join(self.argv)
            res.append(f"Arguments du programme : <code>{tmp}</code>")

        return "<br/>".join(res) if res else "Pas de variables globales, " \
                                             "entrées ni arguments"

    def describe_results(self) -> str:
        """
        Returns a HTML-formatted string describing a test's effect.

        Includes results (if an expression was evaluated), created,
        modified and deleted global variables, read input lines, printed
        text, raised exceptions.

        :return: Full-text HTML formatted description of run effects.
        """
        res = []
        added, deleted, modified = _compare_namespaces(
            self.previous_state, self.current_state)
        n = len(self.previous_inputs) - len(self.current_inputs)
        inputs = self.previous_inputs[:n]

        if self.expression is not None and self.result is not None:
            res.append("Résultat obtenu : <code>{}</code>".format(self.result))
        if added:
            tmp = ", ".join(added)
            res.append(f"Variables créées : <code>{tmp}</code>")
        if modified:
            tmp = ", ".join(modified)
            res.append(f"Variables modifiées : <code>{tmp}</code>")
        if deleted:
            tmp = ", ".join(deleted)
            res.append(f"Variables supprimées : <code>{tmp}</code>")
        if inputs:
            tmp = "<br/>\n".join(inputs)
            res.append(f"Lignes saisies : <code>{tmp}</code>")
        if self.stdout:
            tmp = self.stdout.replace('\n', "↲\n")
            tmp = tmp.replace(' ', '⎵')
            res.append("Texte affiché : "
                       "<pre style='margin:3pt; padding:2pt; "
                       "background-color:black; color:white;'>"
                       "{}</pre>".format(tmp))
        if self.exception:
            res.append("Exception levée : {} ({})".format(
                type(self.exception).__name__, self.exception))

        return "<br/>".join(res) if res else "Aucun effet observable"

    def get_grade(self):
        """
        Gets test grade. Currently only 0 or self.weight.
        """
        return (self.status * self.weight), self.weight

    def render(self) -> str:
        """
        Returns a Jinja2 HTML-formatted description of the test.

        :return: HTML-formatted report on the test.
        """
        with open(_default_test_template, "r") as tempfile:
            templatestring = tempfile.read()
        template = jinja2.Template(templatestring)
        return template.render(test=self)

    def make_id(self) -> str:
        """
        Make a (session-)unique id for the test, using its number.

        :return: Unique id of the form test_<number>
        """
        return 'test_' + str(self.number)

    def set_default_title(self, expression):
        self.title = f"Évaluation de l'expression <code>{expression}</code>"


class TestGroup:
    """
    Groups of Test instances sharing a title.

    Feedback for test groups are supposed to share a <div> and a common
    description. Groups are intended to clarify the relationships between
    certain tests.
    """
    _num = 0

    def __init__(self, title: str, weight: int = 1, **params):
        """
        Initialize a TestGroup.

        :param title: Title of the test group (required). Try to be as clear
        as possible.
        :param weight: Weight in final TestSession grade. The whole groups's
        grade is multiplied by this factor before being added to other Test
        and TestGroup grades.
        :param params: Additional execution parameters such as fail_fast (
        default: True) and report_success (default: False).
        """
        self.num: int = TestGroup._num
        TestGroup._num += 1
        self.title: str = title
        self.weight: int = weight
        self.status: bool = True
        self.tests: List[Test] = []
        self.params = _default_params.copy()
        self.params.update(params)

    def append(self, test: 'Test') -> NoReturn:
        """
        Append a Test to a TestGroup's history.

        The Test instance to be appended should contain all relevant
        information for feedback (execution results, assertions, grade, etc.).

        :param test: The Test instance to append.
        """
        self.tests.append(test)

    def make_id(self) -> str:
        """
        Returns a (TestSession-)unique identifier for the current group.

        :return: Identifier of the form "group_<number>".
        """
        return 'group_' + str(self.num)

    def get_grade(self) -> Tuple[float, int]:
        """
        Returns a grade for the current group, normalized to the current
        group's weight.

        :return: Tuple `(g, w)` where `g` is a grade between 0 and `w`.
        """
        total_grade = total_weight = 0
        for test in self.tests:
            total, weight = test.get_grade()
            total_grade += total
            total_weight += weight
        return total_grade / total_weight * self.weight, self.weight

    def render(self) -> str:
        """
        Returns a Jinja2 HTML-formatted description of the TestGroup.

        :return: HTML-formatted report on the test group.
        """
        with open(_default_group_template, "r") as tempfile:
            templatestring = tempfile.read()
        template = jinja2.Template(templatestring)
        return template.render(testgroup=self)

    def update_status(self, status) -> NoReturn:
        """
        Incorporate new test result into test group status.

        :param status: A new test status.
        """
        self.status = self.status and status


class Assert:
    _num = 0

    def __init__(self, status, params):
        self.num = Assert._num
        Assert._num += 1
        self.status = status
        self.params = _default_params.copy()
        self.params.update(params)


class ExceptionAssert(Assert):

    def __init__(self, status, exception: type(Exception), **params):
        super().__init__(status, params)
        self.exception = exception

    def __str__(self):
        if self.status:
            return "L'exception attendue a été levée"
        else:
            return f"Une exception de type <code>{self.exception}</code> " \
                   f"était attendue"


class NoExceptionAssert(Assert):

    def __init__(self, status, exception=None, **params):
        super().__init__(status, params)
        self.exception = exception

    def __str__(self):
        if self.status:
            return "Aucune exception levée"
        else:
            return "Une exception inattendue s'est produite"


class ResultAssert(Assert):

    def __init__(self, status, expression, expected, actual, **params):
        super().__init__(status, params)
        self.expression = expression
        self.expected = expected
        self.actual = actual

    def __str__(self):
        if self.status:
            if self.expected is not ...:
                return "Résultat correct"
            else:
                return "Pas de résultat"
        else:
            return "Résultat attendu : <pre>{!r}</pre>".format(self.expected)


class OutputAssert(Assert):

    def __init__(self, status, expected, actual, **params):
        super().__init__(status, params)
        self.expected = expected
        self.actual = actual

    def __str__(self):
        if self.status:
            if self.expected == "":
                return "Pas d'affichage"
            else:
                return "Affichage correct"
        elif self.expected == "":
            return "Aucun affichage attendu"
        else:
            # diff = _unidiff_output(self.expected, self.actual)
            tmp = self.expected.replace('\n', "↲\n")
            tmp = tmp.replace(' ', '⎵')
            return ("Affichage attendu :\n"
                    "<pre style='margin:3pt; padding:2pt; "
                    "background-color:black; color:white;'>\n"
                    "{}</pre>".format(tmp))


class VariableValuesAssert(Assert):

    def __init__(self, status, expected, missing, incorrect, **params):
        super().__init__(status, params)
        self.expected = expected
        self.missing = missing
        self.incorrect = incorrect

    def __str__(self):
        if self.status:
            res = "Variables globales correctes"
        else:
            res = "Variables globales incorrectes : "
            details = []
            for var in self.missing:
                details.append("<code>{}</code> manquante".format(var))
            for var in self.incorrect:
                details.append(f"<code>{var}</code> devrait valoir "
                               "<code>{self.expected[var]!r}</code>")
            res += "; ".join(details)
        return res


class VariableTypesAssert(Assert):

    def __init__(self, status, expected, missing, incorrect, **params):
        super().__init__(status, params)
        self.expected = expected
        self.missing = missing
        self.incorrect = incorrect

    def __str__(self):
        if self.status:
            res = "Variables globales correctes"
        else:
            res = "Variables globales incorrectes : "
            details = []
            for var in self.missing:
                details.append("<code>{}</code> manquante".format(var))
            for var in self.incorrect:
                details.append(f"<code>{var}</code> devrait être de type "
                               f"<code>{self.expected[var]!r}</code>")
            res += "; ".join(details)
        return res


class NoGlobalChangeAssert(Assert):

    def __init__(self, status, **params):
        super().__init__(status, params)

    def __str__(self):
        if self.status:
            return "Variables globales inchangées"
        else:
            return "Variables globales modifiées"


class NoArgsChangeAssert(Assert):

    def __init__(self, status, **params):
        super().__init__(status, params)

    def __str__(self):
        if self.status:
            return "Paramètres effectifs inchangés"
        else:
            return "Paramètres effectifs modifiés"


class NoLoopAssert(Assert):

    def __init__(self, status: bool, funcname: str, keywords: Tuple[str],
                 **params):
        super().__init__(status, params)
        self.funcname = funcname
        self.keywords = keywords

    def __str__(self):
        kw = " ou ".join(self.keywords)
        if self.status:
            return f"Pas de boucle {kw} dans la fonction <code>" \
                   f"{self.funcname}</code>"
        else:
            return f"Boucle {kw} dans la fonction <code>{self.funcname}</code>"


class RecursionAssert(Assert):

    def __init__(self, status, expr, **params):
        super().__init__(status, params)
        self.expr = expr

    def __str__(self):
        if self.status:
            return f"L'expression <code>{self.expr}</code> provoque des " \
                   f"appels récursifs"
        else:
            return f"L'expression <code>{self.expr}</code> ne provoque pas " \
                   f"d'appels récursifs"


class FunctionDefinitionAssert(Assert):

    def __init__(self, status, funcname, **params):
        super().__init__(status, params)
        self.funcname = funcname

    def __str__(self):
        if self.status:
            return f"La fonction <code>{self.funcname}</code> est définie"
        else:
            return f"La fonction <code>{self.funcname}</code> n'est pas définie"


class CallAssert(Assert):

    def __init__(self, status, caller, callee, **params):
        super().__init__(status, params)
        self.caller = caller
        self.callee = callee

    def __str__(self):
        if self.status:
            return f"La fonction <code>{self.caller}</code> est susceptible " \
                   f"d'appeler la fonction {self.callee}"
        else:
            return f"La fonction <code>{self.caller}</code> n'appelle pas la " \
                   f"fonction <code>{self.callee}</code>"


class NoReturnAssert(Assert):

    def __init__(self, status, funcname, **params):
        super().__init__(status, params)
        self.funcname = funcname

    def __str__(self):
        if self.status:
            return f"La fonction <code>{self.funcname}</code> " \
                   "renvoie toujours None"
        else:
            return f"La fonction <code>{self.funcname}</code> " \
                   "est susceptible de renvoyer une valeur différente de " \
                   "<code>None</code>"
