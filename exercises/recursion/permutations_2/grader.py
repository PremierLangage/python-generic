def permutations(lst):
    def aux(i, acc):
        if i < 0:
            return [acc.copy()]
        else:
            res = []
            for j in range(len(acc) + 1):
                acc.insert(j, lst[i])
                res.extend(aux(i-1, acc))
                acc.pop(j)
            return res

    return aux(len(lst)-1, [])


def sorted_cmp(lst1, lst2):
    return sorted(lst1) == sorted(lst2)


begin_test('Exécution sans erreur')
execute_source()
assert_output("")
assert_no_exception()

begin_test('Respect des consignes')
assert_defines_function("permutations")
assert_recursion("permutations([1, 2, 3])")

instances = [[], [1, 5, 42], ['a', 'b', 'c']]

for lst in instances:
    begin_test(f'Permutations de {lst}')
    evaluate(f'permutations({lst})')
    assert_output('')
    assert_result(permutations(lst), cmp=sorted_cmp)
