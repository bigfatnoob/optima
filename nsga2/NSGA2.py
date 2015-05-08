import sys
import os
sys.path.append(os.path.abspath("."))
from utils.lib import *
from problems.zdt1 import ZDT1

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
  def __init__(i, decisions):
    i.decisions = decisions
    i.rank = 0
    i.dominated = []
    i.dominating = 0



class NSGA2(O):
  def __init__(i, problem):
    i.problem = problem
    i.frontiers = []

  """
  Fast Non Dominated Sort
  :param - Population to sort
  :return - List of Frontiers
  """
  def fndSort(i, population = None):
    frontiers = []
    front1 = []
    if population == None:
      population = i.problem.population
    points = [Point(one) for one in population]
    for one, rest in loo(points):
      for two in rest:
        if i.problem.dominates(one.decisions, two.decisions):
          one.dominated.append(two)
        elif i.problem.dominates(two.decisions, one.decisions):
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

random.seed(2)
o = ZDT1()
o.populate(50)
nsga2 = NSGA2(o)
fronts = nsga2.fndSort()
for front in fronts:
  print(len(front))