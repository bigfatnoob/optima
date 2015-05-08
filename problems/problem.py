import sys
import os
sys.path.append(os.path.abspath("."))
from utils.lib import *


"""
:return
  -1 indicates worse
  0 indicates equal
  1 indicates better
"""
def compare(one, two, minimize=True):
  if one == two:
    return 0
  if minimize:
    status = 1 if one < two else -1
  else:
    status = 1 if one > two else -1
  return status

class Decision(O):
  def __init__(i, name, low, high):
    i.name = name
    i.low = low
    i.high = high

  def norm(i, val):
    return norm(val, i.low, i.high)

  def deNorm(i, val):
    return deNorm(val, i.low, i.high)


class Objective(O):
  def __init__(i, name, toMinimize=True, low=None, high=None):
    i.name = name
    i.toMinimize = toMinimize
    i.low = low
    i.high = high
    i.value = None


class Problem(O):
  def __init__(i):
    i.name = ""
    i.desc = ""
    i.decisions = []
    i.objectives = []
    i.evals = 0
    i.population = []

  def generate(i):
    return [uniform(d.low, d.high) for d in i.decisions]

  def assign(i, decisions):
    for index, d in enumerate(i.decisions):
      d.value = decisions[index]

  def populate(i, n):
    i.population = []
    for _ in range(n):
      i.population.append(i.generate())
    return i.population

  def evaluate(i, decisions=None):
    pass

  """
  Domination is defined as follows:
  for all objectives a in "one" and
  all objectives b in "two"
  every a <= b

  for all objectives a in "one" and
  all objectives b in "two"
  at least one a < b

  Check if one set of decisions ("one")
  dominates other set of decisions ("two")
  """
  def dominates(i, one, two):
    obj1 = i.evaluate(one)
    obj2 = i.evaluate(two)
    atLeastOnce = False
    for index, (a, b) in enumerate(zip(obj1, obj2)):
      status = compare(a, b, i.objectives[index].toMinimize)
      if status == -1:
        return False
      elif status == 1:
        atLeastOnce = True
    return atLeastOnce


