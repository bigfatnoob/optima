from __future__ import print_function, division
import sys, os
sys.path.append(os.path.abspath("."))
from utils.lib import *
from algorithms.algorithm import Algorithm
import utils.tools as tools
import numpy as np
from copy import deepcopy
from reference import DIVISIONS, cover
from configs import nsga3_settings as default_settings
from measures.igd import igd

__author__ = 'george'

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
    """
    Point.__init__(self, decisions, problem)
    self.rank = 0
    self.dominated = []
    self.dominating = 0
    self.norm_objectives = None
    self.perpendicular = None
    self.reference_id = None

  def clone(self):
    """
    Method to clone a point
    :return:
    """
    new = NSGAPoint(self.decisions)
    new.objectives = self.objectives[:]
    if self.norm_objectives:
      new.norm_objectives = self.norm_objectives[:]
    return new


class NSGA3(Algorithm):
  """
  An improved version of NSGA 2 that uses reference points to solve
  many objective optimization problem.
  .. [Deb2012] Deb and Jain, "An Evolutionary Many-Objective Optimization
      Algorithm Using Reference-Point-Based Non-dominated Sorting Approach,
      Part I: Solving Problems With Box Constraints"

  Check References folder for the paper.
  """
  def __init__(self, problem, population = None, **settings):
    """
    Initial NSGA3 algorithm
    :param problem: Instance of the problem
    :param settings: Settings to be overridden
    """
    Algorithm.__init__(self, 'NSGA3', problem)
    self.settings = default_settings().update(**settings)
    self.select = self._select
    self.evolve = self._evolve
    self.population = population
    self.frontiers = []

  def populate(self):
    return self.problem.populate(self.settings.pop_size)

  def run(self):
    start = get_time()
    if not self.population:
      self.population = self.populate()
    population = [NSGAPoint(one) for one in self.population]
    self.stat.update(population)
    while self.gen < self.settings.gens:
      say(".")
      self.gen += 1
      population = self.select(population)
      population = self.evolve(population)
      self.stat.update(population)
      #print(self.gen, igd([one.objectives for one in population], self.problem.get_pareto_front()))
    self.stat.runtime = get_time() - start
    return population

  def _select(self, population):
    """
    Selector Function
    :param population: Population
    :return : Population and its kids
    """
    kids = []
    clones = [one.clone() for one in population]

    for mom in shuffle(clones):
      dad = None
      while True:
        dad = rand_one(clones)
        if not mom == dad: break
      sis, _ = tools.sbx(self.problem, mom.decisions, dad.decisions)
      sis = tools.poly_mutate(self.problem, sis)
      kids += [NSGAPoint(sis)]
    return clones + kids

  def _evolve(self, population):
    fronts = self.fast_non_dom_sort(population)
    tot = 0
    for f in fronts:
      tot += len(f)
    s = []
    n = self.settings.pop_size
    last_index = 0
    for i, front in enumerate(fronts):
      s += front
      last_index = i
      if len(s)>= n: break
    if len(s) == n:
      return s
    pop_next = []
    for j in range(last_index):
      pop_next += fronts[j]
    # If the top ranked solution is not satisfied the
    # entire batch is unsatisfied. Hence reducing unneccesary computation.
    if not self.problem.check_constraints(s[0].decisions):
      return s[:self.settings.pop_size]
    s = self.normalize(s)
    references = self.get_references()
    self.associate(s, references)
    pop_next = self.niche(s, pop_next, references)
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

  def get_ideal(self, population):
    ideal = []
    for i, obj in enumerate(self.problem.objectives):
      f = min if obj.to_minimize else max
      ideal.append(f([one.objectives[i] for one in population if self.problem.check_constraints(one.decisions)]))
      #ideal.append(f([one.objectives[i] for one in population]))
    return ideal

  def get_worst(self, population):
    worst = []
    for i, obj in enumerate(self.problem.objectives):
      f = max if obj.to_minimize else min
      worst.append(f([one.objectives[i] for one in population if self.problem.check_constraints(one.decisions)]))
      #worst.append(f([one.objectives[i] for one in population]))
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
      extremes += [population[extreme_index].objectives[:]]
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
      j = -1
      for j, obj in enumerate(self.problem.objectives):
        a_j = 1/intercepts_coeff[j][0] + ideal[j]
        f = gt if obj.to_minimize else lt
        if f(a_j, ideal[j]):
          intercepts[j] = a_j
        else:
          break
      if j != len(self.problem.objectives)-1:
        intercepts = worst
    else:
      intercepts = worst
    return intercepts

  def normalize(self, points):
    """
    Normalize set of points
    :param points:
    :return:
    """
    ideal = self.get_ideal(points)
    extremes = self.get_extremes(points, ideal)
    worst = self.get_worst(points)
    intercepts = self.get_intercepts(extremes, ideal, worst)
    for point in points:
      norm_objectives = []
      for i, o in enumerate(point.objectives):
        if self.problem.objectives[i].to_minimize:
          norm_objectives.append((o-ideal[i])/(intercepts[i] - ideal[i] + 0.0000001))
        else:
          norm_objectives.append((ideal[i]-o)/(ideal[i] - intercepts[i] + 0.0000001))
      point.norm_objectives=norm_objectives
    return points

  @staticmethod
  def associate(population, references):
    """
    Associate a set of points to a set of
    reference vectors
    :param population: List of NSGAPoint
    :param references: List of reference vectors
    :return: population with each normalized vector
    associated with a reference vector
    """
    for point in population:
      min_dist = sys.maxint
      index = None
      for i, reference in enumerate(references):
        dist = NSGA3.perpendicular(point.norm_objectives, reference)
        if dist < min_dist:
          min_dist = dist
          index = i
      point.perpendicular = min_dist
      point.reference_id = index
    return population

  @staticmethod
  def perpendicular(vector, reference):
    """
    Perpendicular distance between a
    vector and its projection on a reference
    :param vector: Point to be projected. List of float
    :param reference: Reference to be projected on. List of float
    :return:
    """
    projection = 0
    reference_len = 0
    for v, r in zip(vector, reference):
      projection += v*r
      reference_len += r**2
    reference_len **= 0.5
    projection = abs(projection)/reference_len
    normal = 0
    for v, r in zip(vector, reference):
      normal += (v - projection*r/reference_len)**2
    return normal**0.5

  def niche(self, all_points, current_points, references):
    """
    Get Niche points for next generation from
    population
    :param all_points: Points to select from
    :param current_points: Population
    :param references: Reference points
    :return:
    """
    n = self.settings.pop_size
    k = n - len(current_points)
    last_points = deepcopy(all_points[len(current_points):])
    ref_counts = [0] * len(references)
    ref_status = [False] * len(references)
    for point in current_points:
      ref_counts[point.reference_id] += 1

    index = 0
    while index < k:
      ref_ids = shuffle(range(len(references)))
      least = sys.maxint
      ref_id = -1
      for ref_index in ref_ids:
        if not ref_status[ref_index] and ref_counts[ref_index] < least:
          least = ref_counts[ref_index]
          ref_id = ref_index
      feasibles = []
      for point in last_points:
        if point.reference_id == ref_id:
          feasibles.append(point)
      if feasibles:
        best_point = 0
        if ref_counts[ref_id] == 0:
          least_dist = sys.maxint
          for point in feasibles:
            if point.perpendicular < least_dist:
              least_dist = point.perpendicular
              best_point = point
        else:
          best_point = rand_one(feasibles)
        current_points.append(best_point)
        ref_counts[ref_id]+=1
        last_points.remove(best_point)
        index += 1
      else:
        ref_status[ref_id] = True
    assert len(current_points) == self.settings.pop_size, "Oops population mismatch."
    return current_points

  def get_references(self):
    """
    Get reference points for problems
    :return:
    """
    if self._reference is None:
      m = len(self.problem.objectives)
      divs = DIVISIONS[m]
      self._reference = cover(m, divs[0], divs[1])
    return self._reference


if __name__ == "__main__":
  from problems.dtlz.dtlz1 import DTLZ1
  o = DTLZ1(3)
  nsga3 = NSGA3(o, pop_size=92, gens = 400)
  nsga3.run()