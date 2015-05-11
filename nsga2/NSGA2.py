import sys
import os
sys.path.append(os.path.abspath("."))
from utils.lib import *
from problems.ZDT1 import ZDT1

def settings():
  return O(
    pop_size = 100,
    max_iter = 250
  )

def loo(points):
  for i in range(len(points)):
    one = points[i]
    rest = points[:i] + points[i+1:]
    yield one, rest


class Point(O):
  def __init__(self, decisions, problem):
    self.decisions = decisions
    self.rank = 0
    self.dominated = []
    self.dominating = 0
    self.objectives = problem.evaluate(decisions)
    self.crowd_dist = 0




class NSGA2(O):
  def __init__(self, problem):
    self.problem = problem
    self.frontiers = []

  """
  Fast Non Dominated Sort
  :param - Population to sort
  :return - List of Frontiers
  """
  def fast_non_dom_sort(self, population = None):
    frontiers = []
    front1 = []
    if population is None:
      population = self.problem.population
    points = [Point(one, self.problem) for one in population]
    for one, rest in loo(points):
      for two in rest:
        if self.problem.dominates(one, two):
          one.dominated.append(two)
        elif self.problem.dominates(two, one):
          one.dominating += 1
      if one.dominating == 0:
        one.rank = 1
        front1.append(one)

    current_rank = 1
    while True:
      front2 = []
      for one in front1:
        for two in one.dominated:
          two.dominating -= 1
          if two.dominating == 0:
            two.rank =  current_rank + 1
            front2.append(two)
      current_rank += 1
      if len(front2) == 0 :
        break
      else :
        frontiers.append(front2)
        front1 = front2
    return frontiers

  def assign_crowd_dist(self, frontier):
    l = len(frontier)
    for m in range(len(self.problem.objectives)):
      frontier = sorted(frontier, key=lambda x:x.objectives[m])
      obj_min = frontier[0].objectives[m]
      obj_max = frontier[-1].objectives[m]
      frontier[0].crowd_dist = float("inf")
      frontier[-1].crowd_dist = float("inf")
      for i in range(1,len(frontier)-1):
        frontier[i].crowd_dist += (frontier[i+1].objectives[m] - frontier[i-1].objectives[m])/(obj_max - obj_min)




random.seed(2)
o = ZDT1()
o.populate(50)
nsga2 = NSGA2(o)
fronts = nsga2.fast_non_dom_sort()
# for front in fronts:
#   print(len(front))
nsga2.assign_crowd_dist(fronts[0])