from __future__ import division, print_function
from constants import EPS
import random

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


