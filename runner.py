__author__ = 'george'

from gale.where import *
from problems.ZDT1 import ZDT1


o = ZDT1()
o.populate(100)
node = Node(o, Node.format(o.population), 100).divide(sqrt(o.population))
print(node.show())