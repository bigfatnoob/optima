from __future__ import print_function, division
import sys, os
sys.path.append(os.path.abspath("."))
from problems.problem import *

__author__ = 'panzer'

class ZDT6(Problem):
  """
  No of Decisions = n = 10.
  No of Objectives = m = 2
  """
  def __init__(self):
    Problem.__init__(self)
    self.name = ZDT6.__name__
    self.decisions = [Decision("x"+str(index+1), 0, 1) for index in range(0, 10)]
    self.objectives = [Objective("f1", True, 0, 100), Objective("f2", True, 0, 100)]
    self.evals = 0
    self.ideal_decisions = None
    self.ideal_objectives = None

  def evaluate(self, decisions):
    g  = ZDT6.g(decisions)
    o0 = 1 - math.exp(-4*decisions[0]) * (sin(6*PI*decisions[0])**6)
    o1 = 1 - (o0/g)**2
    objectives = [o0, o1]
    return objectives

  @staticmethod
  def g(decisions):
    return 1 + 9 * (sum(decisions[1:])/(len(decisions)-1))**0.25

  def get_pareto_front(self):
    file_name = "problems/zdt/PF/zdt6.txt"
    pf = []
    with open(file_name) as f:
      for line in f.readlines():
        pf.append(map(float,line.replace("\n","").split(",")))
    return pf