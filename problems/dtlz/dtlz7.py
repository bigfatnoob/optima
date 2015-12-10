from __future__ import print_function, division
import sys, os
sys.path.append(os.path.abspath("."))
from problems.problem import *

__author__ = 'panzer'

def floor(val):
  return int(math.floor(val))

class DTLZ7(Problem):
  """
  Hypothetical test problem with
  "m" objectives and "n" decisions
  """
  def __init__(self, m, n=None):
    """
    Initialize DTLZ7 instance
    :param m: Number of objectives
    :param n: Number of decisions
    """
    Problem.__init__(self)
    self.name = DTLZ7.__name__
    if n is None:
      n = DTLZ7.default_decision_count(m)
    self.decisions = [Decision("x"+str(index+1),0,1) for index in range(n)]
    self.objectives = [Objective("f"+str(index+1), True, 0, 1000) for index in range(m)]
    self.constraints = [Constraint("g"+str(index+1)) for index in range(m)]

  @staticmethod
  def default_decision_count(m):
    return m * 10

  def evaluate(self, decisions):
    m = len(self.objectives)
    n = len(decisions)
    multiplier = 1/floor(n/m)
    f = []
    for j in range(m):
      start = max(floor(j*n/m),0)
      end = min(floor((j+1)*n/m),n-1)
      f_j = 0
      for i in range(start, end):
        f_j += decisions[i]
      f_j *= multiplier
      f.append(f_j)
    return f

  def evaluate_constraints(self, one):
    f = self.evaluate(one)
    m = len(f)
    status = True
    offset = 0
    for i in range(len(f)-1):
      g_i = f[-1] + 4*f[i] - 1
      if g_i < 0:
        status = False
        offset += abs(g_i)
    min_val = sys.maxint
    for i in range(m-1):
      for j in range(i+1, m-1):
        if i == j: continue
        sum_val = f[i] + f[j]
        if sum_val < min_val: min_val = sum_val
    g_m  = 2*f[-1] + min_val - 1
    if g_m < 0:
      status = False
      offset += abs(g_m)
    return status, offset

