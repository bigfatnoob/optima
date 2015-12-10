from __future__ import print_function,division
import sys, os
sys.path.append(os.path.abspath("."))
__author__ = 'panzer'

def eucledian(one, two):
  """
  Compute Eucledian Distance between
  2 vectors. We assume the input vectors
  are normalized.
  :param one: Vector 1
  :param two: Vector 2
  :return:
  """
  dist = 0
  for o_i, t_i in zip(one, two):
    dist += (o_i - t_i)**2
  return dist**0.5

def manhattan(one, two):
  """
  Compute Manhattan Distance between
  2 vectors. We assume the input vectors
  are normalized.
  :param one: Vector 1
  :param two: Vector 2
  :return:
  """
  dist = 0
  for o_i, t_i in zip(one, two):
    dist += abs(o_i - t_i)
  return dist
