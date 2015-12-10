from __future__ import print_function, division
import sys, os
sys.path.append(os.path.abspath("."))
from problems.problem import *

__author__ = 'panzer'

class DTLZ2(Problem):
  """
  Hypothetical test problem with
  "m" objectives and "n" decisions
  """
  k = 10
  def __init__(self, m, n=None):
    """
    Initialize DTLZ2 instance
    :param m: Number of objectives
    :param n: Number of decisions
    """
    Problem.__init__(self)
    self.name = DTLZ2.__name__
    if n is None:
      n = DTLZ2.default_decision_count(m)
    self.decisions = [Decision("x"+str(index+1),0,1) for index in range(n)]
    self.objectives = [Objective("f"+str(index+1), True, 0, 1000) for index in range(m)]

  @staticmethod
  def default_decision_count(m):
    return m + DTLZ2.k - 1

  def evaluate(self, decisions):
    m = len(self.objectives)
    n = len(decisions)
    k = n - m + 1
    g = 0
    for i in range(n - k, n):
      g += (decisions[i] - 0.5)**2
    f = [1 + g]*m
    for i in range(0, m):
      for j in range(0, m-(i+1)):
        f[i] *= cos(decisions[j] * PI / 2)
      if i != 0:
        f[i] *= sin(decisions[m-(i+1)] * PI / 2)
    return f

  def get_pareto_front(self):
    file_name = "problems/dtlz/PF/dtlz2_"+str(len(self.objectives))+"_objectives.txt"
    pf = []
    with open(file_name) as f:
      for line in f.readlines():
        pf.append(map(float,line.strip().replace("\n","").split(" ")))
    return pf