from typing import Callable, TypeVar
from unused.ap1_feedback_old import Feedback

T = TypeVar('T')


def test_call(func: Callable[[...], T],
              args: list, kwargs: dict, expected: T,
              cmp: Callable[[T], T] = lambda x, y: x == y) -> Feedback:
    arglist = ", ".join(args)
    if kwargs:
        kwarglist = (ident + "=" + str(val) for ident, val in kwargs.items())
        arglist += ", " + ", ".join(kwarglist)
    calltext = func.__name__ + '(' + arglist + ')'
    fb = Feedback("Test de l'appel {}".format(calltext))
    try:
        res = func(*args, **kwargs)
    except Exception as e:
        fb.text = "erreur : une exception s'est produite ({})".format(e)
        fb.grade = 0
    else:
        msg = "valeur obtenue : {}".format(res)
        if not isinstance(res, type(expected)):
            msg += "\nerreur : valeur attendue de type {} et non {}"
            fb.text = msg.format(type(expected), type(res))
        elif not cmp(res, expected):
            fb.text = msg + "\nerreur : valeur attendue {}".format(expected)
        else:
            fb.text = "succès :" + msg
            fb.grade = 100
    return fb


def test_variable(ident: str, state: dict, expected: dict) -> Feedback:
    fb = Feedback("Test de la variable {}".format(ident), 0, "detail")
    if ident not in state:
        fb.text = ("erreur : {} non défini".format(ident))
    else:
        value, exp_value = state[ident], expected[ident]
        if not isinstance(value, type(exp_value)):
            msg = "erreur : {} devrait être de type {} et non {}"
            fb.text = (msg.format(ident, type(exp_value), type(value)))
        elif value != exp_value:
            msg = "erreur : {} devrait valoir {} et non {}"
            fb.text = (msg.format(ident, exp_value, value))
        else:
            fb.text = ("succès : valeur obtenue {}".format(value))
            fb.grade = 100
    return fb


def test_state_change(code: str, state: dict, expected: dict) -> Feedback:
    res = Feedback("Test de changement sur état initial {}".format(str(state)),
                   template="unit")
    try:
        exec(code, state)
    except Exception as e:
        res.text = "erreur : une exception s'est produite ({})".format(e)
        res.grade = 0
    else:
        if not expected:
            res.text = "succès : exécution sans erreur"
            res.grade = 100
            return res
        for ident in sorted(expected):
            fb = test_variable(ident, state, expected)
            res.subtest(fb)
        res.set_mean_grade()
        res.text = "succès :" if res.grade == 100 else "échec :"
        del state['__builtins__']
        res.text += " état final {}".format(state)
    return res
