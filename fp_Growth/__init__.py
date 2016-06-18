#coding=utf-8

import tree_builder

routines = [
           ['Cola','Egg','Ham'],
            ['Cola','Diaper','Beer'],
            ['Cola','Beer','Diaper','Ham'],
           ['Diaper','Beer']
        ]
min_sup = 2


tree = tree_builder.tree_builder(routines, min_sup)