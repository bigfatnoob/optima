from __future__ import print_function, division
import sys, os
sys.path.append(os.path.abspath("."))
from utils.lib import *
from algorithms.algorithm import Algorithm
from configs import spea2_settings as default_settings
import utils.tools as tools
from utils.distances import eucledian
from measures.convergence import convergence
import warnings

__author__ = 'panzer'

class SPEA2Point(Point):
  def __init__(self, decisions, problem=None):
    """
    Represents a point in the SPEA2 algorithm
    :param decisions: Set of decisions
    :param problem: Instance of the problem
    :return:
    """
    Point.__init__(self, decisions, problem)
    self.strength = None # Denoted as S in the paper
    self.raw_fitness = None # Denoted as R in the paper
    self.fitness = None # Denoted as F in the paper
    self.density = None # Denoted as D in the paper

  def clone(self):
    """
    Method to clone a point
    :return: Cloned instance of the point
    """
    new = SPEA2Point(self.decisions)
    new.objectives = self.objectives[:]
    new.norm_objectives = self.norm_objectives[:]
    return new

class SPEA2(Algorithm):
  """

  """
  def __init__(self, problem, population = None, **settings):
    Algorithm.__init__(self, "SPEA2", problem)
    self.settings = default_settings().update(**settings)
    self.population  = population
    self.archive = []
    self.evolve = self._evolve

  def run(self):
    """
    Runner function that runs the SPEA2 algorithm
    """
    start = get_time()
    if not self.population:
      self.population = self.problem.populate(self.settings.pop_size)
    self.population = [SPEA2Point(one, problem=self.problem) for one in self.population]
    for point in self.population: point.evaluate(self.problem, self.stat, 1)
    self.stat.update(self.population)
    self.fit_all()
    while self.gen < self.settings.gens:
      say(".")
      self.gen += 1
      self.archive = self.environmental_selection()
      self.stat.update(self.archive)
      self.population = self.evolve()
      assert len(self.population) == self.settings.pop_size
      assert len(self.archive) == self.settings.archive_size
      print(self.gen, convergence([one.objectives for one in self.archive], self.problem.get_pareto_front()))
    self.stat.runtime = get_time() - start
    return self.archive


  def fit_all(self):
    for point in self.population + self.archive:
      point.strength = self.calculate_strength(point)
    for point in self.population + self.archive:
      point.fitness = self.calculate_fitness(point)

  def calculate_strength(self, point):
    """
    Strength of a point is defined as the sum of the
    points it dominates in population and archive.
    :param point: Instance of SPEA2Point whose strength is calculated
    :return: Strength of point
    """
    strength = 0
    for other in self.population + self.archive:
      if tools.nsga_domination(self.problem, point, other) == 1:
        strength += 1
    return strength

  def calculate_fitness(self, point):
    """
    Raw fitness of a point is defined as the sum of the
    strengths of all points dominated by the point in
    the population and archive
    :param point: Instance of SPEA2Point whose raw fitness is calculated
    :return: Raw Fitness of a point
    """
    raw_fitness = 0
    distance_list = []
    k = int(round(math.sqrt(len(self.population) + len(self.archive))))
    for other in self.population + self.archive:
      if other == point: continue
      distance = eucledian(point.norm_objectives, other.norm_objectives)
      distance_list.append(distance)
      if tools.nsga_domination(self.problem, point, other) == 2:
        raw_fitness += other.strength
    k_nearest = sorted(distance_list)[k]
    point.density = 1 / (k_nearest + 2)
    point.raw_fitness = raw_fitness
    return point.raw_fitness + point.density

  def environmental_selection(self):
    archive_size = self.settings.archive_size
    archive = self.archive
    population = self.population
    new_archive = []
    all_points = sorted(set(archive + population), key=lambda x: x.fitness)
    for point in all_points:
      if point.fitness < 1:
        new_archive.append(point)
    if len(new_archive) < archive_size:
      return all_points[:archive_size]
    else:
      return self.prune_archive(new_archive)

  def prune_archive(self, archive):
    while True:
      point_distances = {}
      archive = shuffle(archive)
      for i in range(len(archive)-1):
        min_dist = sys.maxint
        for j in range(i+1, len(archive)):
          min_dist = min(eucledian(archive[i].norm_objectives, archive[j].norm_objectives), min_dist)
        points = point_distances.get(min_dist, [])
        points.append(archive[i])
        point_distances[min_dist] = points
      archive.remove(SPEA2.select_closest(point_distances))
      if len(archive) == self.settings.archive_size:
        return archive

  @staticmethod
  def select_closest(points_map):
    points = []
    for dist, points in sorted(points_map.items()):
      #print(dist, [point.id for point in points])
      if len(points) == 1:
        return points[0]
    exit()
    warnings.warn("None of the points have a size 1")
    return rand_one(points)

  def _evolve(self):
    population = []
    clones = [one.clone() for one in self.archive]
    while len(population) < self.settings.pop_size:
      mom = tools.binary_tournament_selection(self.problem, clones, 2, is_domination=True)
      dad = tools.binary_tournament_selection(self.problem, clones, 2, is_domination=True)
      sis, bro = tools.sbx(self.problem, mom.decisions, dad.decisions, eta=self.settings.sbx_eta)
      sis = tools.poly_mutate(self.problem, sis, eta=self.settings.pm_eta)
      bro = tools.poly_mutate(self.problem, bro, eta=self.settings.pm_eta)
      sis, bro = SPEA2Point(sis), SPEA2Point(bro)
      sis.evaluate(self.problem, self.stat, self.gen)
      bro.evaluate(self.problem, self.stat, self.gen)
      population += [sis, bro]
    return population



