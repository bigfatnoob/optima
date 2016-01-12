from __future__ import print_function, division
import sys, os
sys.path.append(os.path.abspath("."))
from nsga3 import NSGA3, NSGAPoint
import utils.tools as tools

__author__ = 'panzer'

class C_NSGA3(NSGA3):
  """
  A Constraint handled version of NSGA3.
  .. [Jain2014] Jain and Deb, "An Evolutionary Many-Objective Optimization
      Algorithm Using Reference-Point-Based Non-dominated Sorting Approach,
      Part II: Constraints and Extending to an Adaptive Approach"
  """
  def __init__(self, problem, population = None, **settings):
    NSGA3.__init__(self, problem, population = population, **settings)
    self.name = "C-NSGA3"

  def _select(self, population):
    """
    Selector Function
    :param population: Population
    :return : Population and its kids
    """
    kids = []
    clones = [one.clone() for one in population]
    for _ in range(len(clones)):
      mom = tools.binary_tournament_selection(self.problem, clones, 2, is_domination=True)
      dad = None
      while True:
        dad = tools.binary_tournament_selection(self.problem, clones, 2, is_domination=True)
        if not mom == dad: break
      sis, _ = tools.sbx(self.problem, mom.decisions, dad.decisions)
      sis = tools.poly_mutate(self.problem, sis)
      kids += [NSGAPoint(sis)]
    return clones + kids

  def populate(self):
    return self.problem.populate(self.settings.pop_size, check_constraints=False)

if __name__ == "__main__":
  from problems.dtlz.c1_dtlz1 import C1_DTLZ1
  o = C1_DTLZ1(3)
  nsga3 = C_NSGA3(o, pop_size=92, gens = 400)
  nsga3.run()