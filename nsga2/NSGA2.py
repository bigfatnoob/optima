from __future__ import print_function, division
import sys
import os
sys.path.append(os.path.abspath("."))
from utils.lib import *
from utils.algorithm import Algorithm

def settings():
  """
  Default Settings for NSGA 2
  :return: default settings
  """
  return O(
    pop_size = 100,
    gens = 250
  )

def loo(points):
  """
  Iterator which generates a
  test case and training set
  :param points:
  :return:
  """
  for i in range(len(points)):
    one = points[i]
    rest = points[:i] + points[i+1:]
    yield one, rest


class NSGAPoint(Point):

  def __init__(self, decisions, problem=None):
    """
    Represents a point in the frontier for NSGA
    :param decisions: Set of decisions
    :param problem: Instance of the problem
    :param do_eval: Flag to check if evaluation has to be performed
    """
    Point.__init__(self, decisions, problem)
    self.rank = 0
    self.dominated = []
    self.dominating = 0
    self.crowd_dist = 0

  def clone(self):
    """
    Method to clone a point
    :return:
    """
    new = NSGAPoint(self.decisions)
    new.objectives = self.objectives
    return new

  def __gt__(self, other):
    if self.rank != other.rank:
      return self.crowd_dist > other.crowd_dist
    else:
      return self.rank < other.rank


