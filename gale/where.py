from __future__ import print_function, division
from utils.lib import *
from BinaryTree import BinaryTree

__author__ = 'george'


def settings():
  return O(
    verbose =  False,
    b4 = '|..',
    seed = 1
  )

def configs(**d):
  return O(
    minSize   = 8,      # min leaf size
    depthMin  = 2,      # no pruning till this depth
    depthMax  = 10,     # max tree depth
    wriggle   = 0.2,    # min difference of 'better'
    prune     = True,   # If pruning should be performed
  ).update(**d)


def sqrt(pop):
  """
  Returns square root of length of list
  :param pop: List
  :return: Square root of size of list
  """
  return len(pop) ** 0.5

class NodePoint(O):
  def __init__(self, decisions):
    """
    Create a Nodepoint for a tree
    :param decisions: Decisions for the point
    :return:
    """
    O.__init__(self)
    self.decisions = decisions
    self.objectives = None
    self.evaluated = False
    self.a = None              # Distance from East
    self.b = None              # Distance from West
    self.c = None              # Distance between East and West
    self.x = None              # Projection of point on "c"

  def clone(self):
    """
    Duplicate the NodePoint
    :return:
    """
    other = NodePoint(self.decisions)
    other.objectives = self.objectives
    other.evaluated = self.evaluated
    other.a, other.b = self.a, self.b
    other.c, other.x = self.c, self.x
    return other

  def dist(self, problem, one):
    return problem.dist(self.decisions, one.decisions)

  def closest(self, problem, pop, init=sys.maxint, better=less):
    """
    :param problem: Problem used
    :param pop: Population
    :param init: Initial Value
    :param better: Function that defines what is better
    :return: farthest point from self in pop
    """
    dist, out = init, None
    for one in pop:
      if one != self:
        tmp = self.dist(problem, one)
        if better(tmp, dist):
          dist, out = tmp, one
    return one


  def furthest(self, problem, pop):
    """
    :param problem: Problem used
    :param pop: Population
    :return: farthest point from self in pop
    """
    self.closest(problem, pop, init=-sys.maxint, better=more)



class Node(BinaryTree):
  """

  """
  @staticmethod
  def format(pop):
    return [NodePoint(one) for one in pop]

  @staticmethod
  def projection(a, b, c):
    """
    Fastmap projection distance
    :param a: Distance from West
    :param b: Distance from East
    :param c: Distance between West and East
    :return: FastMap projection distance(float)
    """
    return (a**2 + c**2 - b**2) / (2*c+0.00001)

  def __init__(self, problem, pop, total_size, parent=None, level=1):
    """
    Initialize a node for the tree
    :param problem: Instance of the problem
    :param pop: Population for the node # Make sure format is called on pop first
    :param total_size: Total number of points in the whole population
    :param parent: Parent of the node
    :param level: Level of the tree
    :return: Node
    """
    BinaryTree.__init__(self)
    self.problem = problem
    self._pop = pop
    self.level = level
    self.total_size = total_size
    self._parent = parent
    self.east, self.west, self.c, self.x = None, None, None, None


  def fastmap(self, problem, pop):
    """

    :param problem:
    :param pop:
    :return:
    """
    one = rand_one(pop)
    self.west = one.furthest(problem, pop)
    self.east = one.furthest(problem, pop)
    self.c = self.west.dist(self.east)
    for one in pop:
      a = one.dist(self.west)
      b = one.dist(self.east)
      one.x = Node.projection(a, b, self.c)
      one.c = self.c
      one.a = a
      one.b = b
    pop = sorted(pop, key=lambda one: one.x)
    return pop


  def split(self, pop):
    mid = int(len(pop)/2)
    self.x = pop[mid].x
    self.east = pop[0]
    self.west = pop[-1]
    return pop[:mid], pop[mid:]

  def divide(self, threshold):
    """
    Recursively partition tree
    :param threshold:
    :return:
    """
    self._pop = self.fastmap(self.problem, self._pop)
    n = len(self._pop)
    if n >= threshold:
      wests, easts = self.split(self._pop)
    pass

