Les fonctions écrites dans l'exercice *Permutations (épisode 1)* ne sont pas
très satisfaisantes : elles prennent des arguments bizarres, et elles ne
permettent pas de calculer les permutations des éléments d'une liste
quelconque. 

Voilà ce qu'on voudrait vraiment :

    >>> permutations(["bonjour", "chers", "amis"])
    [['bonjour', 'chers', 'amis'],
     ['bonjour', 'amis', 'chers'],
     ['chers', 'bonjour', 'amis'],
     ['amis', 'bonjour', 'chers'],
     ['chers', 'amis', 'bonjour'],
     ['amis', 'chers', 'bonjour']]

À vous de jouer !

*Indications :*
- il est possible de créer une ou plusieurs fonctions auxiliaires ;
- l'ordre dans lequel les permutations apparaît n'est pas imposé.