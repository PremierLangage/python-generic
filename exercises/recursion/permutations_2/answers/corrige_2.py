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
