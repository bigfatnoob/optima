from __future__ import print_function, division
import sys, os
sys.path.append(os.path.abspath("."))
from  moea_d import MOEA_D
from configs import moead_tch_settings

class MOEA_TCH(MOEA_D):
  """
  Subclass of MOEA_D that implements the
  normalized tchebyshev method.
  """
  def __init__(self, problem, population=None, **settings):
    MOEA_D.__init__(self, problem, population)
    self.settings = moead_tch_settings().update(**settings)
    self.name = "MOEA__TCH"

  def update_neighbors(self, point, mutant, ideal, population):
    for neighbor_id in point.neighbor_ids:
      neighbor = population[neighbor_id]
      nadir = self.get_nadir_point(population)
      neighbor_distance = self.normalized_tch_distance(neighbor.objectives, neighbor.weight, ideal, nadir)
      mutant_distance = self.normalized_tch_distance(mutant.objectives, neighbor.weight, ideal, nadir)
      if mutant_distance < neighbor_distance:
        population[neighbor_id].decisions = mutant.decisions
        population[neighbor_id].objectives = mutant.objectives

  def normalized_tch_distance(self, objectives, weights, ideal, nadir):
    dist =  -sys.maxint
    for i in range(len(self.problem.objectives)):
      if ideal[i] == nadir[i]:
        return sys.maxint
      normalized = abs((objectives[i]-ideal[i])/(nadir[i]-ideal[i]))
      if weights[i] == 0:
        normalized *= 0.00001
      else:
        normalized *= weights[i]
      dist = max(dist, weights[i]*normalized)
    assert dist >= 0, "Distance can't be less than 0"
    return dist


if __name__ == "__main__":
  from problems.dtlz.dtlz1 import DTLZ1
  o = DTLZ1(15)
  moead = MOEA_TCH(o, pop_size=135, gens = 1500)
  moead.run()