from __future__ import division, print_function, absolute_import
from ..utils import lib

"""
Default class which everything extends.
"""
class O:
  def __init__(i,**d): i.has().update(**d)
  def has(i): return i.__dict__
  def update(i,**d) : i.has().update(d); return i
  def __repr__(i)   :
    show=[':%s %s' % (k,i.has()[k])
      for k in sorted(i.has().keys() )
      if k[0] is not "#"]
    txt = ' '.join(show)
    if len(txt) > 60:
      show=map(lambda x: '\t'+x+'\n',show)
    return '{'+' '.join(show)+'}'
  def __getitem__(i, item):
    return i.has().get(item)

class Decision(O):
  def __init__(i, name, low, high):
    i.name = name
    i.low = low
    i.high = high

  def norm(i, val):
    return lib.norm(val, i.low, i.high)

  def deNorm(i, val):
    return lib.deNorm(val, i.low, i.high)


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
