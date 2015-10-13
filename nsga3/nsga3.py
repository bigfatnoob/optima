from __future__ import print_function, division
import sys
import os
sys.path.append(os.path.abspath("."))
from utils.lib import *
from utils.algorithm import Algorithm
import utils.tools as tools

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

  def run(self):
    if not self.problem.population:
      self.problem.population = self.problem.populate(self.settings.pop_size)
    population = [NSGAPoint(one) for one in self.problem.population]
    pop_size = len(population)
    gens = 0
    while gens < self.settings.gens:
      say(".")
      population = self.select(population)
      population = self.evolve(population, pop_size)
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