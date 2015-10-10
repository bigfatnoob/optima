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


def splits(dim, div, outer=True):
  if outer:
    start = 0.0
    end = 1.0
  else:
    start = 1/(2*dim)
    end = start + 0.5
  delta = (end - start) / div
  return [start] + [start + i*delta for i in range(1, div)] + [end]

def valid(coord, exact = False):
  if exact:
    return abs(sum(coord) - 1) < EPS
  else:
    return sum(coord) <= 1 + EPS

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


def reference(m, p, outer=True):
  """
  Create a set of reference points
  with m axes and p is the number of
  divisions along each axis
  :param m: Number of axis
  :param p: Number of divisions
  :return:
  """
  possible = splits(m, p, outer=outer)
  coords = [[pt] for pt in possible]
  for i in range(1, m):
    coords = expand(coords, possible)
  return [coord for coord in coords if valid(coord, exact=True)]

def cover(m, p_outer, p_inner=None):
  ref = reference(m, p_outer)
  if p_inner:
    ref += reference(m, p_inner, outer=False)
  return ref


if __name__ == "__main__":
  x = cover(8, 3, 2)
  print(len(x))