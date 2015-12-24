from __future__ import print_function, division
import sys
import os

sys.path.append(os.path.abspath("."))
from utils.lib import *
from algorithms.algorithm import Algorithm
from where import Node, sqrt
from configs import gale_settings as default_settings

__author__ = 'panzer'


class GALE(Algorithm):
  """
  .. [Krall2015] Krall, Menzies et.all, "
      GALE: Geometric Active Learning for Search-Based Software Engineering"

  Check References folder for the paper
  """
  def __init__(self, problem, population = None, **settings):
    """
    Initialize GALE algorithm
    :param problem: Instance of the problem
    :param gens: Max number of generations
    """
    Algorithm.__init__(self, 'GALE', problem)
    self.select = self._select
    self.evolve = self._evolve
    self.recombine = self._recombine
    self.population = population
    self.settings = default_settings().update(**settings)
    self.is_pareto = False # Indicates if final population represents the pareto front

  def run(self):
    start = get_time()
    if not self.population:
      self.population = self.problem.populate(self.settings.pop_size)
    population = Node.format(self.population)
    best_solutions = []
    while self.gen < self.settings.gens:
      say(".")
      self.gen += 1
      # SELECTION
      selectees = self.select(population)
      solutions = self.get_best(selectees)
      self.stat.update(solutions)
      best_solutions += solutions

      # EVOLUTION
      selectees = self.evolve(selectees)

      population = self.recombine(selectees, self.settings.pop_size)
    self.stat.runtime = get_time() - start
    return best_solutions

  def get_best(self, non_dom_leaves):
    """
    Return the best row from all the
    non dominated leaves
    :param non_dom_leaves:
    :return:
    """
    bests = []
    for leaf in non_dom_leaves:
      east = leaf.get_pop()[0]
      west = leaf.get_pop()[-1]
      if not east.evaluated:
        east.evaluate(self.problem, self.stat, self.gen)
      if not west.evaluated:
        west.evaluate(self.problem, self.stat, self.gen)
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
    return bests


  def _select(self, pop):
    node = Node(self.problem, pop, self.settings.pop_size).divide(sqrt(pop))
    non_dom_leafs = node.nonpruned_leaves()
    return non_dom_leafs


  def _evolve(self, selected):
    gamma = self.settings.gamma
    for leaf in selected:
      #Poles
      east = leaf.get_pop()[0]
      west = leaf.get_pop()[-1]
      # Evaluate poles if required
      if not east.evaluated:
        east.evaluate(self.problem, self.stat, self.gen)
      if not west.evaluated:
        west.evaluate(self.problem, self.stat, self.gen)

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

      for row in leaf.get_pop():
        clone = row.clone()
        clone_x = row.x
        for dec_index in range(len(self.problem.decisions)):
          # Few naming shorthands
          me    = row.decisions[dec_index]
          good  = south_pole.decisions[dec_index]
          #bad   = north_pole.decisions[dec_index]
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
        if abs(x - clone_x) > (g * gamma) or not self.problem.evaluate_constraints(row)[0]:
          row.decisions = clone.decisions
          row.x = clone_x

    pop = []
    for leaf in selected:
      for row in leaf.get_pop():
        if row.evaluated:
          row.evaluate(self.problem, self.stat, self.gen) # Re-evaluating
        pop.append(row)

    return pop

  def _recombine(self, mutants, total_size):
    remaining = total_size - len(mutants)
    pop = []
    for _ in range(remaining):
      pop.append(self.problem.generate())
    return mutants + Node.format(pop)

if __name__ == "__main__":
  from problems.dtlz.dtlz1 import DTLZ1
  prob = DTLZ1(3)
  gale = GALE(prob, pop_size=91, gens = 30)
  gale.run()