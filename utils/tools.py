from __future__ import print_function, division
import sys, os
sys.path.append(os.path.abspath("."))
__author__ = 'george'
from lib import *

SBX_CR = 1
SBX_ETA = 30
PM_ETA = 20

def get_betaq(rand, alpha, eta=30):
  if rand <= (1.0/alpha):
    return (rand * alpha) ** (1.0/(eta+1.0))
    #return (1.0/(2.0 - rand*alpha)) ** (1.0/(eta+1.0))
  else:
    return (1.0/(2.0 - rand*alpha)) ** (1.0/(eta+1.0))

def sbx(problem, mom, dad, **params):
  """
  Simulated Binary Crossover Between Mummy And Daddy.
  Produces Sister and Brother.
  cr - Crossover Rate
  eta - Size of population used for distribution
  """
  cr = params.get("cr", SBX_CR)
  eta = params.get("eta", SBX_ETA)
  sis = mom[:]
  bro = dad[:]
  if random.random() > cr: return mom, dad
  for i, decision in enumerate(problem.decisions):
    if random.random() > 0.5:
      sis[i], bro[i] = bro[i], sis[i]
      continue
    if abs(mom[i] - dad[i]) <= EPS:
      continue
    low = problem.decisions[i].low
    up = problem.decisions[i].high
    small = min(sis[i], bro[i])
    large = max(sis[i], bro[i])
    some = random.random()

    #sis
    beta = 1.0 + (2.0 * (small - low)/(large - small))
    alpha = 2.0 - beta**(-1*(eta+1.0))
    if some <= (1.0/alpha):
      betaq = (some * alpha) ** (1.0/(eta+1.0))
    else:
      betaq = (1.0/(2.0 - some*alpha)) ** (1.0/(eta+1.0))
    sis[i] = 0.5 * ((small+large) - betaq * (large - small))
    sis[i] = max(low, min(sis[i], up))

    #bro
    beta = 1.0 + (2.0 * (up - large)/(large - small))
    alpha = 2.0 - beta**(-1*(eta+1.0))
    if some <= (1.0/alpha):
      betaq = (some * alpha) ** (1.0/(eta+1.0))
    else:
      betaq = (1.0/(2.0 - some*alpha)) ** (1.0/(eta+1.0))
    bro[i] = 0.5 * ((small+large) + betaq * (large - small))
    bro[i] = max(low, min(bro[i], up))
    if random.random() > 0.5:
      sis[i], bro[i] = bro[i], sis[i]
  return sis, bro

def poly_mutate(problem, one, **params):
  """
  Perform Polynomial Mutation on a point.
  Default Mutation Probability = 1/No of Decisions in Problem
  """
  pm = params.get("pm", 1/len(problem.decisions))
  eta = params.get("eta", PM_ETA)
  mutant = [0] * len(problem.decisions)

  for i, decision in enumerate(problem.decisions):
    if random.random() > pm:
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

def binary_tournament_selection(problem, population, size, is_domination = True):
  """
  Select individual from the population of size
  tourn_size based on tournament evaluation
  :param problem: Problem used for evaluation
  :param population: Population to sample from
  :param size: Size of tournament
  :return: Most dominant individual from the tournament
  """
  tourn = random.sample(population, size)
  best = tourn[0]
  for i in range(1, len(tourn)):
    if is_domination:
      if nsga_domination(problem, tourn[i], best) == 1:
        best = tourn[i]
    else:
      if problem.better(tourn[i], best) == 1:
        best = tourn[i]
  return best

def nsga_domination(problem, one, two):
    """
    Domination is defined as follows:
    for all objectives a in "one" and
    all objectives b in "two"
    every a <= b

    for all objectives a in "one" and
    all objectives b in "two"
    at least one a < b

    Check if one set of decisions ("one")
    dominates other set of decisions ("two")

    Returns:
      0 - one and two are not better each other
      1 - one better than two
      2 - two better than one
    """
    one_status, one_offset = problem.evaluate_constraints(one.decisions)
    two_status, two_offset = problem.evaluate_constraints(two.decisions)
    if one_status and two_status:
      # Return the better solution if both solutions satisfy the constraints
      return problem.better(one, two)
    elif one_status:
      # Return 1, if 1 satisfies the constraints
      return 1
    elif two_status:
      #Return 2, if 2 satisfies the constraints
      return 2
    # both fail the constraints
    elif one_offset <= two_offset:
      # one has a lesser offset deviation
      return 1
    else:
      # two has a lesser offset deviation
      return 2