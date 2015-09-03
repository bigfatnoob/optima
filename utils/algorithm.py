__author__ = 'panzer'

from lib import O

class Algorithm(O):
  def __init__(self, name, problem):
    """
    Base class algorithm
    :param name: Name of the algorithm
    :param problem: Instance of the problem
    :return:
    """
    self.name = name
    self.problem = problem
    self.select = None
    self.evolve = None
    self.recombine = None

  def run(self):
    pass