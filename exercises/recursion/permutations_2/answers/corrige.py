def build_perm(lst, positions):
    return [lst[positions[i]] for i in range(len(positions))]


def aux(lst, i, positions):
    if i >= len(lst):
        return [build_perm(lst, positions)]
    else:
        res = []
        for k in range(len(lst)):
            if positions[k] is None:
                positions[k] = i
                res.extend(aux(lst, i+1, positions))
                positions[k] = None
        return res


def permutations(lst):
    return aux(lst, 0, [None] * len(lst))
