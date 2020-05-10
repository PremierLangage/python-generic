from random import randrange

begin_test_group("Quelques listes particulières")
for lst in [[], [1], [-1]]:
    test_call("somme_liste", lst, reffunc=sum)

begin_test_group("Quelques listes fixées")
for lst in [[1, 2, 3], [1, 5, 8], [-1, 1, -1, 1, -1, 1.0]]:
    test_call("somme_liste", lst, reffunc=sum, detect_recursion=True)

begin_test_group("Quelques listes aléatoires")
for _ in range(10):
    lst = [randrange(-999, 1000) for _ in range(randrange(10, 20))]
    test_call("somme_liste", lst, reffunc=sum, detect_recursion=True)