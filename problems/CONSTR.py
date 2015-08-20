from __future__ import print_function, division
from problem import *


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

  def evaluateConstraints(self, decisions = None):
    status = False
    offset = 0
    if decisions:
      for index, decision in enumerate(self.decisions):
        decision.value = decisions[index]
    decisions = [decision.value for decision in self.decisions]
    self.constraints[0].value = decisions[1] + 9*decisions[0] - 6
    if self.constraints[0].value < 0:
      offset += abs(self.constraints[0].value)
      status = True
    self.constraints[1].value = - decisions[1] + 9*decisions[0] - 1
    if self.constraints[1].value < 0:
      offset += abs(self.constraints[1].value)
      status = True
    return offset, status


  def evaluate(self, decisions=None):
    if decisions:
      for index, decision in enumerate(self.decisions):
        decision.value = decisions[index]
    decisions = [decision.value for decision in self.decisions]
    self.objectives[0].value = decisions[0]
    self.objectives[1].value = (1+decisions[1])/decisions[0]
    return [self.objectives[0].value, self.objectives[1].value]


  def get_ideal_decisions(self, count = 500):
    if self.ideal_decisions is not None and len(self.ideal_decisions) == count:
      return self.ideal_decisions
    start = 1/(2*500)
    delta = 1/500
    self.ideal_decisions = []
    for i in range(count):
      self.ideal_decisions.append([start + i*delta]+[0]*29)
    return self.ideal_decisions

  def get_ideal_objectives(self, count=500):
    if self.ideal_objectives is not None:
      return self.ideal_objectives
    one_start = 1/(2*500)
    two_start = 1- (1/(2*500))
    delta = 1/500
    self.ideal_objectives = []
    for i in range(count):
      self.ideal_objectives.append([one_start+i*delta, two_start-i*delta])
    return self.ideal_objectives

if __name__ == "__main__":
  import nsga2.NSGA2 as optimizer
  import random
  random.seed(1)
  o = CONSTR()
  o.populate(optimizer.settings().pop_size)
  nsga2 = optimizer.NSGA2(o, 500)
  # goods, fronts = nsga2.generate()
  # print(nsga2.convergence(goods))
  # print(nsga2.diversity(fronts[0]))
  # nsga2.solution_range(goods)
  o.plot()

