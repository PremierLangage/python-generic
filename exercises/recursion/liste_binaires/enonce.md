On souhaite écrire une fonction récursive `liste_binaires(n)` renvoyant la
liste des mots à `n` caractères dans l'alphabet binaire (`'0'` ou `'1'`) dans
l'ordre lexicographique. Par exemple:

    >>> liste_binaires(2)
    ['00', '01', '10', '11']

Pour résoudre ce problème plus aisément, on introduit une fonction auxiliaire
`liste_binaires_prefixe(n, prefixe)` permettant d'afficher tous les nombres
binaires à `n` chiffres commençant par la chaîne `prefixe`(chaîne supposée
contenir uniquement des caractères `'0'` et `'1'`). Par exemple:

    >>> liste_binaires_prefixe(4, '01')
    ['0100', '0101', '0110', '0111']

Le travail demandé est d'écrire la fonction **récursive**
`liste_binaires_prefixe(n, prefixe)` décrite ci - dessus, ainsi que la
fonction `liste_binaires(n)`. On pourra s'inspirer pour cela de l'algorithme
utilisé dans l'exercice *affichage des mots binaires*.
