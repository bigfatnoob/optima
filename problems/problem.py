import sys
import os
sys.path.append(os.path.abspath("."))
from utils.lib import *
import matplotlib.pyplot as plt

"""
:return
  -1 indicates worse
  0 indicates equal
  1 indicates better
"""
def compare(one, two, minimize=True):
  if one == two:
    return 0
  if minimize:
    status = 1 if one < two else -1
  else:
    status = 1 if one > two else -1
  return status

class Decision(O):
  def __init__(self, name, low, high):
    O.__init__(self)
    self.name = name
    self.low = low
    self.high = high

  def norm(self, val):
    return norm(val, self.low, self.high)

  def de_norm(self, val):
    return de_norm(val, self.low, self.high)

  def trim(self, val):
    return max(self.low, min(self.high, val))


class Objective(O):
  def __init__(self, name, to_minimize=True, low=None, high=None):
    O.__init__(self)
    self.name = name
    self.to_minimize = to_minimize
    self.low = low
    self.high = high
    self.value = None

  def norm(self, val):
    return norm(val, self.low, self.high)

class Constraint(O):
  def __init__(self, name):
    O.__init__(self)
    self.name = name
    self.value = None
    self.status = False


class Problem(O):
  def __init__(self):
    O.__init__(self)
    self.name = ""
    self.desc = ""
    self.decisions = []
    self.objectives = []
    self.evals = 0
    self.population = []
    self.ideal_decisions = None
    self.ideal_objectives = None
    self.constraints = []

  def title(self):
    return self.name + "_" + str(len(self.decisions)) + "_" + str(len(self.objectives))

  def generate(self):
    while True:
      one = [uniform(d.low, d.high) for d in self.decisions]
      status = self.evaluate_constraints(one)[0]
      if status:
        return one

  def assign(self, decisions):
    for i, d in enumerate(self.decisions):
      d.value = decisions[i]

  def directional_weights(self):
    """
    Method that returns an array of weights
    based on the objective. If objective is
    to be maximized, return 1 else return 0
    :return:
    """
    weights = []
    for obj in self.objectives:
      # w is negative when we are maximizing that objective
      if obj.to_minimize:
        weights.append(1)
      else:
        weights.append(-1)
    return weights

  def populate(self, n):
    """
    Default method to create a population
    :param n - Size of population
    """
    population = []
    for _ in range(n):
      population.append(self.generate())
    return population

  def norm(self, one, is_obj = True):
    """
    Method to normalize a point
    :param one - Point to be normalized
    :param is_obj - Boolean indicating Objective or Decision
    """
    normalized = []
    if is_obj:
      features = self.objectives
    else:
      features = self.decisions
    for i, feature in enumerate(one):
      normalized.append(features[i].norm(feature))
    return normalized

  def dist(self, one, two, one_norm = True, two_norm = True, is_obj = True):
    """
    Returns normalized euclidean distance between one and two
    :param one - Point A
    :param two - Point B
    :param one_norm - If A has to be normalized
    :param two_norm - If B has to be normalized
    :param is_obj - If the points are objectives or decisions
    """
    one_norm = self.norm(one, is_obj) if one_norm else one
    two_norm = self.norm(two, is_obj) if two_norm else two
    delta = 0
    count = 0
    for i,j in zip(one_norm, two_norm):
      delta += (i-j) ** 2
      count += 1
    return (delta/count) ** 0.5

  def manhattan_dist(self, one, two, one_norm = True, two_norm = True, is_obj = True):
    """
    Returns manhattan distance between one and two
    :param one - Point A
    :param two - Point B
    :param one_norm - If A has to be normalized
    :param two_norm - If B has to be normalized
    :param is_obj - If the points are objectives or decisions
    """
    one_norm = self.norm(one, is_obj) if one_norm else one
    two_norm = self.norm(two, is_obj) if two_norm else two
    delta = 0
    for i, j in zip(one_norm, two_norm):
      delta += abs(i -j)
    return delta

  def evaluate(self, decisions):
    pass

  def get_ideal_decisions(self, count = 500):
    return None

  def get_ideal_objectives(self, count = 500):
    return None

  def evaluate_constraints(self, one):
    return True, 0

  def better(self, one, two):
    """
    Function that checks which of the
    two decisions are dominant
    :param one:
    :param two:
    :return:
    """
    obj1 = one.objectives
    obj2 = two.objectives
    one_at_least_once = False
    two_at_least_once = False
    for index, (a, b) in enumerate(zip(obj1, obj2)):
      status = compare(a, b, self.objectives[index].to_minimize)
      if status == -1:
        #obj2[i] better than obj1[i]
        two_at_least_once = True
      elif status == 1:
        #obj1[i] better than obj2[i]
        one_at_least_once = True
      if one_at_least_once and two_at_least_once:
        #neither dominates each other
        return 0
    if one_at_least_once:
      return 1
    elif two_at_least_once:
      return 2
    else:
      return 0

  def binary_dominates(self, one, two):
    """
    Check if one dominates two
    :param one: Point one
    :param two: Point two
    :return:
    1 if one dominates two
    2 if two dominates one
    0 if one and two are non-dominated
    """
    obj1 = one.objectives
    obj2 = two.objectives
    one_at_least_once = False
    two_at_least_once = False
    for index, (a, b) in enumerate(zip(obj1, obj2)):
      status = compare(a, b, self.objectives[index].to_minimize)
      if status == -1:
        #obj2[i] better than obj1[i]
        two_at_least_once = True
      elif status == 1:
        #obj1[i] better than obj2[i]
        one_at_least_once = True
      if one_at_least_once and two_at_least_once:
        #neither dominates each other
        return 0
    if one_at_least_once:
      return 1
    elif two_at_least_once:
      return 2
    else:
      return 0

  def plot(self, points = None, constraints = None,  file_path="figures/tmp.png"):
    def get_column(matrix, index):
      return [line[index] for line in matrix]
    ideal_objectives = self.get_ideal_objectives()
    if ideal_objectives:
      if len(ideal_objectives[0]) != 2:
        print("Can plot only 2d graphs")
        return
      x,y = get_column(ideal_objectives, 0), get_column(ideal_objectives, 1)
      plt.plot(x, y)
    if points:
     comp_objs = [point.objectives for point in points]
     c_x, c_y = get_column(comp_objs, 0), get_column(comp_objs, 1)
     plt.plot(c_x, c_y, 'ro')
    if constraints:
      for row in constraints:
        plt.plot(row[0], row[1])
    plt.savefig(file_path)

  def populate_from_file(self, file_path):
    with open(file_path) as f:
      content = f.readlines()
    for line in content:
      pts = line.strip().split(", ")
      pts = [float(pt) for pt in pts]
      self.population.append(pts)

  def get_pareto_front(self):
    """
    Get the pareto frontier
    for the problem from
    file in
    :return: List of lists of the pareto frontier
    """
    assert False

