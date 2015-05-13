from __future__ import print_function, division
from problem import *
from math import sqrt

"""
No of Decisions = n = 30.
Range of each imput = [0,1]
Objectives:
  f1(x) = x1
  f2(x) = g(x)(1 - (x1/g(x))**0.5 )
  where g(x) = 1 + 9*(sum_(i = 2 to n) x_i)/ n-1
"""
class ZDT1(Problem):
  def __init__(i):
    i.name = "ZDT1"
    i.desc = "No of Decisions = n = 30. \n \
              Range of each input = [0,1] \n \
              Objectives: \n \
              f1(x) = x1 \n \
              f2(x) = g(x)(1 - (x1/g(x))**0.5 ) \n \
              where g(x) = 1 + 9*(sum_(i = 2 to n) x_i)/ n-1"
    i.decisions = [Decision("x"+str(index+1),0,1) for index in range(30)]
    i.objectives = [Objective("f1", True, 0, 1), Objective("f2", True, 0, 1)]
    i.evals = 0
    i.ideal_decisions = None
    i.ideal_objectives = None

  def evaluate(i, decisions = None):
    if decisions:
      for index, decision in enumerate(i.decisions):
        decision.value = decisions[index]
    decisions = [decision.value for decision in i.decisions]
    g  = 1 + 9 * sum(decisions[1:]) / (len(decisions)-1)
    i.objectives[0].value = decisions[0]
    i.objectives[1].value = g * (1 - sqrt(decisions[0]/g))
    return [i.objectives[0].value, i.objectives[1].value]

  def get_ideal_decisions(self, count = 500):
    if self.ideal_decisions is not None and len(self.ideal_decisions) == count:
      return self.ideal_decisions
    start = 1/(2*500)
    delta = 1/500
    self.ideal_decisions = []
    for i in range(count):
      self.ideal_decisions.append([start + i*delta]+[0]*29)
    return self.ideal_decisions

  def get_ideal_objectives(self):
    if self.ideal_objectives is not None:
      return self.ideal_objectives
    ideal_decisions = self.get_ideal_decisions()
    self.ideal_objectives = []
    for decision in ideal_decisions:
      self.ideal_objectives.append(self.evaluate(decision))
    return self.ideal_objectives

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


if __name__ == "__main__":
  import nsga2.NSGA2 as optimizer
  import random
  random.seed(1)
  o = ZDT1()
  o.populate(optimizer.settings().pop_size)
  nsga2 = optimizer.NSGA2(o)
  goods, fronts = nsga2.generate()
  print(nsga2.convergence(goods))
  print(nsga2.diversity(fronts[0]))
  # print(goods[0].decisions)
  # print(o.norm(goods[0].decisions))
  # print(goods[1].decisions)
  # print(o.norm(goods[1].decisions))
  # print(o.dist(goods[0].decisions, goods[1].decisions))
  #for good in goods:
  #  print(good.decisions)
  #print(len(nsga2.make_kids(nsga2.problem.population)))
  #fronts = nsga2.fast_non_dom_sort()
  # for front in fronts:
  #   print(len(front))
  #frontier = nsga2.assign_crowd_dist(fronts[0])
  #for point in frontier:
  #  print(point.crowd_dist)
  #bro,sis = nsga2.sbx_crossover(fronts[0][0].decisions, fronts[0][1].decisions)
  #print(nsga2.poly_mutate(bro))