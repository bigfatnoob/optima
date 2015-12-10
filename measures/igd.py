"""
Compute the inverse generational
distance for a set of solutions
"""
from __future__ import print_function,division
import sys, os
sys.path.append(os.path.abspath("."))
from utils.distances import eucledian

__author__ = 'panzer'

def igd(obtained, ideals):
  """
  Compute the IGD for a
  set of solutions
  :param obtained: Obtained pareto front
  :param ideals: Ideal pareto front
  :return:
  """
  igd_val = 0
  for d in ideals:
    min_dist = sys.maxint
    for o in obtained:
      min_dist = min(min_dist, eucledian(o, d))
    igd_val += min_dist
  return igd_val/len(ideals)