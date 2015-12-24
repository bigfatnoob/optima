from __future__ import print_function, division
import sys, os
sys.path.append(os.path.abspath("."))
from utils.lib import *
from algorithms.algorithm import Algorithm
import utils.tools as tools
from configs import moead_settings as default_settings
from algorithms.nsga3.reference import cover, DIVISIONS
from utils.distances import eucledian
from decompositions import get_distance
from reproduction import get_crossover

__author__ = 'panzer'

class MOEADPoint(Point):
  def __init__(self, decisions, problem=None):
    """
    Represents a point in the frontier for MOEA/D
    :param decisions: list of decisions
    :param problem: Instance of problem
    :return:
    """
    Point.__init__(self, decisions, problem)
    self.wt_indices = None
    self.weight = None
    self.neighbor_ids = None

  def clone(self):
    """
    Method to clone a point
    :return:
    """
    new  = MOEADPoint(self.decisions)
    if self.objectives: new.objectives = self.objectives[:]
    if self.wt_indices: new.wt_indices = self.wt_indices[:]
    if self.weight: new.weight = self.weight[:]
    if self.neighbor_ids: new.neighbor_ids = self.neighbor_ids[:]
    return new


class MOEA_D(Algorithm):
  """
  Implements Zhang & Li's MOEAD algorithm
  """
  def __init__(self, problem, population=None, **settings):
    Algorithm.__init__(self, 'MOEA_D', problem)
    self.settings = default_settings().update(**settings)
    self.population = population
    self.ideal = [sys.maxint if obj.to_minimize else -sys.maxint for obj in self.problem.objectives]
    self.best_boundary_objectives = [None]*len(self.problem.objectives)
    self.distance = get_distance(self.settings.distance)
    self.crossover = get_crossover(self.settings.crossover)
    self.neighborhood = "local"


  def setup(self, population):
    """
    Mark each point with the nearest "T"
    weight vectors and return the global best.
    """
    self.init_weights(population)
    for key in population.keys():
      population[key].evaluate(self.problem, self.stat, 1)
    for one in population.keys():
      distances = []
      ids = []
      for two in population.keys():
        if one == two:
          continue
        ids.append(two)
        distances.append(eucledian(population[one].weight, population[two].weight))
      sorted_ids = [index for dist, index in sorted(zip(distances, ids))]
      population[one].neighbor_ids = sorted_ids[:self.settings.T]
    for key in population.keys():
      self.update_ideal(population[key])



  def init_weights(self, population):
    """
    Initialize weights. We first check if we can generate
    uniform weights using the Das Dennis Technique.
    If not, we randomly generate them.
    :param population:
    """
    m = len(self.problem.objectives)
    def random_weights():
      wts = []
      for _, __ in population.items():
        wt = [random.random() for _ in xrange(m)]
        tot = sum(wt)
        wts.append([wt_i/tot for wt_i in wt])
      return wts

    divs = DIVISIONS.get(m, None)
    weights = None
    if divs:
      weights = cover(m, divs[0], divs[1])
    if weights is None or len(weights) != len(population):
      weights = random_weights()
    assert len(weights) == len(population), "Number of weights != Number of points"
    weights = shuffle(weights)
    for i, key in enumerate(population.keys()):
      population[key].weight = weights[i]

  def reproduce(self, point, population):
    child = self.crossover(self, point, population)
    child = tools.poly_mutate(self.problem, child, eta=self.settings.nm)
    mutant = MOEADPoint(child)
    return mutant

  def run(self):
    #from measures.igd import igd
    start = get_time()
    #ideal_pf = self.problem.get_pareto_front()
    if self.population is None:
      self.population = self.problem.populate(self.settings.pop_size)
    population = {}
    for one in self.population:
      pt = MOEADPoint(one)
      population[pt.id] = pt
    self.setup(population)
    self.stat.update(population.values())
    while self.gen < self.settings.gens:
      say(".")
      self.gen += 1
      for point_id in shuffle(population.keys()):
        mutant = self.reproduce(population[point_id], population)
        mutant.evaluate(self.problem, self.stat, self.gen)
        self.update_ideal(mutant)
        self.update_neighbors(population[point_id], mutant, population)
      #objs = [population[pt_id].objectives for pt_id in population.keys()]
      self.stat.update(population.values())
    self.stat.runtime = get_time() - start
    return population


  def update_ideal(self, point):
    for i, obj in enumerate(self.problem.objectives):
      if obj.to_minimize:
        if point.objectives[i] < self.ideal[i]:
          self.ideal[i] = point.objectives[i]
          self.best_boundary_objectives[i] = point.objectives[:]
      else:
        if point.objectives[i] > self.ideal[i]:
          self.ideal[i] = point.objectives[i]
          self.best_boundary_objectives[i] = point.objectives[:]

  def update_neighbors(self, point, mutant, population):
    ids = point.neighbor_ids if self.neighborhood == "local" else population.keys()
    for neighbor_id in ids:
      neighbor = population[neighbor_id]
      neighbor_distance = self.distance(self, neighbor.objectives, neighbor.weight)
      mutant_distance = self.distance(self, mutant.objectives, neighbor.weight)
      if mutant_distance < neighbor_distance:
        population[neighbor_id].decisions = mutant.decisions
        population[neighbor_id].objectives = mutant.objectives

  def get_nadir_point(self, population):
    nadir = [-sys.maxint if obj.to_minimize else sys.maxint for obj in self.problem.objectives]
    for point in population.values():
      for i, obj in enumerate(self.problem.objectives):
        if obj.to_minimize:
          if point.objectives[i] > nadir[i]:
            nadir[i] = point.objectives[i]
        else:
          if point.objectives[i] < nadir[i]:
            nadir[i] = point.objectives[i]
    return nadir


if __name__ == "__main__":
  from problems.dtlz.dtlz1 import DTLZ1
  o = DTLZ1(3)
  moead = MOEA_D(o, pop_size=91, gens = 10)
  moead.run()