class NSGA2(Algorithm):
  """
  Sort the first *k* *individuals* into different nondomination levels
  using the "Fast Nondominated Sorting Approach" proposed by Deb et al.,
  see [Deb2002]_. This algorithm has a time complexity of :math:`O(MN^2)`,
  where :math:`M` is the number of objectives and :math:`N` the number of
  individuals.

  .. [Deb2002] Deb, Pratab, Agarwal, and Meyarivan, "A fast elitist
     non-dominated sorting genetic algorithm for multi-objective
     optimization: NSGA-II", 2002.

  Check References folder for the paper
  """
  def __init__(self, problem, gens = settings().gens):
    """
    Initialize NSGA2 algorithm
    :param problem: Instance of the problem
    :param gens: Max number of generations
    """
    Algorithm.__init__(self, 'NSGA2',problem)
    self.select = self._select
    self.evolve = self._evolve
    self.frontiers = []
    self.gens = gens

  def run(self):
    """
    Runner function that runs the NSGA2 optimization algorithm
    """
    population = [NSGAPoint(one) for one in self.problem.population]
    pop_size = len(population)
    gens = 0
    while gens < self.gens:
      say(".")
      population = self.select(population)
      population = self.evolve(population, pop_size)
      gens += 1
    print("")
    return population

  def _select(self, population, is_domination = True):
    """
    Selector Function
    :param population: Population
    :param is_domination: Boolean parameter that decides
    :return : Population and its kids
    """
    kids = []
    clones = [one.clone() for one in population]
    for _ in range(len(clones)//2):
      mom = self.bin_select_tournament(clones, 4, is_domination)
      dad = None
      while True:
        dad = self.bin_select_tournament(clones, 4, is_domination)
        if not mom == dad: break
      sis, bro = self.sbx_crossover(mom.decisions, dad.decisions)
      sis = self.poly_mutate(sis)
      bro = self.poly_mutate(bro)
      kids += [NSGAPoint(sis), NSGAPoint(bro)]
    return clones + kids

  def _evolve(self, population, size):
    """
    Mutator Function: Performs crossover and polynomial mutation
    :param population:Population that needs to be evolved
    :param size: Expected size of the result
    :return : The mutated population
    """
    fronts = self.fast_non_dom_sort(population)
    pop_next = []
    for i, front in enumerate(fronts):
      fronts[i] = self.assign_crowd_dist(front)
      pop_next += fronts[i]
      if len(pop_next) >= size:
        pop_next = pop_next[:size]
        break
    return pop_next

  def bin_select_tournament(self, population, tourn_size, is_domination = True):
    """
    Select 2 individuals from the population of size tournsize
    :param population:
    :param tourn_size:
    :return:
    """
    tourn = random.sample(population, tourn_size)
    best = tourn[0]
    for i in range(1, len(tourn)):
      if is_domination:
        if self.problem.dominates(tourn[i], best) == 1:
          best = tourn[i]
      else:
        if tourn[i] > best:
          best = tourn[i]
    return best

  def fast_non_dom_sort(self, population):
    """
    Fast Non Dominated Sort
    :param - Population to sort
    :return - List of Frontiers
    """
    frontiers = []
    front1 = []
    for one in population:
      one.evaluate(self.problem)
    for one, rest in loo(population):
      for two in rest:
        domination_status = self.problem.dominates(one, two)
        if domination_status == 1:
          one.dominated.append(two)
        elif domination_status == 2:
          one.dominating += 1
      if one.dominating == 0:
        one.rank = 1
        front1.append(one)

    current_rank = 1
    while True:
      front2 = []
      for one in front1:
        for two in one.dominated:
          two.dominating -= 1
          if two.dominating == 0:
            two.rank =  current_rank + 1
            front2.append(two)
      current_rank += 1
      if len(front2) == 0 :
        break
      else :
        frontiers.append(front2)
        front1 = front2
    return frontiers

  def assign_crowd_dist(self, frontier):
    """
    Crowding distance between each point in
    a frontier.
    """
    l = len(frontier)
    for m in range(len(self.problem.objectives)):
      frontier = sorted(frontier, key=lambda x:x.objectives[m])
      obj_min = frontier[0].objectives[m]
      obj_max = frontier[-1].objectives[m]
      frontier[0].crowd_dist = float("inf")
      frontier[-1].crowd_dist = float("inf")
      for i in range(1,l-1):
        frontier[i].crowd_dist += (frontier[i+1].objectives[m] - frontier[i-1].objectives[m])/(obj_max - obj_min)
    return sorted(frontier, key=lambda x:x.crowd_dist, reverse=True)

  def sbx_crossover(self, mom, dad, cr=0.9, eta=30):
    """
    Simulated Binary Crossover Between Mummy And Daddy.
    Produces Sister and Brother.
    cr = probability of crossover
    """
    problem = self.problem
    sis = [0]*len(mom)
    bro = [0]*len(mom)
    if random.random() > cr: return mom, dad

    for i, decision in enumerate(problem.decisions):
      if random.random() > 0.5:
        sis[i] = mom[i]
        bro[i] = dad[i]
        continue

      if abs(mom[i] - dad[i]) <= EPS:
        sis[i] = mom[i]
        bro[i] = dad[i]
        continue

      low = problem.decisions[i].low
      up = problem.decisions[i].high
      small = min(mom[i], dad[i])
      large = max(mom[i], dad[i])
      some = random.random()

      #sis
      beta = 1.0 + (2.0 * (small - low)/(large - small))
      alpha = 2.0 - beta ** (-(eta+1.0))
      betaq = get_betaq(some, alpha, eta)
      sis[i] = 0.5 * ((small+large) - betaq * (large - small))
      sis[i] = max(low, min(sis[i], up))

      #bro
      beta = 1.0 + (2.0 * (up - large)/(large - small))
      alpha = 2.0 - beta ** (-(eta+1.0))
      betaq = get_betaq(some, alpha, eta)
      bro[i] = 0.5 * ((small+large) + betaq * (large - small))
      bro[i] = max(low, min(bro[i], up))
    return sis, bro

  def poly_mutate(self, one, eta = 20):
    """
    Perform Polynomial Mutation on a point.
    Mutation Rate = 1/No of Decisions in Problem
    """
    problem = self.problem
    mr = 1 / len(problem.decisions)
    mutant = [0] * len(problem.decisions)

    for i, decision in enumerate(problem.decisions):
      if random.random() < mr:
        mutant[i] = one[i]
        continue

      low = problem.decisions[i].low
      high = problem.decisions[i].high
      del1 = (one[i] - low)/(high - low)
      del2 = (high - one[i])/(high - low)

      mut_pow = 1/(eta+1)
      rand_no = random.random()

      if rand_no < 0.5:
        xy = 1 - del1
        val = 2 * rand_no + (1-2*rand_no) * (xy ** (eta+1))
        del_q = val ** mut_pow - 1
      else:
        xy = 1 - del2
        val = 2 * (1 - rand_no) + 2*(rand_no-0.5) * (xy ** (eta+1))
        del_q = 1 - val ** mut_pow
      mutant[i] = max(low, min(one[i] + del_q * (high-low) , high))

    return mutant


