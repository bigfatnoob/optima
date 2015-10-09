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
    def g():
      val = 0
      for index in range(len(decisions) - DTLZ1.k, len(decisions)):
        d = decisions[index]
        val += ((d-0.5)**2) - (cos(20*PI*(d-0.5)))
      val = 1 * (DTLZ1.k + val)
      # TODO above line is a hack
      #val = 100 * (DTLZ1.k + val)
      return val

    f = [0.5 * (1 + g())]*m
    for i in range(m):
      for j in range(m-(i+1)):
        f[i] *= decisions[j]
      if i!=0:
        f[i] *= (1-decisions[m-(i+1)])
    return f

def _run_once():
  import nsga2.nsga2 as optimizer
  import random
  algo = optimizer.NSGA2
  random.seed(0)
  o = DTLZ1(2)
  o.populate(optimizer.settings().pop_size)
  opt = algo(o, gens=100)
  goods = opt.run()
  objs = [good.objectives for good in goods]
  opt.solution_range(goods)
  o.plot(goods)

if __name__ == "__main__":
  _run_once()