from __future__ import print_function, division
import sys, os
sys.path.append(os.path.abspath("."))
from moea_d import MOEA_D
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

  def distance(self, objectives, weights):
    mins = [sys.maxint] * len(self.problem.objectives)
    maxs = [-sys.maxint] * len(self.problem.objectives)
    for i in xrange(len(self.problem.objectives)):
      for j in xrange(len(self.problem.objectives)):
        val = self.best_boundary_objectives[j][j]
        if val > maxs[i]: maxs[i] = val
        if val < mins[i]: mins[i] = val
      if maxs[i] == mins[i]:
        print("min value and max value are the same")
        return sys.maxint

    dist = -sys.maxint
    for i in xrange(len(self.problem.objectives)):
      normalized = abs((objectives[i]-self.ideal[i])/(maxs[i]-mins[i]))
      if weights[i] == 0:
        normalized *= 0.0001
      else:
        normalized *= weights[i]
      dist = max(dist, normalized)
    assert dist >= 0, "Distance can't be less than 0"
    return dist


if __name__ == "__main__":
  from problems.dtlz.dtlz1 import DTLZ1
  o = DTLZ1(10)
  moead = MOEA_TCH(o, pop_size=275, gens = 1000)
  moead.run()