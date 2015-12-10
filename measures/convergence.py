from __future__ import print_function,division
import sys, os
sys.path.append(os.path.abspath("."))
from utils.distances import eucledian

__author__ = 'panzer'

def convergence(obtained, ideals):
  """
  :param obtained - Obtained set of pareto solutions
  :param ideals - Ideal Pareto Frontier
  Calculate the convergence metric with
  respect to ideal solutions
  """
  if ideals is None:
    return None
  predicts = [o.objectives for o in obtained]
  gammas = []
  for predict in predicts:
    gammas.append(min([eucledian(predict, ideal) for ideal in ideals]))
  return sum(gammas)/len(gammas)

