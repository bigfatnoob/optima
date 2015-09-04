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
    self.name = name
    self.low = low
    self.high = high

  def norm(self, val):
    return norm(val, self.low, self.high)

  def deNorm(self, val):
    return deNorm(val, self.low, self.high)


class Objective(O):
  def __init__(self, name, to_minimize=True, low=None, high=None):
    self.name = name
    self.to_minimize = to_minimize
    self.low = low
    self.high = high
    self.value = None

  def norm(self, val):
    return norm(val, self.low, self.high)


class Constraint(O):
  def __init__(self, name):
    self.name = name
    self.value = None
    self.status = False


class Problem(O):
  def __init__(self):
    self.name = ""
    self.desc = ""
    self.decisions = []
    self.objectives = []
    self.evals = 0
    self.population = []
    self.ideal_decisions = None
    self.ideal_objectives = None
    self.constraints = []

  def generate(self):
    while True:
      one = [uniform(d.low, d.high) for d in self.decisions]
      status = self.evaluate_constraints(one)[0]
      if not status:
        return one

  def assign(self, decisions):
    for i, d in enumerate(self.decisions):
      d.value = decisions[i]

  def populate(self, n):
    """
    Default method to create a population
    :param n - Size of population
    """
    self.population = []
    for _ in range(n):
      self.population.append(self.generate())
    return self.population

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

  def evaluate(self, decisions=None):
    pass

  def get_ideal_decisions(self, count = 500):
    pass

  def evaluate_constraints(self, one):
    return False, 0

  def dominates(self, one, two):
    """
    Check if one dominates two
    """
    one_status, one_offset = self.evaluate_constraints(one.decisions)
    two_status, two_offset = self.evaluate_constraints(two.decisions)
    better = self.better(one, two)
    if not one_status and not two_offset:
      # Return the better solution if both solutions satisfy the constraints
      return better
    elif not one_status:
      # Return 1, if 1 satisfies the constraints
      return 1
    elif not two_status:
      #Return 2, if 2 satisfies the constraints
      return 2
    # both fail the constraints
    elif one_offset < two_offset:
      # one has a lesser offset deviation
      return 1
    else:
      # two has a lesser offset deviation
      return 2

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
  def better(self, one, two):
    #TODO evaluate better function
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
      return [row[index] for row in matrix]
    ideal_objectives = self.get_ideal_objectives()
    print(ideal_objectives[0])
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