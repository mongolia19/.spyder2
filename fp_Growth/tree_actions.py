#coding=utf-8

class Node(object):
    def __init__(self, data=-1, count=0, parent=None):
        self.data = data
        self.count = count
        self.parent = parent
        self.children = {}


class tree_growth(object):
    def __init__(self, data=-1, parent=None, itemTable=None):
        self.root = Node(data='null', parent=self)
        self.itemTable = itemTable


    def addRoutine(self, routine, Rroot):
        if len(routine) <= 0:
            return
        node = Rroot
        elem = routine.pop(0)
        if elem in node.children:
            nextNode = node.children[elem]
        else:
            newNode = Node(data=elem, parent=node)
            node.children.setdefault(elem,newNode)
            nextNode = newNode
        nextNode.count += 1
        if nextNode not in self.itemTable[elem]:
            self.itemTable[elem].append(nextNode)
        self.addRoutine(routine, nextNode)
            
