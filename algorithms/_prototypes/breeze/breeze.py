from __future__ import print_function, division
import sys
import os
sys.path.append(os.path.abspath("."))
from utils.lib import *
from algorithms.algorithm import Algorithm
from where import Node

__author__ = 'panzer'

def default_settings():
  return O(
    pop_size        = 208,    # Size of Population
    gens            = 20,   # Number of generations
    allowDomination = True,   # Domination Flag
    gamma           = 0.15    # Gamma factor for mutation
  )



class Breeze(Algorithm):
  """

  """
  def __init__(self, problem, population = None, **settings):
    """
    Initialize the algorithm
    :param problem:
    :param population:
    :param settings:
    :return:
    """
    Algorithm.__init__(self, 'BREEZE', problem)
    self.settings = default_settings().update(**settings)
    self.select = self._select
    self.evolve = self._evolve
    self.population = population
    self.leaves = None
    self.frontiers = []

  def random_weights(self, size):
    """
    Normalized Random weights
    :param size:
    :return:
    """
    m = len(self.problem.objectives)
    wts = []
    for _ in range(size):
      wt = [random.random() for _ in xrange(m)]
      tot = sum(wt)
      wts.append([wt_i/tot for wt_i in wt])
    return wts

  def assign_references(self, leaves, references):
    refs = references[:]
    for leaf in shuffle(leaves):
      pop = leaf.get_pop()
      pt = pop[len(pop)//2]
      if not pt.evaluated:
        pt.evaluate(self.problem, self.stat, 1)
      nearest = sorted(refs, key = lambda ref : self.problem.dist(pt.objectives, ref, one_norm = True, two_norm = False, is_obj=True))[0]
      refs.remove(nearest)
      leaf.reference = nearest

  def run(self):
    popultaion = self.initialize()
    while self.gen < self.settings.gens:
      say(".")
      self.gen += 1

      #SELECTION


  def _select(self):
    pass

  def _evolve(self):
    pass

  def initialize(self):
    if not self.population:
      self.population = self.problem.populate(self.settings.pop_size)
    self.population = Node.format(self.population)
    threshold = 2 * len(self.population) ** 0.5
    leaves = Node(self.problem, self.population, len(self.population)).divide(threshold).leaves()
    references = self.random_weights(len(leaves))
    self.assign_references(leaves, references)
    self.leaves = leaves
    for leaf in leaves:
      leaf.max_size = len(leaf.get_pop())
      leaf.set_pop(get_quartile_range(leaf.get_pop()))
      print(len(leaf.get_pop()))
    return None

def get_quartile_range(lst):
  n = len(lst)
  return lst[n//4:3*n//4]

def _test():
  from problems.zdt.zdt1 import ZDT1
  o = ZDT1()
  algo = Breeze(o)
  algo.run()

if __name__ == "__main__":
  _test()
