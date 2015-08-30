from __future__ import print_function, division
from utils.lib import *

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

