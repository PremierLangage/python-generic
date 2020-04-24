from grader import grade_this, create_student_file

student_code = r"""
def affiche_binaires_prefixe(n, prefixe):
    if n <= len(prefixe):
        print(prefixe)
    else:
        affiche_binaires_prefixe(n, prefixe + '0')
        affiche_binaires_prefixe(n, prefixe + '1')

def affiche_binaires(n):
    if n > 0:
        affiche_binaires_prefixe(n, '')
"""


validation_code = r"""
from types import FunctionType

def chaines_binaires_aux(n, prefixe):
    if n <= len(prefixe):
        return prefixe + '\n'
    else:
        return (chaines_binaires_aux(n, prefixe + '0')
                + chaines_binaires_aux(n, prefixe + '1'))

def chaines_binaires(n):
    if n == 0:
        return ''
    else: 
        return chaines_binaires_aux(n, '')


begin_test_group("Test de la fonction <tt>affiche_binaires_prefix</tt>")

run(title='Existence de la fonction <tt>affiche_binaires_prefix</tt>', 
    output='',
    types={"affiche_binaires_prefixe":FunctionType})

run(title='Respect des consignes', 
    output='',
    types={"affiche_binaires_prefixe":FunctionType})
assert_no_loop("affiche_binaires_prefixe")
assert_recursion("affiche_binaires_prefixe(3, '')")

run('affiche_binaires_prefixe(3, "000")', 
    title = f'Chaînes binaires de longueur 3 et de préfixe "000"',
    result = None,
    output = '000\n')

run('affiche_binaires_prefixe(3, "0")', 
    title = f'Chaînes binaires de longueur 3 et de préfixe "0"',
    result = None,
    output = chaines_binaires_aux(3, "0"))

end_test_group()

begin_test_group("Test de la fonction <tt>affiche_binaires</tt>")

run(title='Existence de la fonction <tt>affiche_binaires</tt>', 
    output='',
    types={"affiche_binaires":FunctionType})

run(f'affiche_binaires(0)', 
    title = f'Chaînes binaires de longueur 0',
    result = None,
    output = '')

run(f'affiche_binaires(3)', 
    title = f'Chaînes binaires de longueur 3',
    result = None,
    output = chaines_binaires(3))
"""

if __name__ == "__main__":
    grade, fb = grade_this(student_code, validation_code, globals())
    print(fb)
