from __future__ import print_function, division
import sys, os
sys.path.append(os.path.abspath("."))
from utils.lib import *
from utils.algorithm import Algorithm
from configs import de_settings as default_settings

__author__ = 'panzer'

class DE(Algorithm):
  """
  Created by Storn and Price, differential evolution (DE) is a method that optimizes
  a problem by iteratively trying to improve a candidate solution with regard to a
  given measure of quality.
  ..[Storn 97] Storn and Price, "Differential Evolution - A Simple and Efficient
    Heuristic for Global Optimization over Continuous Spaces"
  """
  def __init__(self, problem, population=None, **settings):
    """
    Initialize DE algorithm
    :param problem: Instance of problems
    :param settings: Settings to be overridden
    """
    Algorithm.__init__(self, 'DE', problem)
    self.settings = default_settings().update(**settings)
    self.settings.pop_size = len(self.problem.decisions)*10
    self.population = population
    self.select = self._select
    self.evolve = self._evolve


  def run(self):
    if not self.population:
      self.population = self.problem.populate(self.settings.pop_size)
    population = [Point(one) for one in self.population]
    gens = 0
    while gens < self.settings.gens:
      say(".")
      selected = self.select(population)
      population = self.evolve(selected, population)
      print(gens, self.IGD(population, self.problem.get_pareto_front()))
      gens += 1
    return population

  def _select(self, population):
    clones = []
    for one in population:
      clone = one.clone()
      clone.evaluate(self.problem)
      clones.append(clone)
    assert self.settings.pop_size == len(clones), "Size mismatch"
    return clones

  def _evolve(self, selected, population):
    for point in population:
      point.evaluate(self.problem)
      mutant = self.mutate(point, population)
      mutant.evaluate(self.problem)
      if self.problem.binary_dominates(mutant, point) == 1:
        selected.remove(point)
        selected.append(mutant)
    return selected

  def mutate(self, one, population):
    """
    Mutate point "one".
    :param one: Point to be mutated
    :param population: Population to mutate from
    :return:
    """
    decisions = self.problem.decisions
    two, three, four = DE.three_others(one, population)
    random_index  = rand_one(range(len(decisions)))
    mutated_decisions = one.decisions[:]
    for i in range(len(decisions)):
      if (random.random() < self.settings.cr) or (i == random_index):
        mutated_decisions[i] = decisions[i].trim(two.decisions[i] + self.settings.f*(three.decisions[i] - four.decisions[i]))
    return Point(mutated_decisions)

  @staticmethod
  def three_others(one, pop):
    """
    Return three other points from population
    :param one: Point not to consider
    :param pop: Population to look in
    :return: two, three, four
    """
    def one_other():
      while True:
        x = rand_one(pop)
        if not x.id in seen:
          seen.append(x.id)
          return x
    seen = [one.id]
    two = one_other()
    three = one_other()
    four = one_other()
    return two, three, four




