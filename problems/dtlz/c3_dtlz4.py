from __future__ import print_function, division
import sys, os
sys.path.append(os.path.abspath("."))
from problems.problem import Constraint
from dtlz4 import DTLZ4

__author__ = 'george'

class C3_DTLZ4(DTLZ4):
  """
  Constrained(C3) version of DTLZ4
  """
  k = 5
  def __init__(self, m ,n = None):
    DTLZ4.__init__(self, m, n)
    self.name = "C3-DTLZ4"
    self.constraints = [Constraint("C"+str(i + 1)) for i in range(m)]

  def check_constraints(self, decisions):
    f = self.evaluate(decisions)
    f_squared = sum([f_i for f_i in f])
    for f_i in f:
      c_i = f_squared/4 + f_squared - f_i**2 - 1
      if c_i < 0:
        return False
    return True

  def evaluate_constraints(self, decisions):
    f = self.evaluate(decisions)
    f_squared = sum([f_i for f_i in f])
    c = 0
    for f_i in f:
      c_i = f_squared/4 + f_squared - f_i**2 - 1
      if c_i < 0:
        c += abs(c_i)
    return c==0, c