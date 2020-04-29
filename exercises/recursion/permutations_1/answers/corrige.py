def affiche_permutations(n, i, lst):
    if i > n:
        print(lst)
    else:
        for k in range(n):
            if lst[k] == 0:
                lst[k] = i
                affiche_permutations(n, i+1, lst)
                lst[k] = 0


def liste_permutations(n, i, lst):
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
