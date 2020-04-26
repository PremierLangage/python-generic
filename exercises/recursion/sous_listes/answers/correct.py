def sous_listes(lst, indice=0):
    if indice >= len(lst):
        return [[]]
    else:
        tmp = sous_listes(lst, indice + 1)
        tmp.extend([[lst[indice]] + sub for sub in tmp])
        return tmp
