from __future__ import print_function, division
import sys, os
sys.path.append(os.path.abspath("."))
from dtlz3 import DTLZ3

__author__ = 'george'

class C1_DTLZ3(DTLZ3):
  """
  Constrainted version of DTLZ1
  """
  k = 5
  def __init__(self, m ,n = None):
    DTLZ3.__init__(self, m, n)
    self.name = "C1-DTLZ3"

  def check_constraints(self, decisions):
    f = self.evaluate(decisions)
    r = self.get_r()
    sum_f = sum([f_i**2 for f_i in f])
    c = (sum_f - 16) * (sum_f - r**2)
    return c>=0

  def evaluate_constraints(self, decisions):
    f = self.evaluate(decisions)
    r = self.get_r()
    sum_f = sum([f_i**2 for f_i in f])
    c = (sum_f - 16) * (sum_f - r**2)
    if c >= 0:
      return True, 0
    else:
      return False, abs(c)

  def get_r(self):
    m = len(self.objectives)
    if m == 3:
      return 9
    elif m == 3 or m == 8:
      return 12.5
    elif m == 10 or m == 15:
      return 15