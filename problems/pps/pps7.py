from __future__ import print_function, division
import sys, os
sys.path.append(os.path.abspath("."))
from problems.problem import *

__author__ = 'panzer'

class PPS7(Problem):
  """
  n decisions and 2 objectives
  """
  def __init__(self, n=10):
    """
    Initialize the problem
    :param n: Number of decisions
    :return:
    """
    Problem.__init__(self)
    self.name = PPS7.__name__
    self.decisions = [Decision("x"+str(index+1), 0, 1) for index in xrange(0, n)]
    self.objectives = [Objective("f1", True, 0, 1000), Objective("f2", True, 0, 1000)]

  def evaluate(self, decisions):
    n = len(decisions)
    x = decisions
    j1_values = []
    j2_values = []
    for j in xrange(1, n):
      y_j = x[j] - x[0]**(0.5*(1 + 3*(j-1)/n-2))
      val = 4*(y_j**2) - cos(8*y_j*PI) + 1
      if is_even(j+1):
        j2_values.append(val)
      else:
        j1_values.append(val)
    f1 = x[0] + (2/len(j1_values)) * sum(j1_values)
    f2 = 1 - x[0]**0.5 + (2/len(j2_values)) * sum(j2_values)
    return [f1, f2]

  def get_pareto_front(self):
    file_name = "problems/pps/PF/pps7.txt"
    pf = []
    with open(file_name) as f:
      for line in f.readlines():
        pf.append(map(float,line.strip().replace("\n","").split("  ")))
    return pf

if __name__ == "__main__":
  pps = PPS7()
  pf_pps = pps.get_pareto_front()
  for _ in range(10000):
    print(pps.evaluate(pps.generate()))
  # for one in pf_pps:
  #   print(one)