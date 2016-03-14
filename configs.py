"""
This file contains configuration of the
problems and optimizers
"""
from __future__ import print_function, division
from utils.lib import O

__author__ = 'panzer'

GENS = 400
REPEATS = 5

def gale_settings():
  """
  Default Settings for GALE
  """
  return O(
    pop_size        = 100,    # Size of Population
    gens            = GENS,   # Number of generations
    allowDomination = True,   # Domination Flag
    gamma           = 0.15    # Gamma factor for mutation
  )

def nsga2_settings():
  """
  Default Settings for NSGA2
  """
  return O(
    pop_size = 100,  # Size of population
    gens = GENS      # Number of generations
  )

def nsga3_settings():
  """
  Default Settings for NSGA3
  """
  return O(
    pop_size = 92,    # Size of Population
    gens = GENS,      # Number of generations
    cr = 1,           # Crossover rate for SBX
    nc = 30,          # eta for SBX
    nm = 20           # eta for Mutation
  )

def de_settings():
  """
  Default Settings for DE
  """
  return O(
    pop_size = 50,    # Size of Population
    gens = GENS,      # Number of generations
    f = 0.75,         # Mutation Factor
    cr = 0.3          # Crossover Rate
  )

def moead_settings():
  """
  Default MOEA/D settings
  """
  return O(
    pop_size = 91,      # Size of Population
    gens = GENS,        # Number of generations
    distance = "pbi",   # Distance metric
    T = 20,             # Closest weight vectors.
    penalty = 5,        # Penalty parameter for PBI distance
    crossover = "sbx",   # Crossover Metric
    cr = 1,             # Crossover rate for SBX
    nc = 20,            # eta for SBX
    nm = 20,            # eta for Mutation
    de_np = 0.9,        # DE neighborhood probability
    de_cr = 0.5         # DE crossover rate
  )

def spea2_settings():
  """
  Default SPEA2 settings
  :return:
  """
  return O(
    pop_size = 100,
    archive_size = 100,
    gens = GENS,
    sbx_eta = 20,
    pm_eta = 20
  )