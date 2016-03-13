from __future__ import print_function, division
import sys
import os

sys.path.append(os.path.abspath("."))
from utils.lib import *
from algorithms.algorithm import Algorithm
import utils.tools as tools
from configs import nsga2_settings as default_settings


class NSGAPoint(Point):

  def __init__(self, decisions, problem=None):
    """
    Represents a point in the frontier for NSGA
    :param decisions: Set of decisions
    :param problem: Instance of the problem
    """
    Point.__init__(self, decisions, problem)
    self.rank = 0
    self.dominated = []
    self.dominating = 0
    self.crowd_dist = 0

  def clone(self):
    """
    Method to clone a point
    :return:
    """
    new = NSGAPoint(self.decisions)
    new.objectives = self.objectives[:]
    return new

  def __gt__(self, other):
    if self.rank != other.rank:
      return self.crowd_dist > other.crowd_dist
    else:
      return self.rank < other.rank


class NSGA2(Algorithm):
  """
  Sort the first *k* *individuals* into different non-domination levels
  using the "Fast Non-dominated Sorting Approach" proposed by Deb et al.,
  see [Deb2002]_. This algorithm has a time complexity of :math:`O(MN^2)`,
  where :math:`M` is the number of objectives and :math:`N` the number of
  individuals.

  .. [Deb2002] Deb, Pratab, Agarwal, and Meyarivan, "A fast elitist
     non-dominated sorting genetic algorithm for multi-objective
     optimization: NSGA-II", 2002.

  Check References folder for the paper
  """
  def __init__(self, problem, population = None, **settings):
    """
    Initialize NSGA2 algorithm
    :param problem: Instance of the problem
    :param settings: Settings to be overridden
    """
    Algorithm.__init__(self, 'NSGA2',problem)
    self.settings = default_settings().update(**settings)
    self.select = self._select
    self.evolve = self._evolve
    self.population = population
    self.frontiers = []


  def run(self):
    """
    Runner function that runs the NSGA2 optimization algorithm
    """
    start = get_time()
    if not self.population:
      self.population = self.problem.populate(self.settings.pop_size)
    population = [NSGAPoint(one) for one in self.population]
    pop_size = len(population)
    self.stat.update(population)
    while self.gen < self.settings.gens:
      say(".")
      self.gen += 1
      population = self.select(population)
      population = self.evolve(population, pop_size)
      self.stat.update(population)
    self.stat.runtime = get_time() - start
    return population


  def _select(self, population, is_domination = True):
    """
    Selector Function
    :param population: Population
    :param is_domination: Boolean parameter that decides
    :return : Population and its kids
    """
    kids = []
    clones = [one.clone() for one in population]

    for _ in range(len(clones)):
      mom = tools.binary_tournament_selection(self.problem, clones, 4, is_domination)
      dad = None
      while True:
        dad = tools.binary_tournament_selection(self.problem, clones, 4, is_domination)
        if not mom == dad: break
      sis, bro = tools.sbx(self.problem, mom.decisions, dad.decisions)
      sis = tools.poly_mutate(self.problem, sis)
      bro = tools.poly_mutate(self.problem, bro)
      kids += [NSGAPoint(sis), NSGAPoint(bro)]
    return clones + kids


  def _evolve(self, population, size):
    """
    Mutator Function: Performs crossover and polynomial mutation
    :param population:Population that needs to be evolved
    :param size: Expected size of the result
    :return : The mutated population
    """
    fronts = self.fast_non_dom_sort(population)
    pop_next = []
    for i, front in enumerate(fronts):
      if len(pop_next) + len(fronts[i]) >= size:
        fronts[i] = self.assign_crowd_dist(front)
        pop_next += sorted(fronts[i], key=lambda x:x.crowd_dist, reverse=True)[:(size - len(pop_next))]
        break
      else:
        pop_next += fronts[i]
    return pop_next

  def fast_non_dom_sort(self, population):
    """
    Fast Non Dominated Sort
    :param - Population to sort
    :return - List of Frontiers
    """
    frontiers = []
    front1 = []
    for one in population:
      one.evaluate(self.problem, self.stat, self.gen)
    for one, rest in loo(population):
      for two in rest:
        domination_status = tools.nsga_domination(self.problem, one, two)
        if domination_status == 1:
          one.dominated.append(two)
        elif domination_status == 2:
          one.dominating += 1
      if one.dominating == 0:
        one.rank = 1
        front1.append(one)
    current_rank = 1
    frontiers.append(front1)
    while True:
      front2 = []
      for one in front1:
        for two in one.dominated:
          two.dominating -= 1
          if two.dominating == 0:
            two.rank =  current_rank + 1
            front2.append(two)
      current_rank += 1
      if len(front2) == 0 :
        break
      else :
        frontiers.append(front2)
        front1 = front2
    return frontiers

  def assign_crowd_dist(self, frontier):
    """
    Crowding distance between each point in
    a frontier.
    """
    l = len(frontier)
    for m in range(len(self.problem.objectives)):
      frontier = sorted(frontier, key=lambda x:x.objectives[m])
      frontier[0].crowd_dist = float("inf")
      frontier[-1].crowd_dist = float("inf")
      for i in range(1,l-1):
        frontier[i].crowd_dist += (frontier[i+1].objectives[m] - frontier[i-1].objectives[m])
    return frontier


if __name__ == "__main__":
  from problems.dtlz.dtlz1 import DTLZ1
  o = DTLZ1(3)
  nsga2 = NSGA2(o, pop_size=91, gens = 10)
  nsga2.run()