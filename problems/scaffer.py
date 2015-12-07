from __future__ import print_function, division
import sys, os
sys.path.append(os.path.abspath("."))
from problem import *

__author__ = 'george'

class Schaffer(Problem):
  def __init__(self):
    Problem.__init__(self)
    self.name = "Schaffer"
    self.desc = """
        No of Decisions = n = 1
        Range of each input = [-10^5 , 10^5]
        Objectives:
          f1(x) = x^2
          f2(x) = (x-2)^2
    """
    extreme = 10**2
    self.decisions = [Decision("x"+str(index+1), -extreme, extreme) for index in range(1)]
    self.objectives = [Objective("f1", True, 0, extreme**2), Objective("f2", True, 0, (-extreme - 2)**2)]
    self.evals = 0
    self.ideal_decisions = None
    self.ideal_objectives = None

  def evaluate(self, decisions):
    self.objectives[0].value = decisions[0] ** 2
    self.objectives[1].value = (decisions[0] - 2) ** 2
    return [self.objectives[0].value, self.objectives[1].value]

def _run_once():
  #import algorithms.gale.gale as optimizer
  import algorithms.nsga2.nsga2 as optimizer
  import random
  random.seed(1)
  o = Schaffer()
  #nsga2 = optimizer.GALE(o, 100)
  nsga2 = optimizer.NSGA2(o, 100)
  goods = nsga2.run()
  nsga2.solution_range(goods)
  o.plot(goods, file_path="figures/"+o.name+".png")

if __name__ == "__main__":
  _run_once()