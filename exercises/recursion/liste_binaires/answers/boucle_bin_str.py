def liste_binaires(n):
    return [str(bin(i))[2:].zfill(n) for i in range(2**n)]