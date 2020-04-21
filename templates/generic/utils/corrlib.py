"""Modules contenant des fonctions utiles pour écrire des correcteurs
automatiques pour les TPs d'algorithmique.

Auteur : Anthony Labarre
"""
import os
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from bdb import Bdb
from doctest import DocTestRunner, DocTestFinder
from importlib import import_module
from platform import system
from subprocess import check_call
from sys import settrace
from traceback import format_exc


# Variables globales ----------------------------------------------------------
PAD = " " * 6  # la taille de "[ ? ]" + un espace
SIGN = ["[ \033[1;31mx\033[0m ]", "[ \033[1;32mv\033[0m ]"]
if system() == "Windows":
    SIGN = ["[ x ]", "[ v ]"]


def charger_module_etudiant(chemin, correction_deja_tentee=False):
    """Charge et renvoie le module spécifié."""
    try:
        return import_module(chemin)
    except TabError:
        print(
            "\nImpossible de charger le module de l'étudiant à cause d'un "
            "mélange de tabulations et d'espaces", end=""
        )
        if correction_deja_tentee:
            print(
                ", même après tentative de correction automatique par autopep8"
            )
            exit(-1)

        if which("autopep8"):
            reponse = prompt(
                ".\n\tJ'ai détecté autopep8, voulez-vous que je tente de corriger "
                "le fichier automatiquement?", ["o", "n"]
            )
            if reponse == "o":
                correction_autopep8(chemin + ".py")
                return charger_module_etudiant(chemin, True)

        else:
            print("; réglez le problème et relancez-moi ensuite.\n")

        exit(-1)
    except IndentationError:
        print(
            "\nImpossible de charger le module de l'étudiant à cause d'une "
            "erreur d'indentation."
        )
        montrer_derniere_erreur()
        exit(-1)
    except SyntaxError:
        print(
            "\nImpossible de charger le module de l'étudiant à cause d'une "
            "erreur de syntaxe."
        )
        montrer_derniere_erreur()
        exit(-1)


def completer_module(nom_module, fonctions_attendues):
    """Rajoute des fonctions à un module (typiquement celui d'un étudiant) pour
    éviter les plantages ultérieurs."""
    fonctions_manquantes = set(fonctions_attendues).difference(
        set(dir(nom_module))
    )
    for nom in fonctions_manquantes:
        setattr(nom_module, nom, fonction_bidon)

    return fonctions_manquantes


def copier_doctests(fonction, module_dest):
    """Copie la docstring de la fonction spécifiée vers celle portant le même
    nom dans module_dest.

    :rtype : None
    :param fonction: la fonction "source"
    :param module_dest:  le module contenant la fonction "destination"
    :return:
    """
    getattr(module_dest, fonction.__name__).__doc__ = fonction.__doc__


def correction_autopep8(fichier):
    """Copie fichier vers fichier.BAK et tente de corriger automatiquement ce
    qui peut l'être via autopep8."""
    print("\tCopie de", fichier, "vers", fichier + ".BAK")
    print("\tCorrection de", fichier, "par autopep8")
    check_call(["autopep8", "-i", fichier])


def feedback(fonctions_problematiques):
    """Résumé des problèmes du module testé."""
    print("\nRésumé :")
    print("========\n")
    for key in fonctions_problematiques:
        fonctions_problematiques[key].discard("fonction_bidon")

    if fonctions_problematiques["manquantes"]:
        pretty_print(
            "les fonctions suivantes n'ont pas été trouvées: " +
            ", ".join(sorted(fonctions_problematiques["manquantes"])), False
        )

    if fonctions_problematiques["plantent"]:
        pretty_print(
            "les fonctions suivantes ont provoqué des exceptions: " +
            ", ".join(sorted(fonctions_problematiques["plantent"])), False
        )

    if fonctions_problematiques["fausses"]:
        pretty_print(
            "les fonctions suivantes donnent des résultats faux: " +
            ", ".join(sorted(fonctions_problematiques["fausses"])), False
        )

    if "non récursives" in fonctions_problematiques and fonctions_problematiques["non récursives"]:
        pretty_print(
            "les fonctions suivantes ne sont pas récursives: " +
            ", ".join(sorted(fonctions_problematiques["non récursives"])),
            False
        )

    if "récursivité infinie" in fonctions_problematiques and fonctions_problematiques["récursivité infinie"]:
        pretty_print(
            "les fonctions récursives suivantes sont infinies dans certains "
            "cas: " + ", ".join(
                sorted(fonctions_problematiques["récursivité infinie"])
            ), False
        )

    print()


