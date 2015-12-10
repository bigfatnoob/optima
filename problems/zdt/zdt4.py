from __future__ import print_function, division
import sys, os
sys.path.append(os.path.abspath("."))
from problems.problem import *

__author__ = 'panzer'

class ZDT4(Problem):
  """
  No of Decisions = n = 10.
  No of Objectives = m = 2
  """
  def __init__(self):
    Problem.__init__(self)
    self.name = ZDT4.__name__
    self.decisions = [Decision("x1", 0, 1)] + [Decision("x"+str(index+1),-5,5) for index in range(1,10)]
    self.objectives = [Objective("f1", True, 0, 100), Objective("f2", True, 0, 100)]
    self.evals = 0
    self.ideal_decisions = None
    self.ideal_objectives = None

  def evaluate(self, decisions):
    o0 = decisions[0]
    g  = ZDT4.g(decisions)
    o1 = g*(1 - (o0/g)**2)
    objectives = [o0, o1]
    return objectives

  @staticmethod
  def g(decisions):
    g_val = 1 + 10*(len(decisions) - 1)
    for i in range(1, len(decisions)):
      g_val += decisions[i]**2 - 10*cos(4*PI*decisions[i])
    return g_val

  def get_pareto_front(self):
    file_name = "problems/zdt/PF/zdt4.txt"
    pf = []
    with open(file_name) as f:
      for line in f.readlines():
        pf.append(map(float,line.replace("\n","").split(",")))
    return pf