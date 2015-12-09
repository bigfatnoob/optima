from __future__ import print_function, division
import sys, os
sys.path.append(os.path.abspath("."))
from problems.problem import *

__author__ = 'george'

class DTLZ1(Problem):
  """
  Hypothetical test problem with
  "m" objectives and "n" decisions
  """
  k = 5
  def __init__(self, m, n = None):
    Problem.__init__(self)
    self.name = DTLZ1.__name__
    if n is None:
      n = DTLZ1.default_decision_count(m)
    self.decisions = [Decision("x"+str(index+1),0,1) for index in range(n)]
    self.objectives = [Objective("f"+str(index+1), True, 0, 1000) for index in range(m)]

  @staticmethod
  def default_decision_count(m):
    return m + DTLZ1.k - 1

  def evaluate(self, decisions):
    m = len(self.objectives)
    n = len(decisions)
    k = n - m + 1
    g = 0
    for i in range(n - k, n):
      g += ((decisions[i] - 0.5)**2 - cos(20.0 * PI * (decisions[i] - 0.5)))
    g = 100 * (k + g)
    f = []
    for i in range(0, m): f.append((1.0 + g)*0.5)
    for i in xrange(m):
      for j in range(0, m-(i+1)): f[i] *= decisions[j]
      if not (i==0):
        aux = m - (i+1)
        f[i] *= 1 - decisions[aux]
    return f

  def get_pareto_front(self):
    file_name = "problems/dtlz/PF/dtlz1_"+str(len(self.objectives))+"_objectives.txt"
    pf = []
    with open(file_name) as f:
      for line in f.readlines():
        pf.append(map(float,line.replace("\n","").split(" ")))
    return pf
