from __future__ import print_function, division
import sys, os
sys.path.append(os.path.abspath("."))
from problem import *
from math import sqrt
import numpy as np

class ZDT1(Problem):
  """
  No of Decisions = n = 30.
  Range of each input = [0,1]
  Objectives:
    f1(x) = x1
    f2(x) = g(x)(1 - (x1/g(x))**0.5 )
    where g(x) = 1 + 9*(sum_(i = 2 to n) x_i)/ n-1
  """
  def __init__(self):
    Problem.__init__(self)
    self.name = "ZDT1"
    self.desc = "No of Decisions = n = 30. \n \
              Range of each input = [0,1] \n \
              Objectives: \n \
              f1(x) = x1 \n \
              f2(x) = g(x)(1 - (x1/g(x))**0.5 ) \n \
              where g(x) = 1 + 9*(sum_(i = 2 to n) x_i)/ n-1"
    self.decisions = [Decision("x"+str(index+1),0,1) for index in range(30)]
    self.objectives = [Objective("f1", True, 0, 1), Objective("f2", True, 0, 1)]
    self.evals = 0
    self.ideal_decisions = None
    self.ideal_objectives = None

  def evaluate(self, decisions):
    g  = 1 + 9 * sum(decisions[1:]) / (len(decisions)-1)
    self.objectives[0].value = decisions[0]
    self.objectives[1].value = g * (1 - sqrt(decisions[0]/g))
    return [self.objectives[0].value, self.objectives[1].value]

  def get_ideal_decisions(self, count = 500):
    if self.ideal_decisions is not None and len(self.ideal_decisions) == count:
      return self.ideal_decisions
    start = 1/(2*500)
    delta = 1/500
    self.ideal_decisions = []
    for i in range(count):
      self.ideal_decisions.append([start + i*delta]+[0]*29)
    return self.ideal_decisions

  def get_ideal_objectives(self, count=500):
    if self.ideal_objectives is not None:
      return self.ideal_objectives
    # one_start = 1/(2*500)
    # two_start = 1- (1/(2*500))
    # delta = 1/500
    self.ideal_objectives = []
    ideal_decisions = self.get_ideal_decisions(count)
    for ideal_decision in ideal_decisions:
      self.ideal_objectives.append(self.evaluate(ideal_decision))
    return self.ideal_objectives


def _run_once():
  import nsga2.nsga2 as optimizer
  import random
  algo = optimizer.NSGA2
  random.seed(0)
  o = ZDT1()
  opt = algo(o, gens=250)
  goods = opt.run()
  print(opt.convergence(goods))
  print(opt.diversity(goods))
  opt.solution_range(goods)
  o.plot(goods, file_path="figures/"+opt.name+".png")

def _run_many():
  import nsga2.nsga2 as optimizer
  import random
  random.seed(1)
  gammas,deltas = [], []
  for _ in range(20):
    o = ZDT1()
    opt = optimizer.NSGA2(o, gens=100)
    goods = opt.run()
    gammas.append(opt.convergence(goods))
    deltas.append(opt.diversity(goods))
  print(np.mean(gammas), np.var(gammas))
  print(np.mean(deltas), np.var(deltas))

if __name__ == "__main__":
  _run_once()
