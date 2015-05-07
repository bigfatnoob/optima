from __future__ import division, print_function
from constants import EPS
import random

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

"""
Method to normalize value
between 0 and 1
"""
def norm(x, low, high):
  nor = (x - low)/(high - low + EPS)
  if nor > 1:
    return 1
  elif nor < 0:
    return 0
  return nor

"""
Method to de-normalize value
between low and high
"""
def deNorm(x, low, high):
  deNor = x*(high-low) + low
  if deNor > high:
    return high
  elif deNor < low:
    return low
  return deNor


def uniform(low, high):
  return random.uniform(low, high)


