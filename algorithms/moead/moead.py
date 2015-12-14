from __future__ import print_function, division
import sys, os
import random
sys.path.append(os.path.abspath("."))
from utils.lib import *
from algorithms.algorithm import Algorithm
import utils.tools as tools
from configs import moead_settings as default_settings
from algorithms.nsga3.reference import cover, DIVISIONS

__author__ = 'panzer'

class MOEAD_Point(Point):
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

  def clone(self):
    """
    Method to clone a point
    :return:
    """
    new  = MOEAD_Point(self.decisions)
    if self.objectives:
      new.objectives = self.objectives[:]
    new.wt_indices = self.wt_indices[:]
    new.weight = self.weight[:]


class MOEA_D(Algorithm):
  def __init__(self, problem, population=None, **settings):
    Algorithm.__init__(self, 'MOEA/D', problem)
    self.settings = default_settings().update(**settings)
    self.population = population

  def setup(self):
    pass

  def init_weights(self, population):
    m = len(self.problem.objectives)
    def random_weights():
      wts = []
      for _ in population:
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
    for i, point in enumerate(population):
      point.weight = weights[i]

  def run(self):
    if self.population is None:
      self.population = self.problem.populate(self.settings.pop_size)
    population = [MOEAD_Point(one) for one in self.population]


