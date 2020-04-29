def liste_binaires_aux(n, prefixe):
    if n <= len(prefixe):
        return [prefixe]
    else:
        return (liste_binaires_aux(n, prefixe + '0')
                + liste_binaires_aux(n, prefixe + '1'))


def liste_binaires(n):
    return liste_binaires_aux(n, '')