def fonction_bidon(*_, **__):
    """Fonction bidon à insérer dans le module de l'étudiant dans le cas où une
    des fonctions qu'il devait écrire manque. Ceci permet de continuer les
    tests même si l'on n'arrive pas à charger tout ce qu'il nous faut."""
    return None


def initialiser_parser(__name, __description):
    """Initialise et renvoie un parser d'options pour le correcteur."""
    parser = ArgumentParser(
        prog=__name,
        description=__description,
        formatter_class=ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        '-f', '--fichier', type=str, default="",
        help="le fichier .py à vérifier"
    )

    parser.add_argument(
        '-v', '--verbose', type=bool, default=False,
        help='affiche plus de détails'
    )

    return parser


def montrer_derniere_erreur():
    """Affiche la dernière erreur qui s'est produite lors de l'exécution du
    code de l'étudiant."""
    print("\n" + PAD + format_exc().replace("\n", "\n      "))


def points_pour_doctests(un_module, fonction):
    """Exécute les tests spécifiés dans la docstring de la fonction voulue du
    module renseigné, et renvoie le nombre de tests exécutés avec succès.

    :param un_module: le module où se trouve la fonction spécifiée.
    :param fonction: la fonction à tester
    :return: le nombre de tests qui ont été exécutés et le nombre de tests qui
    ont échoué
    """
    total, echecs = 0, 0
    testeur = DocTestRunner(verbose=False)
    for test in DocTestFinder().find(getattr(un_module, fonction.__name__)):
        testeur.run(test)
        total += testeur.tries
        echecs += testeur.failures

    return total, echecs


def pretty_print(msg, success):
    """Affichage d'un message au format "[ v ] ..." ou "[ x ] ..." selon que
    success est True ou False. Sous Linux, le v est en vert gras et le x en
    rouge gras."""
    print(" ".join([SIGN[success], msg]))


def prompt(question, choices, separator="/"):
    """Keeps asking user a question until one of the choices can be
    returned."""
    answer = ''
    message = ' '.join([question, (separator.join(choices)).join('[]'), ''])

    while answer not in choices:
        answer = input(message)

    return answer


def which(programme):
    """Renvoie True SSI programme est trouvable via la variable PATH."""
    # (stackoverflow.com/questions/377017/test-if-executable-exists-in-python)
    def is_exe(chemin_exec):
        """Vérifie que chemin_exec existe et est exécutable."""
        return os.path.isfile(chemin_exec) and os.access(chemin_exec, os.X_OK)

    fpath = os.path.split(programme)[0]
    if fpath and is_exe(programme):
        return True

    for path in os.environ["PATH"].split(os.pathsep):
        if is_exe(os.path.join(path, programme)):
            return True

    return False


# Classes et fonction permettant de vérifier si une fonction donnée est
# récursive (source: https://stackoverflow.com/a/36663046)
class RecursionDetected(Exception):
    pass


class RecursionDetector(Bdb):
    def do_clear(self, arg):
        pass

    def __init__(self, *args):
        Bdb.__init__(self, *args)
        self.stack = set()

    def user_call(self, frame, argument_list):
        code = frame.f_code
        if code in self.stack:
            raise RecursionDetected
        self.stack.add(code)

    def user_return(self, frame, return_value):
        self.stack.remove(frame.f_code)


def est_recursive(func):
    """Renvoie True si func effectue des appels récursifs, False sinon.
    Fonctionne aussi pour des fonctions indirectement récursives, et en
    particulier la récursivité croisée, même si la fonction effectue des
    appels récursifs infinis.

    >>> def non_rec(n):
    ...     return n
    ...
    >>> est_recursive(lambda: non_rec(10))
    False
    >>> def a(n):
    ...     return a(n-1)
    ...
    >>> est_recursive(lambda: a(10))
    True
    >>> def b(n):
    ...     return c(n-1)
    ...
    >>> def c(n):
    ...     return b(n-1)
    ...
    >>> est_recursive(lambda: b(10))
    True
    >>> def d(n):
    ...     if n: return d(n-1)
    ...
    >>> est_recursive(lambda: d(1))
    True
    >>> est_recursive(lambda: d(0))
    False
    """
    detector = RecursionDetector()
    detector.set_trace()
    try:
        func()
    except RecursionDetected:
        return True
    else:
        return False
    finally:
        settrace(None)

