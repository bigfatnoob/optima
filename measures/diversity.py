from __future__ import print_function,division
import sys, os
sys.path.append(os.path.abspath("."))
from utils.distances import eucledian

__author__ = 'panzer'

def sort_solutions(solutions):
  """
  Sort a list of list before computing diversity
  """
  def sorter(lst):
    m = len(lst)
    weights = reversed([10 ** i for i in xrange(m)])
    return sum([element * weight for element, weight in zip(lst, weights)])
  return sorted(solutions, key=sorter)

def diversity(obtained, ideals):
  """
  Calculate the diversity (a.k.a spread)
  for a set of solutions
  """
  if ideals is None:
    return
  s_obtained = sort_solutions(obtained)
  s_ideals = sort_solutions(ideals)
  def closest(one, many):
    min_dist = sys.maxint
    closest_point = None
    for this in many:
      dist = eucledian(this, one)
      if dist < min_dist:
        min_dist = dist
        closest_point = this
    return min_dist, closest_point


  d_f = closest(s_ideals[0], s_obtained)[0]
  d_l = closest(s_ideals[-1], s_obtained)[0]
  distances = []
  for i in range(len(s_obtained)-1):
    distances.append(eucledian(s_obtained[i], s_obtained[i+1]))
  d_bar = sum(distances)/len(distances)
  d_sum = sum([abs(d_i - d_bar) for d_i in distances])
  delta = (d_f + d_l + d_sum) / (d_f + d_l + (len(s_obtained) - 1)*d_bar)
  return delta