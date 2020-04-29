On souhaite écrire une fonction `affiche_permutations(n, i, tmp)` qui affiche 
toutes les permutations de l’ensemble $\{i, i+1, i+2, \ldots, n\}$ 
(avec $i \geq 1$). Pour cela, on va remplir la liste de taille $n$
`tmp` (qui doit contenir initialement uniquement des 0), en plaçant
successivement chaque entier entre `i` et `n` dans chaque case libre puis en
remplissant les cases libres restantes avec les autres entiers (on considère
qu’une case est libre si elle contient 0). 

À chaque appel, la fonction effectue les étapes suivantes :

-   Si `i` est supérieur à `n` c’est qu’on a placé tous les entiers, on affiche
    alors le contenu de la liste `tmp` ;
-   Sinon on cherche une place libre pour placer `i` (une case de `tmp`
    contenant 0) et on effectue un appel récursif pour placer les valeurs
    suivantes ;
-   Au retour de l’appel récursif, on libère la case utilisée et on cherche une
    autre place pour `i`.

Exemples :

    >>> affiche_permutations(3, 1, [0]*3)
    [1, 2, 3]
    [1, 3, 2]
    [2, 1, 3]
    [3, 1, 2]
    [2, 3, 1]
    [3, 2, 1]

    >>> affiche_permutations(3, 2, [0, 1, 0])
    [2, 1, 3]
    [3, 1, 2]

Cet exercice contient deux tâches distinctes :

1. Écrire une fonction récursive `affiche_permutations(n, i, tmp)` qui
   renvoie la *liste* de toutes les permutations de l'ensemble $\{i, i+1, i+2,
   \ldots, n\}$, dans un ordre quelconque.

2. En utilisant un algorithme similaire, écrire une fonction récursive
   `liste_permutations(n, i, tmp)` qui renvoie la *liste* de toutes les 
   permutations de l'ensemble $\{i, i+1, i+2, \ldots, n\}$, dans un ordre 
   quelconque.
