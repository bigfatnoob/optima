"""
Let A and B be two approximations to the PF of a MOP, C(A,B)
is defined as the percentage of the solutions in B
that are dominated by at least one solution in  A
"""
from __future__ import print_function,division
import sys, os
sys.path.append(os.path.abspath("."))

__author__ = 'panzer'

def coverage(problem, one, two):
  """
  Method to compute coverage percentage of 'one' in 'two'
  :param problem: Instance of the problem.
  :param one: Set of objectives to check for
  :param two: Set of objectives to check against
  :return: Coverage value between 0 and 100.
  """
  c = 0
  for o_i in one:
    for t_i in two:
      if problem.binary_dominates(o_i, t_i) == 1:
        c += 1
        break
  assert c<=len(two), "Something went wrong.  c has to be less than two"
  return c*100/len(two)
