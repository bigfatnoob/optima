from __future__ import print_function, division
import sys, os
sys.path.append(os.path.abspath("."))
from utils.tools import sbx
from utils.lib import *

__author__ = 'panzer'


def get_crossover(name):
  if name == "sbx":
    return simulated_binary_crossover
  elif name == "de":
    return differential_evolution
  assert False, "Invalid Crossover type : %s"%name


"""
Mutation Methods
"""
def simulated_binary_crossover(moead, point, population):
  """
  Perform Simulated Binary Crossover
  for producing mutants
  :param moead: Instance of MOEAD
  :param point: Instance of MOEADPoint to generate a crossover
  :param population: Population to search from
  :return: List containing Decisions of mutant
  """
  one = rand_one(point.neighbor_ids)
  two = rand_one(point.neighbor_ids)
  while one != two:
    two = rand_one(point.neighbor_ids)
  mom = population[one].decisions
  dad = population[two].decisions
  child, _ = sbx(moead.problem, mom, dad, cr = moead.settings.cr, eta=moead.settings.nc)
  return child


def differential_evolution(moead, point, population):
  """
  Use Differential Evolution to
  produce mutants
  :param moead: Instance of MOEAD
  :param point: Instance of MOEADPoint to generate a crossover
  :param population: Population to search from
  :return: List containing Decisions of mutant
  """
  problem = moead.problem
  rnd = random.random()
  if rnd < moead.settings.de_np:
    is_local = True
    moead.neighborhood = "local"
  else:
    is_local = False
    moead.neighborhood = "global"
  mom, dad = select_mates(point, population, is_local)
  me = point.decisions
  mom = population[mom].decisions
  dad = population[dad].decisions
  new = [None]*len(problem.decisions)
  for i, dec in enumerate(problem.decisions):
    new[i] = me[i] + moead.settings.de_cr*(dad[i] - mom[i])
    if new[i] < dec.low:
      new[i] = dec.low + random.random()*(me[i] - dec.low)
    if new[i] > dec.high:
      new[i] = dec.high - random.random()*(dec.high - me[i])
  return new


"""
Utility Methods
"""
def select_mates(point, population, is_local):
  """
  Select mates to perform DE
  :param point:
  :param population:
  :param is_local:
  :return: two mates for mating
  """
  seen = [point.id]
  def one_more(ids):
    one = rand_one(ids)
    while one not in seen:
      one = rand_one(ids)
      seen.append(one)
    return one
  neighbor_ids = point.neighbor_ids if is_local else population.keys()
  mom = one_more(neighbor_ids)
  dad = one_more(neighbor_ids)
  return mom, dad

