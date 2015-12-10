from __future__ import print_function, division
__author__ = 'panzer'
import sys, os
sys.path.append(os.path.abspath("."))
from utils.lib import O
from utils.stat import Stat

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
    self.stat = Stat(problem)
    self.select = None
    self.evolve = None
    self.recombine = None
    self._reference = None

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

  def run(self):
    assert False
