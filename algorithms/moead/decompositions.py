from __future__ import print_function, division
import sys, os
sys.path.append(os.path.abspath("."))

__author__ = 'panzer'

def get_distance(distance_name):
  if distance_name == "tch":
    return weighted_tch
  elif distance_name == "pbi":
    return pbi
  assert False, "Invalid distance type : %s"%distance_name

"""
Distance Measures
"""
def pbi(moead, objectives, weights):
  """
  Penalty Boundary Intersection distance
  :param moead - Instance of MOEAD.
  :param objectives - Objectives of the point.
  :param weights - Weight of the points.
  """
  d1_vector = [abs(i-f) for i, f in zip(objectives, moead.ideal)]
  weights_norm = vector_norm(weights)
  d1 = dot_product(d1_vector, weights)/weights_norm
  d2_vector = []
  for i, obj in enumerate(moead.problem.objectives):
    if obj.to_minimize:
      d2_vector.append(objectives[i] - (moead.ideal[i]+d1*weights[i]))
    else:
      d2_vector.append(objectives[i] - (moead.ideal[i]-d1*weights[i]))
  d2 = vector_norm(d2_vector)
  return d1 + moead.settings.penalty * d2


def weighted_tch(moead, objectives, weights):
  """
  Tchebyshev distance
  :param moead - Instance of MOEAD.
  :param objectives - Objectives of the point.
  :param weights - Weight of the points.
  """
  mins = [sys.maxint] * len(moead.problem.objectives)
  maxs = [-sys.maxint] * len(moead.problem.objectives)
  for i in xrange(len(moead.problem.objectives)):
    for j in xrange(len(moead.problem.objectives)):
      val = moead.best_boundary_objectives[j][j]
      if val > maxs[i]: maxs[i] = val
      if val < mins[i]: mins[i] = val
    if maxs[i] == mins[i]:
      #print("min value and max value are the same")
      return sys.maxint
  dist = -sys.maxint
  for i in xrange(len(moead.problem.objectives)):
    normalized = abs((objectives[i]-moead.ideal[i])/(maxs[i]-mins[i]))
    if weights[i] == 0:
      normalized *= 0.0001
    else:
      normalized *= weights[i]
    dist = max(dist, normalized)
  assert dist >= 0, "Distance can't be less than 0"
  return dist


"""
Utility Methods
"""
def vector_norm(vector):
  """
  Get the  norm of the vector
  :param vector: Vector to be normalized
  :return:
  """
  return sum([v**2 for v in vector])**0.5

def dot_product(one, two):
  """
  Dot Product between one and two
  :param one: Vector one
  :param two: Vector two
  :return:
  """
  assert len(one) == len(two), "Vectors are not of equal length"
  return sum([o_i*t_i for o_i, t_i in zip(one, two)])