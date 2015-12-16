from __future__ import print_function, division
import sys, os
sys.path.append(os.path.abspath("."))
from moea_d import MOEA_D
from configs import moead_pbi_settings

__author__ = 'panzer'

def vector_norm(vector):
  return sum([v**2 for v in vector])**0.5

def dot_product(one, two):
  assert len(one) == len(two), "Vectors are not of equal length"
  return sum([o_i*t_i for o_i, t_i in zip(one, two)])

class MOEA_PBI(MOEA_D):
  """
  Subclass of MOEA_D that implements the
  penalty boundary intersection method
  """
  def __init__(self, problem, population=None, **settings):
    MOEA_D.__init__(self, problem, population)
    self.settings = moead_pbi_settings().update(**settings)

  def distance(self, objectives, weights):
    d1_vector = [abs(i-f) for i, f in zip(objectives, self.ideal)]
    weights_norm = vector_norm(weights)
    #normalized_weights = [w/weights_norm for w in weights]
    d1 = dot_product(d1_vector, weights)/weights_norm
    d2_vector = []
    for i, obj in enumerate(self.problem.objectives):
      if obj.to_minimize:
        d2_vector.append(objectives[i] - (self.ideal[i]+d1*weights[i]))
      else:
        d2_vector.append(objectives[i] - (self.ideal[i]-d1*weights[i]))
    d2 = vector_norm(d2_vector)
    return d1 + self.settings.penalty * d2

  # def distance(self, objectives, weights):
  #   """
  #   This function is implemented as per
  #   the C++ code on MOEAD website
  #   :param objectives:
  #   :param weights:
  #   :return:
  #   """
  #   weights_norm = vector_norm(weights)
  #   normalized_weights = [w/weights_norm for w in weights]
  #   d1_vector = [(i-f) for i, f in zip(objectives, self.ideal)]
  #   d1 = abs(dot_product(d1_vector, normalized_weights))
  #   d2_vector = []
  #   for i, obj in enumerate(self.problem.objectives):
  #     if obj.to_minimize:
  #       d2_vector.append(objectives[i] - (self.ideal[i]+d1*weights[i]))
  #     else:
  #       d2_vector.append(objectives[i] - (self.ideal[i]-d1*weights[i]))
  #   d2 = vector_norm(d2_vector)
  #   return d1 + self.settings.penalty * d2

if __name__ == "__main__":
  from problems.dtlz.dtlz2 import DTLZ2
  o = DTLZ2(15)
  moead = MOEA_PBI(o, pop_size=135, gens = 1500)
  moead.run()