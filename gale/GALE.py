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
    allowDomination = True,
    gamma           = 0.15
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
    best_solutions = []
    gen = 0
    while gen < self.gens:
      say(".")
      total_evals = 0
      # SELECTION
      selectees, evals =  self.select(population)
      solutions, evals = self.get_best(selectees)
      best_solutions += solutions
      total_evals += evals

      # EVOLUTION
      selectees, evals = self.evolve(selectees)
      total_evals += evals

      population, evals = self.recombine(selectees, settings().pop_size)
      total_evals += evals
      gen += 1
    print("")
    return best_solutions

  def get_best(self, non_dom_leaves):
    """
    Return the best row from all the
    non dominated leaves
    :param non_dom_leaves:
    :return:
    """
    bests = []
    evals = 0
    for leaf in non_dom_leaves:
      east = leaf._pop[0]
      west = leaf._pop[-1]
      if not east.evaluated:
        east.evaluate(self.problem)
        evals += 1
      if not west.evaluated:
        west.evaluate(self.problem)
        evals += 1
      weights = self.problem.directional_weights()
      weighted_west = [c*w for c,w in zip(west.objectives, weights)]
      weighted_east = [c*w for c,w in zip(east.objectives, weights)]
      objs = self.problem.objectives
      west_loss = loss(weighted_west, weighted_east, mins=[o.low for o in objs], maxs=[o.high for o in objs])
      east_loss = loss(weighted_east, weighted_west, mins=[o.low for o in objs], maxs=[o.high for o in objs])
      if east_loss < west_loss:
        bests.append(east)
      else:
        bests.append(west)
    return bests, evals


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
    evals = 0
    GAMMA = settings().gamma
    for leaf in selected:
      #Poles
      east = leaf._pop[0]
      west = leaf._pop[-1]
      # Evaluate poles if required
      if not east.evaluated:
        east.evaluate(self.problem)
        evals += 1
      if not west.evaluated:
        west.evaluate(self.problem)
        evals += 1

      weights = self.problem.directional_weights()
      weighted_west = [c*w for c,w in zip(west.objectives, weights)]
      weighted_east = [c*w for c,w in zip(east.objectives, weights)]
      objs = self.problem.objectives
      west_loss = loss(weighted_west, weighted_east, mins=[o.low for o in objs], maxs=[o.high for o in objs])
      east_loss = loss(weighted_east, weighted_west, mins=[o.low for o in objs], maxs=[o.high for o in objs])

      # Determine better Pole
      if east_loss < west_loss:
        south_pole,north_pole = east,west
      else:
        south_pole,north_pole = west,east

      # Magnitude of the mutations
      g = abs(south_pole.x - north_pole.x)

      for row in leaf._pop:
        clone = row.clone()
        clone_x = row.x
        for dec_index in range(len(self.problem.decisions)):
          # Few naming shorthands
          me    = row.decisions[dec_index]
          good  = south_pole.decisions[dec_index]
          bad   = north_pole.decisions[dec_index]
          dec   = self.problem.decisions[dec_index]

          if    me > good: d = -1
          elif  me < good: d = +1
          else           : d =  0

          # Mutating towards the better solution
          row.decisions[dec_index] = min(dec.high, max(dec.low, me + me * g * d))
        # Project the mutant
        a = row.dist(self.problem, north_pole, is_obj=False)
        b = row.dist(self.problem, south_pole, is_obj=False)
        x = (a**2 + row.c**2 - b**2) / (2*row.c+0.00001)
        row.x = x
        if abs(x - clone_x) > (g * GAMMA) or not self.problem.evaluate_constraints(row)[0]:
          row.decisions = clone.decisions
          row.x = clone_x

    pop = []
    for leaf in selected:
      for row in leaf._pop:
        if row.evaluated:
          row.evaluate(self.problem) # Re-evaluating
        pop.append(row)

    return pop, evals

  def _recombine(self, mutants, total_size):
    remaining = total_size - len(mutants)
    pop = []
    for _ in range(remaining):
      pop.append(self.problem.generate())
    return mutants + Node.format(pop), 0

def _test():
  from problems.ZDT1 import ZDT1
  o = ZDT1()
  o.populate(100)
  gale = GALE(o)
  gale.run()

if __name__ == "__main__":
  _test()