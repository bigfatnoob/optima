from __future__ import print_function, division
import sys, os
sys.path.append(os.path.abspath("."))
from utils.lib import *
__author__ = 'george'

class Coordinate(O):
  id = 0
  def __init__(self):
    O.__init__(self)
    self.id = ++Coordinate.id
    self.pts = []


def splits(divisions):
  delta = 1 / divisions
  return [i*delta for i in range(divisions)]+[1.0]

def initialize(p):
  return [[pt] for pt in splits(p)]

def valid(coord, exact = False):
  if exact:
    return abs(sum(coord) - 1) < EPS
  else:
    return sum(coord) <= 1

def expand(coords, possible):
  expanded  = []
  for coord in coords:
    for val in possible:
      new = coord + [val]
      if valid(new):
        expanded.append(new)
      else:
        break
  return expanded


def reference(m, p):
  """
  Create a set of reference points
  with m axes and p is the number of
  divisions along each axis
  :param m: Number of axis
  :param p: Number of divisions
  :return:
  """
  possible = splits(p)
  coords = [[pt] for pt in possible]
  for i in range(1, m):
    coords = expand(coords, possible)
  return [coord for coord in coords if valid(coord, exact=True)]


if __name__ == "__main__":
  print(reference(3,12))