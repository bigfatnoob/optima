__author__ = 'george'
import sys,os
sys.path.append(os.path.abspath("."))
from problems.problem import *
from softgoals.parser.OMETree import Parser

# TODO implement model here based on model.json based on the architecture in optima/utils/problem.py

EDGE_WEIGHTS = {
  "make"  : +2,
  "help"  : +1,
  "hurt"  : -1,
  "break" : -2
}


class Model(Problem):
  def __init__(self, src):
    Problem.__init__(self)
    self.src = src
    self.properties = 'properties.json'
    self._tree = Parser(src)
    self._tree.parse()
    self._tree.remove_actors()
    self.roots = self._tree.get_roots()


  def generate(self):
    point_map = {}
    for node in self.roots:
      point_map[node.id] = random.choice([node.lo, node.hi])
    return point_map

