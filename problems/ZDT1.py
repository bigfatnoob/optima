from __future__ import print_function, division
from problem import *
from math import sqrt
import numpy as np

"""
No of Decisions = n = 30.
Range of each imput = [0,1]
Objectives:
  f1(x) = x1
  f2(x) = g(x)(1 - (x1/g(x))**0.5 )
  where g(x) = 1 + 9*(sum_(i = 2 to n) x_i)/ n-1
"""
class ZDT1(Problem):
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

  def evaluate(self, decisions = None):
    if decisions:
      for index, decision in enumerate(self.decisions):
        decision.value = decisions[index]
    decisions = [decision.value for decision in self.decisions]
    g  = 1 + 9 * sum(decisions[1:]) / (len(decisions)-1)
    self.objectives[0].value = decisions[0]
    self.objectives[1].value = g * (1 - sqrt(decisions[0]/g))
    return [self.objectives[0].value, self.objectives[1].value]

  def norm(self, one):
    normalized = []
    for i, dec in enumerate(one):
      normalized.append(self.objectives[i].norm(dec))
    return normalized

  def dist(self, one, two):
    one_norm = self.norm(one)
    two_norm = self.norm(two)
    delta = 0
    count = 0
    for i,j in zip(one_norm, two_norm):
      delta += (i-j) ** 2
      count += 1
    return (delta/count) ** 0.5

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
  import nsga2.NSGA2 as optimizer
  import random
  random.seed(1)
  o = ZDT1()
  o.populate(optimizer.settings().pop_size)
  nsga2 = optimizer.NSGA2(o)
  goods, fronts = nsga2.generate()
  print(nsga2.convergence(goods))
  print(nsga2.diversity(fronts[0]))
  nsga2.solution_range(goods)
  print(goods[0])
  o.plot(goods)

def _run_many():
  import nsga2.NSGA2 as optimizer
  import random
  random.seed(1)
  gammas,deltas = [], []
  for _ in range(1):
    o = ZDT1()
    o.populate(optimizer.settings().pop_size)
    nsga2 = optimizer.NSGA2(o)
    goods, fronts = nsga2.generate()
    gammas.append(nsga2.convergence(goods))
    deltas.append(nsga2.diversity(fronts[0]))
  print(np.mean(gammas), np.var(gammas))
  print(np.mean(deltas), np.var(deltas))

if __name__ == "__main__":
  _run_once()
