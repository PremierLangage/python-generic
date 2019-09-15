#!/usr/bin/env python3
#
# Authors:
#   Quentin Coumes <coumes.quentin@gmail.com>
#   Antoine Meyer <antoine.meyer@u-pem.fr>

from contextlib import contextmanager
from typing import List, Union



class InputMocker:
    """Can be use to replace the 'input()' built-in function so that it returned
    predefined inputs.
    
    Inputs can either be a list of string (without '\n') or one string (will be split at '\n').
    
    Example:
    >>> input = InputMocker(["Line 1", "Line 2"])
    >>> input() == "Line 1"
    True
    >>> input() == "Line 2"
    True
    >>> input()
    Traceback (most recent call last):
    ...
    EOFError: No input to be read
    >>> input = InputMocker("Line 1\\nLine 2")
    >>> input() == "Line 1"
    True
    >>> input() == "Line 2"
    True
    
    Using eval():
    >>> context = {'__builtins__': {'input': InputMocker(["Line 1"])}}
    >>> eval('input()', context) == "Line 1"
    True
    
    Using exec():
    >>> context = {'__builtins__': {'input': InputMocker(["Line 1"])}}
    >>> exec("l = input()", context)
    >>> context['l'] == "Line 1"
    True
    """
    
    
    def __init__(self, inputs: Union[str, List[str]]):
        if isinstance(inputs, str):
            inputs = inputs.split('\n')
        self.inputs = inputs
    
    
    def __call__(self, prompt: str = None) -> str:
        try:
            return self.inputs.pop(0)
        except IndexError:
            raise EOFError("No input to be read")



@contextmanager
def mock_input(inputs: Union[str, List[str]], context=None) -> dict:
    """Calls to input() done in this context manager will return the given inputs.
    
    Modifies globals() by default, you can provide an optional context to modify it instead so it
    can be given to exec() or globals().
    
    The mocking is done by adding / modifying the 'input' key for the duration of the context
    manager.
    
    Example:
    >>> with mock_input(["Line 1", "Line 2"], globals()):
    ...     input() == "Line 1"
    ...     input() == "Line 2"
    True
    True
    
    >>> with mock_input("Line 1\\nLine 2", globals()):
    ...     input() == "Line 1"
    ...     input() == "Line 2"
    True
    True

    Using eval():
    >>> with mock_input(["Line 1"], globals()):
    ...     eval("input()") == "Line 1"
    True

    Using exec():
    >>> with mock_input(["Line 1"], globals()):
    ...     exec("l = input()")
    ...     l == "Line 1"
    True

    Using a custom context:
    >>> with mock_input(["Line 1"], {}) as context:
    ...     eval("input()", context) == "Line 1"
    True
    """
    if context is None:
        context = globals()
    old_input = context['input'] if 'input' in context else None
    context['input'] = InputMocker(inputs)
    
    try:
        yield context
    finally:
        if old_input is None:
            del context['input']
        else:
            context['input'] = old_input
