from __future__ import print_function, division
import sys
import os
sys.path.append(os.path.abspath("."))
from BinaryTree import BinaryTree
from utils.lib import *

__author__ = 'george'


def settings():
  return O(
    verbose =  False,
    b4 = '|.. ',
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

class NodePoint(Point):
  def __init__(self, decisions):
    """
    Create a Nodepoint for a tree
    :param decisions: Decisions for the point
    :return:
    """
    Point.__init__(self, decisions)
    self.objectives = None
    self.evaluated = False
    self.normalized = False
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
    other.normalized = self.normalized
    return other

  def clear(self):
    self.decisions = None
    self.objectives = None
    self.evaluated = False
    self.normalized = False
    self.a = None              # Distance from East
    self.b = None              # Distance from West
    self.c = None              # Distance between East and West
    self.x = None              # Projection of point on "c"

  def dist(self, problem, one, is_obj=True):
    """
    Estimate normalized euclidean distance between a point and another point
    :param problem: Instance of the problem
    :param one: point whose distance needs to be computed
    :param is_obj: Flag indicating objective or decision
    :return: Distance between self and one
    """
    if is_obj:
      self_normalized = self.normalized
      one_normalized = one.normalized
      self.normalized = True
      one.normalized = True
      return problem.dist(self.objectives, one.objectives,
                          one_norm = not self_normalized,
                          two_norm = not one_normalized,
                          is_obj = is_obj)
    else :
      return problem.dist(self.decisions, one.decisions,
                          is_obj = is_obj)

  def manhattan_dist(self, problem, one, is_obj = True):
    """
    Estimate manhattan distance between a point and another point
    :param problem: Instance of the problem
    :param one: point whose distance needs to be computed
    :param is_obj: Flag indicating objective or decision
    :return: Distance between self and one
    """
    if is_obj:
      self_normalized = self.normalized
      one_normalized = one.normalized
      self.normalized = True
      one.normalized = True
      return problem.manhattan_dist(self.objectives, one.objectives,
                          one_norm = not self_normalized,
                          two_norm = not one_normalized,
                          is_obj = is_obj)
    else :
      return problem.manhattan_dist(self.decisions, one.decisions,
                          is_obj = is_obj)

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
        tmp = self.dist(problem, one, is_obj=False)
        if better(tmp, dist):
          dist, out = tmp, one
    return one


  def furthest(self, problem, pop):
    """
    :param problem: Problem used
    :param pop: Population
    :return: farthest point from self in pop
    """
    return self.closest(problem, pop, init=-sys.maxint, better=more)

  def evaluate(self, problem):
    self.objectives = problem.evaluate(self.decisions)
    self.evaluated = True



class Node(BinaryTree):
  """
  Represents node of a tree
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

  def __init__(self, problem, pop, total_size, parent=None, level=1, n=1):
    """
    Initialize a node for the tree
    :param problem: Instance of the problem
    :param pop: Population for the node # Make sure format is called on pop first
    :param total_size: Total number of points in the whole population
    :param parent: Parent of the node
    :param level: Level of the tree
    :param n: Represents cut in the node
    :return: Node
    """
    BinaryTree.__init__(self)
    self.problem = problem
    self._pop = pop
    self.level = level
    self.N = n
    self.total_size = total_size
    self._parent = parent
    self.east, self.west, self.c, self.x = None, None, None, None
    self.abort = False


  def fastmap(self, problem, pop):
    """
    Fastmap function that projects all the points on the principal component
    :param problem: Instance of the problem
    :param pop: Set of points in the cluster population
    :return:
    """
    one = rand_one(pop)
    self.west = one.furthest(problem, pop)
    self.east = one.furthest(problem, pop)
    self.c = self.west.dist(problem, self.east, is_obj=False)
    for one in pop:
      a = one.dist(problem, self.west, is_obj=False)
      b = one.dist(problem, self.east, is_obj=False)
      one.x = Node.projection(a, b, self.c)
      one.c = self.c
      one.a = a
      one.b = b
    pop = sorted(pop, key=lambda one: one.x)
    return pop


  def split(self, pop, cut):
    """
    Split the population at the midpoint
    :param pop:
    :return:
    """
    # TODO - I swapped east and west from the original
    self.x = pop[cut].x
    self.west = pop[0]
    self.east = pop[-1]
    return pop[:cut], pop[cut:]

  def divide(self, threshold, abort = False):
    """
    Recursively partition tree
    :param threshold:
    :return:
    """
    def afew(pop):
      clones = [point.clone() for point in pop]
      return clones

    self._pop = self.fastmap(self.problem, self._pop)
    self.n = len(self._pop)
    n = len(self._pop)

    cut, _ = self.binary_chop(self._pop, n//2, None, 2*n ** 0.5, n)
    self.abort = abort
    if not abort and n >= threshold:
      # Splitting
      wests, easts = self.split(self._pop, cut)

      if self.west != self.east:
        if self.N > cut:
          little_n = cut
        else:
          little_n = self.N

        west_abort = False
        east_abort = False
        if not self.east.evaluated:
          self.east.evaluate(self.problem)
        if not self.west.evaluated:
          self.west.evaluate(self.problem)

        weights = self.problem.directional_weights()

        weighted_west = [c*w for c,w in zip(self.west.objectives, weights)]
        weighted_east = [c*w for c,w in zip(self.east.objectives, weights)]
        objs = self.problem.objectives
        west_loss = loss(weighted_west, weighted_east, mins=[o.low for o in objs], maxs=[o.high for o in objs])
        east_loss = loss(weighted_east, weighted_west, mins=[o.low for o in objs], maxs=[o.high for o in objs])

        EPSILON = 1.0
        if west_loss < EPSILON * east_loss:
          east_abort = True
        if east_loss < EPSILON * west_loss:
          west_abort = True

        self.left = Node(self.problem, afew(wests), self.total_size, parent=self, level=self.level+1, n=little_n)\
          .divide(threshold, abort=west_abort)
        self.right = Node(self.problem, afew(easts), self.total_size, parent=self, level=self.level+1, n=little_n)\
          .divide(threshold, abort=east_abort)
    return self

  def sum_squared(self, pop):
    """
    Compute the sum squared value between all
    the points in the population
    :param pop: array of NodePoint
    :return: Sum Squared Measure
    """
    d_mins = []
    for i, one in enumerate(pop):
      temp_dists = []
      for j, two in enumerate(pop):
        if i != j:
          temp_dists.append(one.manhattan_dist(self.problem, two, is_obj=False))
      d_mins.append(min(temp_dists))
    d_bar = avg(d_mins)
    ssm = ((1 / (len(pop) - 1)) * sum([(d_bar - d_i) ** 2 for d_i in d_mins])) ** 0.5
    return ssm

  def binary_chop(self, pop, cut, delta, min_n, last_cut=None):
    """
    Perform Binary chop for an appropriate place to split
    :param pop: Population to split
    :param cut: Proposed cut
    :param delta: Difference between the left child and right child
    :param min_n: Minimum number of kids to continue splitting
    :param last_cut: Parent's cut
    :return: the best point to cut, the delta between the left and right child
    """
    if cut < min_n or (last_cut - cut) < min_n:
      # stop if too small
      return cut, delta

    # segment left and right sides
    left = pop[:cut]
    right = pop[cut:]

    #get spreads of each side
    left_spread = self.sum_squared(left)
    right_spread = self.sum_squared(right)
    delta = abs(left_spread - right_spread)

    # recurse
    left_cut, left_delta = self.binary_chop(pop, cut//2, delta, min_n, cut)
    right_cut, right_delta = self.binary_chop(pop, cut + (last_cut - cut)//2, delta, min_n, cut)

    # minimize deltas
    smallest = min(delta, left_delta, right_delta)
    if smallest == delta:
      return cut, delta
    elif smallest == left_delta:
      return left_cut, left_delta
    else:
      return right_cut, right_delta

  def show(self):
    out = ""
    out += (self.level - 1) * settings().b4 + str(self.n) + " (" + str(id(self) % 1000)+ ") \n"
    if self.left:
      out += self.left.show()
    if self.right:
      out += self.right.show()
    return out

def _test():
  from problems.ZDT1 import ZDT1
  o = ZDT1()
  o.populate(100)
  node = Node(o, Node.format(o.population), 100).divide(sqrt(o.population))
  print(node.show())

if __name__ == "__main__":
  _test()

