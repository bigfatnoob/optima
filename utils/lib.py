from __future__ import division, print_function
import sys, os
sys.path.append(os.path.abspath("."))
import random
import math
import time
import json
import numpy as np

__author__ = 'panzer'

PI = math.pi
EPS = 0.000001

def cos(x):
  return math.cos(x)

def sin(x):
  return math.sin(x)

"""
Default class which everything extends.
"""
class O:
  def __init__(self, **d): self.has().update(**d)
  def has(self): return self.__dict__
  def update(self, **d) : self.has().update(d); return self
  def __repr__(self)   :
    show=[':%s %s' % (k,self.has()[k])
      for k in sorted(self.has().keys() )
      if k[0] is not "_"]
    txt = ' '.join(show)
    if len(txt) > 60:
      show=map(lambda x: '\t'+x+'\n',show)
    return '{'+' '.join(show)+'}'
  def __getitem__(self, item):
    return self.has().get(item)

"""
An accumulator for reporting on numbers.
"""
class N:
  """Add/delete counts of numbers."""
  def __init__(self, inits=None):
    if inits is None: inits = []
    self.n = self.mu = self.m2 = self.cache = None
    self.zero()
    map(self.__iadd__,inits)
  def zero(self):
    self.n = self.mu = self.m2 = 0
    self.cache= Cache()
  def sd(self)  :
    if self.n < 2:
      return 0
    else:
      return (max(0, self.m2)/(self.n - 1))**0.5
  def __iadd__(self, x):
    self.cache += x
    self.n     += 1
    delta       = x - self.mu
    self.mu    += delta/(1.0*self.n)
    self.m2    += delta*(x - self.mu)
    return self
  def __isub__(self,x):
    self.cache = Cache()
    if self.n < 2: return self.zero()
    self.n  -= 1
    delta = x - self.mu
    self.mu -= delta/(1.0 * self.n)
    self.m2 -= delta*(x - self.mu)
    return self

CACHE_SIZE=128
class Cache:
  """
  Keep a random sample of stuff seen so far.
  """
  def __init__(self, inits=None):
    if inits is None: inits = []
    self.all, self.n, self._has = [],0,None
    map(self.__iadd__, inits)
  def __iadd__(self, x):
    self.n += 1
    if len(self.all) < CACHE_SIZE: # if not full
      self._has = None
      self.all += [x]               # then add
    else: # otherwise, maybe replace an old item
      if random.random() <= CACHE_SIZE/self.n:
        self._has=None
        self.all[int(random.random()*CACHE_SIZE)] = x
    return self
  def has(self):
    if self._has is None:
      lst  = sorted(self.all)
      med,iqr = median_iqr(lst,ordered=True)
      self._has = O(
        median = med,      iqr = iqr,
        lo     = self.all[0], hi  = self.all[-1])
    return self._has

def median_iqr(lst, ordered=False):
  if not ordered:
    lst = sorted(lst)
  n = len(lst)
  q = n//4
  iqr = lst[q*3] - lst[q]
  if n % 2:
    return lst[q*2],iqr
  else:
    p = max(0,q-1)
    return (lst[p] + lst[q]) * 0.5,iqr

def norm(x, low, high):
  """
  Method to normalize value
  between 0 and 1
  """
  nor = (x - low)/(high - low + EPS)
  if nor > 1:
    return 1
  elif nor < 0:
    return 0
  return nor


def de_norm(x, low, high):
  """
  Method to de-normalize value
  between low and high
  """
  de_nor = x*(high-low) + low
  if de_nor > high:
    return high
  elif de_nor < low:
    return low
  return de_nor


def uniform(low, high):
  return random.uniform(low, high)


def say(*lst):
  print(*lst, end="")
  sys.stdout.flush()

def rand_one(lst):
  return random.choice(lst)

def more(x,y):
  """
  Check if x > y
  :param x: Left Comparative Value
  :param y: Right Comparative Value
  :return: Boolean
  """
  return x > y

def less(x,y):
  """
  Check if x < y
  :param x: Left Comparative Value
  :param y: Right Comparative Value
  :return: Boolean
  """
  return x < y

def avg(lst):
  """
  Average of list
  :param lst:
  :return:
  """
  return sum(lst)/float(len(lst))

def shuffle(lst):
  random.shuffle(lst)
  return lst

