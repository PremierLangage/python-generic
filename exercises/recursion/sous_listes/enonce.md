On souhaite écrire une fonction *récursive* `sous_listes(lst)` renvoyant la
liste de toutes les sous-listes de `lst`, c'est à dire de toutes les listes
contenant une partie des éléments de `lst`, dans l'ordre où ils apparaissent
dans `lst`. On pourra s'inspirer pour cela de l'algorithme utilisé dans 
l'exercice *affichage des mots binaires*.

Exemples :

    >>> sous_listes([])
    [[]]

    >>> sous_listes([1, 2])
    [[], [2], [1], [1, 2]]

La fonction ne doit provoquer aucun affichage. Votre programme ne doit pas 
créer d'autres variables globales que la fonction `sous_listes`. L'ordre dans
lequel les sous-listes apparaissent dans le résultat n'est pas imposé, mais 
l'ordre des éléments dans chaque sous-liste l'est.  

