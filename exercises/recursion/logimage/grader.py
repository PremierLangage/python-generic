from random import randint


def longueurs_blocs(rangee):
    res = []
    cpt = 0
    for pixel in rangee:
        if pixel == 1:
            cpt += 1
        else:
            if cpt > 0:
                res.append(cpt)
                cpt = 0
    if cpt > 0:
        res.append(cpt)
    return res


def verifie(contraintes, rangee):
    return longueurs_blocs(rangee) == contraintes


def coloriable(rangee, k):
    n = len(rangee)
    if n < k:
        return False
    if n > k and rangee[k] == 1:
        return False
    return True


def completable(contraintes, rangee):
    if len(contraintes) == 0:
        return True
    elif len(rangee) == 0:
        return False
    elif verifie(contraintes, rangee):
        return True

    # cas 1
    k = contraintes[0]
    if coloriable(rangee, k) and completable(contraintes[1:], rangee[k+1:]):
        return True

    # cas 2
    if rangee[0] == 0 and completable(contraintes, rangee[1:]):
        return True

    # échec
    return False


begin_test('Exécution sans erreur')
execute_source()
assert_output("")
assert_no_exception()

begin_test_group('Question 1 - Fonction <code>longueurs_blocs</code>')

begin_test('Respect des consignes')
assert_defines_function("longueurs_blocs")

instances = [[], [0], [1]]
for lst in instances:
    begin_test(f'Longueurs des blocs dans {lst} (test fixe)')
    evaluate(f'longueurs_blocs({lst})')
    assert_output('')
    assert_result(longueurs_blocs(lst))

instances = [[randint(0, 1) for i in range(randint(10, 20))]
             for _ in range(10)]
for lst in instances:
    begin_test(f'Longueurs des blocs dans {lst} (test aléatoire)')
    evaluate(f'longueurs_blocs({lst})')
    assert_output('')
    assert_result(longueurs_blocs(lst))

begin_test_group('Question 2 - Fonction <code>verifie</code>')

instances = [([], []), ([1], []),
             ([], [0]), ([1], [0]), ([1], [1]),
             ([1], [0, 1]), ([1], [1, 0]), ([1], [0, 0]),
             ([2], [0, 1]), ([2], [1, 0]), ([2], [0, 0]),
             ([3], [0, 0, 0]), ([3], [1, 0, 0]),
             ([3], [0, 0, 1]), ([3], [0, 1, 0]),
             ([3], [0, 1, 1]), ([3], [1, 1, 0]),
             ([3], [1, 0, 1]), ([3], [1, 1, 1]),
             ([2], [1, 0, 1]), ([1, 2], [0, 0, 0]),
             ([1, 1], [0, 1, 0]),
             ([1, 1], [0, 0, 0])]

begin_test('Respect des consignes')
assert_defines_function("verifie")
assert_calls_function("verifie", "longueurs_blocs")

for contraintes, rangee in instances:
    begin_test(f'Vérification (test fixe)')
    evaluate(f'verifie({contraintes}, {rangee})')
    assert_output('')
    assert_result(verifie(contraintes, rangee))

begin_test_group('Question 3 - Fonction <code>coloriable</code>')

begin_test('Respect des consignes')
assert_defines_function("coloriable")

instances_col = [([0, 0, 1], 0), ([0, 0, 1], 1),
                 ([0, 0, 1], 2), ([0, 0, 1], 3), ([0, 0, 1], 4)]

for rangee, k in instances_col:
    begin_test(f'Coloriable (test fixe)')
    evaluate(f'coloriable({rangee}, {k})')
    assert_output('')
    assert_result(coloriable(rangee, k))
    assert_no_global_change()

begin_test_group('Question 4 - Fonction <code>completable</code>')

begin_test('Respect des consignes')
assert_defines_function("completable")
assert_recursion("completable([1, 1], [0, 0, 1])")

for contraintes, rangee in instances:
    begin_test(f'Complétable (test fixe)')
    evaluate(f'completable({contraintes}, {rangee})')
    assert_output('')
    assert_result(completable(contraintes, rangee))
