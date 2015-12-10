from __future__ import print_function, division
import sys, os
sys.path.append(os.path.abspath("."))
from problems.problem import *

__author__ = 'panzer'

class DTLZ6(Problem):
  """
  Hypothetical test problem with
  "m" objectives and "n" decisions
  """
  k = 20
  def __init__(self, m, n=None):
    """
    Initialize DTLZ6 instance
    :param m: Number of objectives
    :param n: Number of decisions
    """
    Problem.__init__(self)
    self.name = DTLZ6.__name__
    if n is None:
      n = DTLZ6.default_decision_count(m)
    self.decisions = [Decision("x"+str(index+1),0,1) for index in range(n)]
    self.objectives = [Objective("f"+str(index+1), True, 0, 1000) for index in range(m)]

  @staticmethod
  def default_decision_count(m):
    return m + DTLZ6.k - 1

  def evaluate(self, decisions):
    m = len(self.objectives)
    n = len(decisions)
    k = n - m + 1
    # Compute g
    g = 0
    for i in range(n - k, n):
      g += decisions[i]
    g = 1 + 9 * g / k

    f = decisions[:m-1]
    h = 0
    for f_i in f:
      h += f_i * (1 + sin(3*PI*f_i)) / (1 + g)
    h = m - h
    f.append((1 + g) * h)
    return f