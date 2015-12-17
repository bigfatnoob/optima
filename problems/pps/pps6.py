from __future__ import print_function, division
import sys, os
sys.path.append(os.path.abspath("."))
from problems.problem import *

__author__ = 'panzer'

class PPS6(Problem):
  """
  n decisions and 3 objectives
  """
  def __init__(self, n=10):
    """
    Initialize the problem
    :param n: Number of decisions
    :return:
    """
    Problem.__init__(self)
    self.name = PPS6.__name__
    self.decisions = [Decision("x1",0,1), Decision("x2",0,1)] + [Decision("x"+str(index+1),-2,2) for index in xrange(2, n)]
    self.objectives = [Objective("f"+str(i+1), True, 0, 1000) for i in xrange(3)]

  def evaluate(self, decisions):
    n = len(decisions)
    x = decisions
    j1_values = []
    j2_values = []
    j3_values = []
    for j in xrange(1, n):
      val = (x[j] - 2*x[1]*sin(2*PI*x[0] + (j+1)*PI/n))**2
      if (j+1) % 3 == 0:
        j3_values.append(val)
      elif (j-1) % 3 == 0:
        j2_values.append(val)
      elif j % 3 == 0:
        j1_values.append(val)
    f1 = cos(0.5*PI*x[0]) * cos(0.5*PI*x[1]) + (2/len(j1_values)) * sum(j1_values)
    f2 = cos(0.5*PI*x[0]) * sin(0.5*PI*x[1]) + (2/len(j2_values)) * sum(j2_values)
    f3 = sin(0.5*PI*x[0]) + (2/len(j3_values)) * sum(j3_values)
    return [f1, f2, f3]



  def get_pareto_front(self):
    file_name = "problems/pps/PF/pps6.txt"
    pf = []
    with open(file_name) as f:
      for line in f.readlines():
        pf.append(map(float,line.strip().replace("\n","").split("  ")))
    return pf

if __name__ == "__main__":
  pps = PPS6()
  pf_pps = pps.get_pareto_front()
  for _ in range(10000):
    print(pps.evaluate(pps.generate()))
  # for one in pf_pps:
  #   print(one)