def loss(x1, x2, mins=None, maxs=None):
  """
  Compute Normalized difference between two vectors
  :param x1: List 1
  :param x2: List 2
  :param mins: Min Possible Values
  :param maxs: Max Possible values
  :return:
  """
  #normalize if mins and maxs are given
  if mins and maxs:
      x1 = [norm(x, mins[i], maxs[i]) for i,x in enumerate(x1)]
      x2 = [norm(x, mins[i], maxs[i]) for i,x in enumerate(x2)]

  o = min(len(x1), len(x2)) #len of x1 and x2 should be equal
  return sum([math.exp((x2i - x1i)/o) for x1i, x2i in zip(x1,x2)])/o


def gt(x, y):
  """
  True if x > y
  :param x:
  :param y:
  :return: True/False
  """
  return x > y

def gte(x, y):
  """
  True if x >= y
  :param x:
  :param y:
  :return: True/False
  """
  return x >= y

def lt(x, y):
  """
  True if x < y
  :param x:
  :param y:
  :return: True/False
  """
  return x < y

def lte(x, y):
  """
  True if x <= y
  :param x:
  :param y:
  :return:
  """
  return x <= y

def neq(x, y):
  """
  True if x != y
  :param x:
  :param y:
  :return: True/False
  """
  return x != y

def eq(x, y):
  """
  True if x == y
  :param x:
  :param y:
  :return: True/False
  """
  return x == y

def drange(start, end, num=100, end_point = True):
  """
  Decimal Range between start and end
  :param start: Start value
  :param end: End Value
  :param num: Number of values
  :param end_point: If end point has to be considered
  :return:
  """
  delta =(end - start)/num
  if end_point:
    func = lte
  else:
    func = lt
  values = []
  temp = start
  while func(temp, end):
    temp = round(temp, 6)
    values.append(temp)
    temp += delta
  return values

class Point(O):
  id = 0
  def __init__(self, decisions, problem=None):
    """
    Represents a point in the frontier for NSGA
    :param decisions: Set of decisions
    :param problem: Instance of the problem
    """
    O.__init__(self)
    Point.id += 1
    self.id = Point.id
    self.decisions = decisions[:]
    if problem:
      self.objectives = problem.evaluate(decisions)
      self.norm_objectives = problem.norm(self.objectives)
    else:
      self.objectives = []
      self.norm_objectives = []

  def clone(self):
    """
    Method to clone a point
    :return:
    """
    new = Point(self.decisions)
    new.objectives = self.objectives[:]
    new.norm_objectives = self.norm_objectives[:]
    return new

  def evaluate(self, problem, stat = None, gen = None):
    """
    Evaluate a point
    :param problem: Problem used to evaluate
    """
    if not self.objectives:
      self.objectives = problem.evaluate(self.decisions)
      self.norm_objectives = problem.norm(self.objectives)
      if stat:
        stat.evals+=1
        if gen is not None:
          if stat.gen_evals is None:
            stat.gen_evals = []
          if len(stat.gen_evals) == gen:
            stat.gen_evals[gen-1] += 1
          else:
            stat.gen_evals.append(1)

  def __eq__(self, other):
    return self.decisions == other.decisions

  def __hash__(self):
    return hash(frozenset(self.decisions))

def is_even(i):
  """
  Checks if "i" is even
  :param i:
  :return: True / False
  """
  return i % 2 == 0

def get_time():
  """
  Get Current Wall clock time in milliseconds
  :return:
  """
  return time.clock()

def mkdir(directory):
  """
  Implements the "mkdir" linux function
  :param directory:
  :return:
  """
  if not os.path.exists(directory):
    os.makedirs(directory)

def get_subdirectories(base_dir):
  """
  List sub-directories in a folder
  :param base_dir:
  :return:
  """
  return [x[1] for x in os.walk(base_dir)][0]

def ls(directory):
  """
  Implements the "ls" linux function
  :param directory:
  :return:
  """
  return os.listdir(directory)

def get_json(file_path):
  """
  Retrieve json from a file
  :param file_path:
  :return: JSON object
  """
  with open(file_path) as json_file:
    json_data = json.load(json_file)
  return json_data

def mean_iqr(lst):
  """
  return mean and iqr of a list.
  :param lst: List to fetch mean and iqr
  :return: (mean, iqr)
  """
  mean = np.mean(lst)
  q75, q25 = np.percentile(lst, [75, 25])
  return mean, q75 - q25

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