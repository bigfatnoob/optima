from __future__ import print_function, division
import sys
import os
sys.path.append(os.path.abspath("."))
from utils.lib import *
from utils.algorithm import Algorithm
import utils.tools as tools
import numpy as np
from reference import DIVISIONS, cover

__author__ = 'george'


def default_settings():
  """
  Default Settings for NSGA 2
  :return: default settings
  """
  return O(
    pop_size = 100,   # Size of Population
    gens = 250,       # Number of generations
    p_outer = 3,      # Divisions on outer boundary
    p_inner = None,   # Divisions on inner boundary
    cr = 1,           # Crossover rate for SBX
    nc = 30,          # eta for SBX
    nm = 20           # eta for Mutation
  )

def loo(points):
  """
  Iterator which generates a
  test case and training set
  :param points:
  :return:
  """
  for i in range(len(points)):
    one = points[i]
    rest = points[:i] + points[i+1:]
    yield one, rest

class NSGAPoint(Point):
  def __init__(self, decisions, problem=None):
    """
    Represents a point in the frontier for NSGA
    :param decisions: Set of decisions
    :param problem: Instance of the problem
    :param do_eval: Flag to check if evaluation has to be performed
    """
    Point.__init__(self, decisions, problem)
    self.rank = 0
    self.dominated = []
    self.dominating = 0

  def clone(self):
    """
    Method to clone a point
    :return:
    """
    new = NSGAPoint(self.decisions)
    new.objectives = self.objectives
    return new

class NSGA3(Algorithm):
  """
  An improved version of NSGA 2 that uses reference points to solve
  many objective optimization problem.
  .. [Deb2012] Deb and Jain, "An Evolutionary Many-Objective Optimization
      Algorithm Using Reference-Point-Based Nondominated Sorting Approach,
      Part I: Solving Problems With Box Constraints"

  Check References folder for the paper.
  """
  def __init__(self, problem, **settings):
    """
    Initial NSGA3 algorithm
    :param problem: Instance of the problem
    :param settings: Settings to be overridden
    """
    Algorithm.__init__(self, 'NSGA3', problem)
    self.settings = default_settings().update(**settings)
    self.select = self._select
    self.evolve = self._evolve
    self.frontiers = []
    self._reference = None

  def run(self):
    if not self.problem.population:
      self.problem.population = self.problem.populate(self.settings.pop_size)
    population = [NSGAPoint(one) for one in self.problem.population]
    pop_size = len(population)
    gens = 0
    while gens < self.settings.gens:
      say(".")
      population = self.select(population)
      population = self.evolve(population)
      exit()
      gens += 1
    print("")
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

  def _evolve(self, population):
    fronts = self.fast_non_dom_sort(population)
    s = []
    n = self.settings.pop_size
    last_index = 0
    for i, front in enumerate(fronts):
      if len(s) + len(front) >= n: break
      s += front
      last_index = i
    if len(s) == n:
      return s
    pop_next = []
    for j in range(last_index):
      pop_next += fronts[j]
    k = n - len(pop_next)
    ideal = self.get_ideal(population)
    extremes = self.get_extremes(population, ideal)
    worst = self.get_worst(population)
    intercepts = self.get_intercepts(extremes, ideal, worst)
    print(intercepts)
    reference = self.get_reference()

  def fast_non_dom_sort(self, population):
    """
    Fast Non Dominated Sort
    :param - Population to sort
    :return - List of Frontiers
    """
    frontiers = []
    front1 = []
    for one in population:
      one.evaluate(self.problem)
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

  def get_ideal(self, population):
    ideal = []
    for i, obj in enumerate(self.problem.objectives):
      f = min if obj.to_minimize else max
      ideal.append(f([one.objectives[i] for one in population]))
    return ideal

  def get_worst(self, population):
    worst = []
    for i, obj in enumerate(self.problem.objectives):
      f = max if obj.to_minimize else min
      worst.append(f([one.objectives[i] for one in population]))
    return worst

  def get_extremes(self, population, ideal):
    def asf(point, index):
      max_val = -sys.maxint
      eps = 1e-6
      for k, (o, idl) in enumerate(zip(point, ideal)):
        temp = abs(o - idl)
        if index != k:
          temp /= eps
        if temp > max_val:
          max_val = temp
      return max_val
    extremes = []
    for j, obj in enumerate(self.problem.objectives):
      extreme_index = -1
      min_val = sys.maxint
      for i, one in enumerate(population):
        asf_val = asf(one.objectives, j)
        if asf_val < min_val:
          min_val = asf_val
          extreme_index = i
      extremes += [population[extreme_index].objectives]
    return extremes

  def get_intercepts(self, extremes, ideal, worst):
    """
    Get Intercepts of the extreme points on each
    of the objective axis.
    :param extremes: Extreme points
    :param ideal: Ideal point
    :param worst: Worst point
    :return: Intercepts on each objective axis
    """
    norm_extremes = []
    for extreme in extremes:
      norm_extremes.append([e-i for e, i in zip(extreme, ideal)])
    norm_extremes = np.array(norm_extremes)
    intercepts = [-1] * len(self.problem.objectives)
    if np.linalg.matrix_rank(norm_extremes) == len(norm_extremes):
      unit = np.matrix([[1]]*len(self.problem.objectives))
      inv_extremes = np.linalg.inv(norm_extremes)
      intercepts_coeff = inv_extremes.dot(unit)
      intercepts_coeff = intercepts_coeff.tolist()
      for j in range(len(self.problem.objectives)):
        a_j = 1/intercepts_coeff[j][0] + ideal[j]
        if a_j > ideal[j]:
          intercepts[j] = a_j
      if j != len(self.problem.objectives)-1:
        intercepts = worst
    return intercepts

  def get_reference(self):
    if self._reference is None:
      m = len(self.problem.objectives)
      divs = DIVISIONS[m]
      self._reference = cover(m, divs[0], divs[1])
    return self._reference

