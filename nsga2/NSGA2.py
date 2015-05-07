import sys
import os
sys.path.append(os.path.abspath("."))
from utils.lib import *

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
    i.dominated = []
    i.dominating = 0

class NSGA2(O):
  def __init__(i, problem):
    i.problem = problem
    i.frontiers = []

  def fndSort(i):
    for one, rest in loo(i.problem.population):
      onePoint =  Point(one)
      for two in rest:
        pass
        # TODO

