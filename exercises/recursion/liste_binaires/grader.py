def liste_binaires_aux(n, prefixe):
    if n <= len(prefixe):
        return [prefixe]
    else:
        return (liste_binaires_aux(n, prefixe + '0')
                + liste_binaires_aux(n, prefixe + '1'))


def liste_binaires(n):
    return liste_binaires_aux(n, '')


begin_test('Exécution sans erreur')
execute_source()
assert_output("")
assert_no_exception()

begin_test('Respect des consignes', fail_fast=False)
assert_defines_function("liste_binaires")
assert_no_loop("liste_binaires")
assert_recursion("liste_binaires(3)")

for i in range(10):
    begin_test(f'Chaînes binaires de longueur {i}', fail_fast=False)
    evaluate(f'liste_binaires({i})')
    assert_output('')
    assert_result(liste_binaires(i))
