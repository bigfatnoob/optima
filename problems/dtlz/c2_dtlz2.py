from __future__ import print_function, division
import sys, os
sys.path.append(os.path.abspath("."))
from dtlz2 import DTLZ2

__author__ = 'george'

class C2_DTLZ2(DTLZ2):
  """
  Constrainted version of DTLZ2
  """
  k = 5
  def __init__(self, m ,n = None):
    DTLZ2.__init__(self, m, n)
    self.name = "C1-DTLZ2"

  def check_constraints(self, decisions):
    f = self.evaluate(decisions)
    m = len(self.objectives)
    r = self.get_r()
    rhs = sum([(f_i - 1/(m**0.5))**2 for f_i in f]) - r**2
    lhs = sys.maxint
    f_squared = sum([f_i**2 for f_i in f])
    for i in range(m):
      temp_lhs = (f[i] - 1)**2 + f_squared - (r**2) - (f[i]**2)
      lhs = min(lhs, temp_lhs)
    c = -min(lhs, rhs)
    return c>=0

  def evaluate_constraints(self, decisions):
    f = self.evaluate(decisions)
    m = len(self.objectives)
    r = self.get_r()
    rhs = sum([(f_i - 1/(m**0.5))**2 for f_i in f]) - r**2
    lhs = sys.maxint
    f_squared = sum([f_i**2 for f_i in f])
    for i in range(m):
      temp_lhs = (f[i] - 1)**2 + f_squared - (r**2) - (f[i]**2)
      lhs = min(lhs, temp_lhs)
    c = -min(lhs, rhs)
    if c >= 0:
      return True, 0
    else:
      return False, abs(c)

  def get_r(self):
    m = len(self.objectives)
    if m == 3:
      return 0.4
    else:
      return 0.5