def liste_binaires(n):
    if n == 0 :
        return ['']
    else:
        tmp = liste_binaires(n-1)
        res = []
        for mot in tmp:
            res.append(mot + '0')
            res.append(mot + '1')
        return res
