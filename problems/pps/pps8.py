from __future__ import print_function, division
import sys, os
sys.path.append(os.path.abspath("."))
from problems.problem import *
from operator import mul

__author__ = 'panzer'

class PPS8(Problem):
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
    self.name = PPS8.__name__
    self.decisions = [Decision("x"+str(index+1), 0, 1) for index in xrange(0, n)]
    self.objectives = [Objective("f1", True, 0, 1000), Objective("f2", True, 0, 1000)]

  def evaluate(self, decisions):
    n = len(decisions)
    x = decisions
    j1_values = []
    j2_values = []
    y_j1_values = []
    y_j2_values = []
    for j in xrange(1, n):
      y_j = x[j] - x[0]**(0.5*(1 + 3*(j-1)/n-2))
      val = cos(20*y_j*PI/((j+1)**0.5))
      if is_even(j+1):
        y_j2_values.append(y_j**2)
        j2_values.append(val)
      else:
        y_j1_values.append(y_j**2)
        j1_values.append(val)
    f1 = x[0] + (2/len(j1_values)) * (4*sum(y_j1_values) - 2*reduce(mul,j1_values,1) + 2)
    f2 = 1 - x[0]**0.5 + (2/len(j2_values)) * (4*sum(y_j2_values) - 2*reduce(mul,j2_values,1) + 2)
    return [f1, f2]

  def get_pareto_front(self):
    file_name = "problems/pps/PF/pps8.txt"
    pf = []
    with open(file_name) as f:
      for line in f.readlines():
        pf.append(map(float,line.strip().replace("\n","").split("  ")))
    return pf

if __name__ == "__main__":
  pps = PPS8()
  pf_pps = pps.get_pareto_front()
  # for _ in range(100000):
  #   print(pps.evaluate(pps.generate()))
  for one in pf_pps:
    print(one)