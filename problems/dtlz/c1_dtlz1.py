from __future__ import print_function, division
import sys, os
sys.path.append(os.path.abspath("."))
from dtlz1 import DTLZ1

__author__ = 'george'

class C1_DTLZ1(DTLZ1):
  """
  Constrainted version of DTLZ1
  """
  k = 5
  def __init__(self, m ,n = None):
    DTLZ1.__init__(self, m, n)
    self.name = "C1-DTLZ1"

  def check_constraints(self, decisions):
    f = self.evaluate(decisions)
    c = 1 - (f[-1]/0.6) - sum(f[0:-1])/0.5
    return c>=0

  def evaluate_constraints(self, decisions):
    f = self.evaluate(decisions)
    c = 1 - (f[-1]/0.6) - sum(f[0:-1])/0.5
    if c >= 0:
      return True, 0
    else:
      return False, abs(c)