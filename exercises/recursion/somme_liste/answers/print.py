def somme_liste(lst, i=0):
    print(i)
    if len(lst) == i:
        return 0
    else:
        return lst[i] + somme_liste(lst, i+1)
