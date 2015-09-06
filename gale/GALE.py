from __future__ import print_function, division
import sys, os
sys.path.append(os.path.abspath("."))
from utils.lib import *
from utils.algorithm import Algorithm
from where import Node, sqrt

__author__ = 'panzer'

def settings():
  """
  Default Settings for NSGA 3
  :return: default settings
  """
  return O(
    pop_size        = 100,
    gens            = 250,
    allowDomination = True
  )

class GALE(Algorithm):
  """
  .. [Krall2015] Krall, Menzies et.all, "
      GALE: Geometric Active Learning for Search-Based Software Engineering"

  Check References folder for the paper
  """
  def __init__(self, problem, gens=settings().gens):
    """
    Initialize GALE algorithm
    :param problem: Instance of the problem
    :param gens: Max number of generations
    """
    Algorithm.__init__(self, 'GALE', problem)
    self.select = self._select
    self.evolve = self._evolve
    self.recombine = self._recombine
    self.gens = gens

  def run(self):
    population = Node.format(self.problem.population)

    gen = 0
    while gen < self.gens:
      total_evals = 0
      # SELECTION
      selectees, evals =  self.select(population)
      total_evals += evals

      # EVOLUTION
      selectees, evals = self.evolve(selectees)
      total_evals += evals

      population, evals = self.recombine(population, selectees, settings().pop_size)
      total_evals += evals

    return population


  def _select(self, pop):
    node = Node(self.problem, pop, settings().pop_size).divide(sqrt(pop))
    non_dom_leafs = node.nonpruned_leaves()
    all_leafs = node.leaves()

    # Counting number of evals
    evals = 0
    for leaf in all_leafs:
      for row in leaf._pop:
        if row.evaluated:
          evals+=1
    return non_dom_leafs, evals


  def _evolve(self, selected):
    pass

  def _recombine(self, population, mutants, total_size):
    pass

def _test():
  from problems.ZDT1 import ZDT1
  o = ZDT1()
  o.populate(100)
  gale = GALE(o)
  gale.select(Node.format(gale.problem.population))

if __name__ == "__main__":
  _test()