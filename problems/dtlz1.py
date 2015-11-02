from __future__ import print_function, division
import sys, os
sys.path.append(os.path.abspath("."))
from problem import *

__author__ = 'george'

class DTLZ1(Problem):
  """
  Hypothetical test problem with
  "m" objectives and "n" decisions
  """
  k = 5
  def __init__(self, m, n = None):
    Problem.__init__(self)
    self.name = DTLZ1.__name__
    if n is None:
      n = DTLZ1.default_decision_count(m)
    self.decisions = [Decision("x"+str(index+1),0,1) for index in range(n)]
    self.objectives = [Objective("f"+str(index+1), True) for index in range(m)]

  @staticmethod
  def default_decision_count(m):
    return m + DTLZ1.k - 1

  def evaluate(self, decisions):
    m = len(self.objectives)
    n = len(decisions)
    k = n - m + 1
    g = 0
    for i in range(n - k, n):
      g += ((decisions[i] - 0.5)**2 - cos(20.0 * PI * (decisions[i] - 0.5)))
    g = 100 * (k + g)
    f = []
    for i in range(0, m): f.append((1.0 + g)*0.5)
    for i in xrange(m):
      for j in range(0, m-(i+1)): f[i] *= decisions[j]
      if not (i==0):
        aux = m - (i+1)
        f[i] *= 1 - decisions[aux]
    return f

def _run_once():
  #import nsga2.nsga2 as optimizer
  import nsga3.nsga3 as optimizer
  import random
  algo = optimizer.NSGA3
  random.seed(0)
  o = DTLZ1(8)
  opt = algo(o, pop_size=156, gens=750)
  goods = opt.run()
  opt.solution_range(goods)
  o.plot(goods, file_path="figures/"+opt.name+"_"+o.name+".png");

if __name__ == "__main__":
  _run_once()