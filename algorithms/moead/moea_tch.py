from __future__ import print_function, division
import sys, os
sys.path.append(os.path.abspath("."))
from  moea_d import MOEA_D


class MOEA_TCH(MOEA_D):
  """
  Subclass of MOEA_D that implements the
  normalized tchebychev method.
  """
  def __init__(self, problem, population=None, **settings):
    MOEA_D.__init__(self, problem, population, **settings)
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
      dist = max(dist, weights[i]*abs((objectives[i]-ideal[i])/(nadir[i]-ideal[i])))
    assert dist >= 0, "Distance can't be less than 0"
    return dist


if __name__ == "__main__":
  from problems.dtlz.dtlz1 import DTLZ1
  o = DTLZ1(3)
  moead = MOEA_TCH(o)
  moead.run()