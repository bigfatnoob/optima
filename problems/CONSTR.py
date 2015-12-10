from __future__ import print_function, division
import sys, os
sys.path.append(os.path.abspath("."))
from problem import *
from copy import deepcopy
import numpy as np

"""
No of Decisions = n = 2.
x1 = [0.1,1]
x2 = [0, 5]
Objectives:
  f1(x) = x1 ..... [0.1, 1]
  f2(x) = (1+x2)/x1 ....... [1, 60]
Constraints:
  g1(x) = x2 + 9*x1 >= 6
  g1(x) = - x2 + 9*x1 >= 1
"""
class CONSTR(Problem):
  def __init__(self):
    Problem.__init__(self)
    self.name = "CONSTR"
    self.desc = "No of Decisions = n = 2. \
                x1 = [0.1,1] \
                x2 = [0, 5] \
                Objectives: \
                  f1(x) = x1 ..... [0.1, 1] \
                  f2(x) = (1+x2)/x1 ....... [1, 60] \
                Constraints: \
                  g1(x) = x2 + 9*x1 >= 6 \
                  g1(x) = - x2 + 9*x1 >= 1"
    self.decisions = [Decision("x1",0.1,1), Decision("x2",0,5)]
    self.objectives = [Objective("f1",0.1,1), Objective("f2",1,60)]
    self.constraints = [Constraint("g1"), Constraint("g2")]
    self.evals = 0
    self.ideal_decisions = None
    self.ideal_objectives = None

  def evaluate_constraints(self, decisions):
    status = True
    offset = 0
    self.constraints[0].value = decisions[1] + 9*decisions[0] - 6
    if self.constraints[0].value < 0:
      offset += abs(self.constraints[0].value)
      status = False
    self.constraints[1].value = - decisions[1] + 9*decisions[0] - 1
    if self.constraints[1].value < 0:
      offset += abs(self.constraints[1].value)
      status = False
    return status, offset


  def evaluate(self, decisions):
    self.objectives[0].value = decisions[0]
    self.objectives[1].value = (1+decisions[1])/decisions[0]
    return [self.objectives[0].value, self.objectives[1].value]

  def get_ideal_decisions(self, count = 500):
    if self.ideal_decisions is not None and len(self.ideal_decisions) == count:
      return self.ideal_decisions
    base_delta = 1/(count**(1 / len(self.decisions)))
    print(base_delta)
    starts = [decision.low + base_delta / 2 for decision in self.decisions]
    deltas = [(decision.high - decision.low) * base_delta for decision in self.decisions]
    ideal_decisions = [starts]
    for i in range(len(starts)) :
      temp_pop = []
      for decision in ideal_decisions:
        last_dec = deepcopy(decision)
        while True:
          temp_decision = deepcopy(last_dec)
          temp_decision[i] += deltas[i]
          if temp_decision[i] < self.decisions[i].high:
            temp_pop.append(temp_decision)
            last_dec = temp_pop[-1]
          else :
            break
      ideal_decisions += temp_pop
    self.ideal_decisions = ideal_decisions
    return self.ideal_decisions

  def get_ideal_objectives(self, count=500):
    if self.ideal_objectives is not None:
      return self.ideal_objectives
    self.ideal_objectives = []
    for decisions in self.get_ideal_decisions(count):
      self.ideal_objectives.append(self.evaluate(decisions))
    return self.ideal_objectives

if __name__ == "__main__":
  import algorithms.nsga2.nsga2 as optimizer
  import random
  random.seed(1)
  o = CONSTR()
  nsga2 = optimizer.NSGA2(o, 100)
  goods = nsga2.run()
  nsga2.solution_range(goods)
  x = np.arange(0.1,1.0,0.005)
  c1 = [6 - 9 * pt for pt in x]
  c2 = [9 * pt - 1 for pt in x]
  constraints = [[x, c1], [x, c2]]
  o.plot(goods, constraints)

