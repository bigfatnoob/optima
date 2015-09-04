from __future__ import print_function, division
import sys
import os
sys.path.append(os.path.abspath("."))
from utils.lib import *
from utils.algorithm import *
from copy import copy
import numpy as np

def settings():
  """
  Default Settings for NSGA 2
  :return:
  """
  return O(
    pop_size = 100,
    max_iter = 250
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


class Point(O):

  def __init__(self, decisions, problem, do_eval = True):
    """
    Represents a point in the frontier for NSGA
    :param decisions: Set of decisions
    :param problem: Instance of the problem
    :param do_eval: Flag to check if evaluation has to be performed
    """
    O.__init__(self)
    self.decisions = decisions
    self.rank = 0
    self.dominated = []
    self.dominating = 0
    if do_eval:
      self.objectives = problem.evaluate(decisions)
    else:
      self.objectives = []
    self.crowd_dist = 0




class NSGA2(Algorithm):
  def __init__(self, problem, gens = 250):
    """
    Initialize NSGA2 algorithm
    :param problem: Instance of the problem
    :param gens: Max number of Generations
    """
    Algorithm.__init__(self, 'NSGA2',problem)
    self.select = self.selector
    self.evolve = self.evolver
    self.frontiers = []
    self.gens = gens

  def selector(self, population):
    """
    Selector Function
    :param population: Population
    :return : Population and its kids
    """
    kids = self.make_kids(population)
    return population + kids

  def evolver(self, population, size):
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

  def run(self):
    """
    Runner function that runs the NSGA2 optimization algorithm
    """
    population = copy(self.problem.population)
    pop_size = len(population)
    points = []
    gens = 0
    while gens < self.gens:
      say(".")
      population = self.select(population)
      points = self.evolve(population, pop_size)
      population = [point.decisions for point in points]
      gens += 1
    print("")
    return points

  def make_kids(self, population):
    """
    Function that makes kids from the parents
    :param population: Parent population
    :return : Kids of the parents
    """
    kids = []
    for _ in range(len(population)):
      mom = random.choice(population)
      dad = None
      while True:
        dad = random.choice(population)
        if mom != dad: break
      sis, bro = self.sbx_crossover(mom, dad)
      sis = self.poly_mutate(sis)
      bro = self.poly_mutate(bro)
      kids += [sis, bro]
    return kids

  """
  Fast Non Dominated Sort
  :param - Population to sort
  :return - List of Frontiers
  """
  def fast_non_dom_sort(self, population = None):
    """
    Fast dominated sorting algorithm
    """
    frontiers = []
    front1 = []
    if population is None:
      population = self.problem.population
    points = [Point(one, self.problem) for one in population]
    for one, rest in loo(points):
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

  def convergence(self, obtained):
    """
    Calculate the convergence metric with respect to ideal
    solutions
    """
    problem = self.problem
    if problem.constraints:
      return
    ideals = problem.get_ideal_objectives()
    predicts = [o.objectives for o in obtained]
    gammas = []
    for predict in predicts:
      gammas.append(min([problem.dist(predict, ideal, one_norm = True, two_norm = True) for ideal in ideals]))
    return np.mean(gammas)

  @staticmethod
  def solution_range(obtained):
    """
    Calculate the range for each objective
    """
    predicts = [o.objectives for o in obtained]
    solutions = [[] for _ in range(len(predicts[0]))]
    for predict in predicts:
      for i in range(len(predict)):
        solutions[i].append(predict[i])
    for i, solution in enumerate(solutions):
      print("Objective :",i,
            "   Max = ", max(solutions[i]),
            "   Min = ", min(solutions[i]))

  """
  Calculate the diversity of the spread for a
  set of solutions
  """
  def diversity(self, obtained):
    def closest(one, many):
      min_dist = sys.maxint
      closest_point = None
      for this in many:
        dist = self.problem.dist(this, one, one_norm = True, two_norm = True)
        if dist < min_dist:
          min_dist = dist
          closest_point = this
      return min_dist, closest_point

    problem = self.problem
    if problem.constraints:
      return
    ideals = problem.get_ideal_objectives()
    predicts = [o.objectives for o in obtained]
    d_f = closest(ideals[0], predicts)[0]
    d_l = closest(ideals[-1], predicts)[0]
    distances = []
    for i in range(len(predicts)-1):
      distances.append(problem.dist(predicts[i], predicts[i+1], one_norm = True, two_norm = True))
    d_bar = np.mean(distances)
    d_sum = sum([abs(d_i - d_bar) for d_i in distances])
    delta = (d_f + d_l + d_sum) / (d_f + d_l + (len(predicts) - 1)*d_bar)
    return delta
