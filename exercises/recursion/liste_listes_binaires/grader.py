def liste_listes_binaires_aux(n, acc):
    if n == len(acc):
        return [acc]
    else:
        res = liste_listes_binaires_aux(n, acc + [0])
        res.extend(liste_listes_binaires_aux(n, acc + [1]))
        return res


def liste_listes_binaires(n):
    return liste_listes_binaires_aux(n, [])


begin_test('Exécution sans erreur')
execute_source()
assert_output("")
assert_no_exception()

begin_test('Respect des consignes', fail_fast=False)
assert_defines_function("liste_listes_binaires")
assert_recursion("liste_listes_binaires(3)")

for i in range(10):
    begin_test(f'Listes binaires de longueur {i}', fail_fast=False)
    evaluate(f'liste_listes_binaires({i})')
    assert_output('')
    assert_result(liste_listes_binaires(i))
