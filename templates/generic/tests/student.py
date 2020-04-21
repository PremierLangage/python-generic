def affiche_binaires_prefixe(n, prefixe):
    if n <= len(prefixe):
        print(prefixe)
    else:
        affiche_binaires_prefixe(n, prefixe + '0')
        affiche_binaires_prefixe(n, prefixe + '1')


def affiche_binaires(n):
    if n > 0:
        affiche_binaires_prefixe(n, '')
