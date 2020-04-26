from random import randrange


def sous_listes_corr(lst, indice=0):
    if indice >= len(lst):
        return [[]]
    else:
        tmp = sous_listes_corr(lst, indice + 1)
        tmp.extend([[lst[indice]] + sub for sub in tmp])
        return tmp


def sorted_cmp(lst1, lst2):
    return sorted(lst1) == sorted(lst2)


begin_test('Exécution sans erreur')
execute_source()
assert_output("")
assert_no_exception()

begin_test('Respect des consignes')
assert_defines_function('sous_listes')
assert_no_loop('sous_listes', ('while', ))
assert_recursion('sous_listes([1, 2])')

begin_test('Sous-listes de <tt>[]</tt>')
evaluate('sous_listes([])')
assert_result([[]])
assert_output("")

begin_test('Sous-listes de <tt>[1, 2, 3]</tt>')
evaluate('sous_listes([1, 2, 3])')
assert_result(sous_listes_corr([1, 2, 3]), cmp=sorted_cmp)
assert_output("")

begin_test("Sous-listes d'une liste aléatoire")
lst = [randrange(10) for _ in range(4)]
evaluate(f'sous_listes({lst})')
assert_result(sous_listes_corr(lst))
assert_output("")
