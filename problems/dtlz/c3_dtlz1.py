from __future__ import print_function, division
import sys, os
sys.path.append(os.path.abspath("."))
from problems.problem import Constraint
from dtlz1 import DTLZ1

__author__ = 'george'

class C3_DTLZ1(DTLZ1):
  """
  Constrained(C3) version of DTLZ1
  """
  k = 5
  def __init__(self, m ,n = None):
    DTLZ1.__init__(self, m, n)
    self.name = "C3-DTLZ1"
    self.constraints = [Constraint("C"+str(i + 1)) for i in range(m)]

  def check_constraints(self, decisions):
    f = self.evaluate(decisions)
    f_sum = sum(f)
    for f_i in f:
      c_i = f_sum - f_i + (f_i/0.5) - 1
      if c_i < 0:
        return False
    return True

  def evaluate_constraints(self, decisions):
    f = self.evaluate(decisions)
    f_sum = sum(f)
    c = 0
    for f_i in f:
      c_i = f_sum - f_i + (f_i/0.5) - 1
      if c_i < 0:
        c += abs(c_i)
    return c==0, c