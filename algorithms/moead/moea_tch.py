from __future__ import print_function, division
import sys, os
sys.path.append(os.path.abspath("."))
from moea_d import MOEA_D

__author__ = 'panzer'

class MOEA_TCH(MOEA_D):
  """
  Implements TCH version of MOEAD
  """
  def __init__(self, problem, population=None, **settings):
    MOEA_D.__init__(self, problem, population=population, **settings)
    self.settings.update(distance="tch", crossover="sbx")
    self.name = "MOEA_TCH"
