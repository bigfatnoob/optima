import sys
import os
sys.path.append(os.path.abspath("."))
from utils.lib import *


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
