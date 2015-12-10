from __future__ import print_function, division
import sys, os
sys.path.append(os.path.abspath("."))
from problems.problem import *

__author__ = 'panzer'

class DTLZ5(Problem):
  """
  Hypothetical test problem with
  "m" objectives and "n" decisions
  """
  k = 10
  def __init__(self, m, n=None):
    """
    Initialize DTLZ5 instance
    :param m: Number of objectives
    :param n: Number of decisions
    """
    Problem.__init__(self)
    self.name = DTLZ5.__name__
    if n is None:
      n = DTLZ5.default_decision_count(m)
    self.decisions = [Decision("x"+str(index+1),0,1) for index in range(n)]
    self.objectives = [Objective("f"+str(index+1), True, 0, 1000) for index in range(m)]

  @staticmethod
  def default_decision_count(m):
    return m + DTLZ5.k - 1

  def evaluate(self, decisions):
    m = len(self.objectives)
    n = len(decisions)
    k = n - m + 1
    # Compute g
    g = 0
    for i in range(n - k, n):
      g += decisions[i]**0.1
    # Compute theta
    theta = [decisions[0]*PI/2]
    t = PI / (4 * (1 + g))
    for i in range(1, m-1):
      theta.append(t * (1 + 2*g*decisions[i]))
    #Compute f
    f = [1 + g]*m
    for i in range(0, m):
      for j in range(0, m-(i+1)):
        f[i] *= cos(theta[j])
      if i != 0:
        f[i] *= sin(theta[m-(i+1)])
    return f