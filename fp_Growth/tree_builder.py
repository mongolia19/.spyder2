#coding=utf-8

import tree_actions

class tree_builder(object):

    def __init__(self, routines, min_sup=-1):
        self.routines = routines
        self.min_sup = min_sup
        self.items = self.getItems()            #获取所有项
        self.sortedItems = self.getSortedItems()            #对所有项进行统计个数，并排序
        self.itemsTable = self.initItemsTable()
        self.SortedRoutines = list()
        self.tree = self.treeBuilding()
        

    def getItems(self):
        items = {}
        for routine in self.routines:
            for item in routine:
                    items.setdefault(item,0)
                    items[item] += 1
        return items
    
    def getSortedItems(self):
        sortedItems = []
        temp = sorted(self.items.iteritems(), key=lambda asd:asd[1], reverse=True)
        for elem in temp:
            if elem[1] >= self.min_sup:
                sortedItems.append(elem[0])
        return sortedItems
    
    def getSortedRoutine(self, routine=None):
        sortedRoutine = []
        for elem in self.sortedItems:
            if elem in routine:
                sortedRoutine.append(elem)
        return sortedRoutine

    def initItemsTable(self):
        itemsTable = {}
        for item in self.sortedItems:
            itemsTable.setdefault(item,[])
        return itemsTable 

    def getListStr(self, listStr):
        res = ""
        if listStr is None:
            return ""
        for s in listStr:
            res = res + s + ' '
        return res


    def treeBuilding(self):
        tree = tree_actions.tree_growth(itemTable=self.itemsTable)
        for routine in self.routines:
            sortedRoutine = self.getSortedRoutine(routine)
            print sortedRoutine
            tempstr = self.getListStr(sortedRoutine)
            if tempstr != "":
                self.SortedRoutines.append(tempstr)
            tree.addRoutine(sortedRoutine,tree.root)

        return tree

    
    
    
    
    