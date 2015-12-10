"""
Statistics for running an
optimizer on a problem
"""
from __future__ import print_function,division
import sys, os
sys.path.append(os.path.abspath("."))
__author__ = 'panzer'

class Stat:
  def __init__(self, problem):
    """
    Initialize the statistic object
    :param problem: Instance of problem
    :return:
    Stat object that contains
    - problem
    - generations: population for each generation
    - evals: total number of evaluations
    - runtime: total runtime of optimization
    - IGD: Inverse Generational Distance for each generation
    - spread: Spread for each generation
    - hyper_volume: Hypervolume for each generation
    """
    self.problem = problem
    self.generations = None
    self.evals = 0
    self.runtime = None
    self.IGD = None
    self.spread = None
    self.hyper_volume = None

  def update(self, population, evals = 0):
    if self.generations is None:
      self.generations = []
    self.generations.append(population)
    self.evals += evals
