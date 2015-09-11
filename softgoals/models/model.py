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
    self.name = 'bCMS_SR_bCMS_AuthenticationVariation'
    self.src = src
    self.properties = 'properties.json'
    self._tree = Parser(src)
    self._tree.parse()

  def make_model(self):
    for node in self._tree.node:
      # identify decisions and objectives
      pass

f = open('properties.json', 'r')
txt = f.read()
f.close()
print(txt)


