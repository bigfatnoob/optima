from __future__ import print_function, division
__author__ = 'panzer'
import sys, os
sys.path.append(os.path.abspath("."))
import sys
import numpy as np
from lib import O

class Algorithm(O):
  def __init__(self, name, problem):
    """
    Base class algorithm
    :param name: Name of the algorithm
    :param problem: Instance of the problem
    :return:
    """
    O.__init__(self)
    self.name = name
    self.problem = problem
    self.select = None
    self.evolve = None
    self.recombine = None

  def convergence(self, obtained):
    """
    Calculate the convergence metric with respect to ideal
    solutions
    """
    problem = self.problem
    if problem.constraints:
      return
    ideals = problem.get_ideal_objectives()
    for o in obtained:
      if not o.objectives:
        o.objectives = self.problem.evaluate(o.decisions)
    predicts = [o.objectives for o in obtained]
    gammas = []
    for predict in predicts:
      gammas.append(min([problem.dist(predict, ideal, one_norm = True, two_norm = True) for ideal in ideals]))
    return np.mean(gammas)

  @staticmethod
  def solution_range(obtained):
    """
    Calculate the range for each objective
    """
    predicts = [o.objectives for o in obtained]
    solutions = [[] for _ in range(len(predicts[0]))]
    for predict in predicts:
      for i in range(len(predict)):
        solutions[i].append(predict[i])
    for i, solution in enumerate(solutions):
      print("Objective :",i,
            "   Max = ", max(solutions[i]),
            "   Min = ", min(solutions[i]))

  def diversity(self, obtained):
    """
    Calculate the diversity of the spread for a
    set of solutions
    """
    def closest(one, many):
      min_dist = sys.maxint
      closest_point = None
      for this in many:
        dist = self.problem.dist(this, one, one_norm = True, two_norm = True)
        if dist < min_dist:
          min_dist = dist
          closest_point = this
      return min_dist, closest_point

    problem = self.problem
    if problem.constraints:
      return
    ideals = problem.get_ideal_objectives()
    for o in obtained:
      if not o.objectives:
        o.objectives = problem.evaluate(o.decisions)
    predicts = [o.objectives for o in obtained]
    d_f = closest(ideals[0], predicts)[0]
    d_l = closest(ideals[-1], predicts)[0]
    distances = []
    for i in range(len(predicts)-1):
      distances.append(problem.dist(predicts[i], predicts[i+1], one_norm = True, two_norm = True))
    d_bar = np.mean(distances)
    d_sum = sum([abs(d_i - d_bar) for d_i in distances])
    delta = (d_f + d_l + d_sum) / (d_f + d_l + (len(predicts) - 1)*d_bar)
    return delta

  def run(self):
    pass
