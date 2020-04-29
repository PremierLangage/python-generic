def chaine_permutations(n, i=1, lst=None):
    if lst is None:
        lst = [0] * n
    if i > n:
        return str(lst) + '\n'
    else:
        res = []
        for k in range(n):
            if lst[k] == 0:
                lst[k] = i
                res.append(chaine_permutations(n, i+1, lst))
                lst[k] = 0
        return ''.join(res)


def liste_permutations(n, i=1, lst=None):
    if lst is None:
        lst = [0] * n
    if i > n:
        return [lst[:]]
    else:
        res = []
        for k in range(n):
            if lst[k] == 0:
                lst[k] = i
                res.extend(liste_permutations(n, i+1, lst))
                lst[k] = 0
        return res


def sorted_cmp(lst1, lst2):
    return sorted(lst1) == sorted(lst2)


def sorted_lines_cmp(text1, text2):
    lst1 = text1.split('\n')
    lst2 = text2.split('\n')
    return sorted(lst1) == sorted(lst2)


begin_test('Exécution sans erreur')
execute_source()
assert_output("")
assert_no_exception()

begin_test_group('Test de la fonction <code>affiche_permutations</code>')

begin_test('Respect des consignes')
assert_defines_function("affiche_permutations")
assert_recursion("affiche_permutations(3, 1, [0, 0, 0])")

begin_test(f'Permutations de []')
evaluate(f'affiche_permutations(0, 1, [])')
assert_output('[]\n')
assert_result(None)

begin_test(f'Permutations de [1, 2, 3]')
evaluate(f'affiche_permutations(3, 1, [0, 0, 0])')
assert_output(chaine_permutations(3, 1, [0, 0, 0]), cmp=sorted_lines_cmp)
assert_result(None)

begin_test(f'Permutations de [1, ..., 5] '
           f'ayant 1 en position 2 et 2 en position 0')
evaluate(f'affiche_permutations(5, 3, [2, 0, 1, 0, 0])')
assert_output(chaine_permutations(5, 3, [2, 0, 1, 0, 0]), cmp=sorted_lines_cmp)
assert_result(None)

begin_test_group('Test de la fonction <code>liste_permutations</code>')

begin_test('Respect des consignes')
assert_defines_function("liste_permutations")
assert_recursion("liste_permutations(3, 1, [0, 0, 0])")

begin_test(f'Permutations de []')
evaluate(f'liste_permutations(0, 0, [])')
assert_output('')
assert_result(liste_permutations(0, 0, []))

begin_test(f'Permutations de [1, 2, 3]')
evaluate(f'liste_permutations(3, 1, [0, 0, 0])')
assert_output('')
assert_result(liste_permutations(3, 1, [0, 0, 0]), cmp=sorted_cmp)

begin_test(f'Permutations de [1, ..., 5] '
           f'ayant 1 en position 2 et 2 en position 0')
evaluate(f'liste_permutations(5, 3, [2, 0, 1, 0, 0])')
assert_output('')
assert_result(liste_permutations(5, 3, [2, 0, 1, 0, 0]))

