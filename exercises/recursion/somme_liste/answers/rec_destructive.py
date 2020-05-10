def somme_liste(lst):
    if len(lst) == 0:
        return 0
    else:
        return lst.pop() + somme_liste(lst)
