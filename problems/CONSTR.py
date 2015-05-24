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
    self.objectives = [Objective("f1",0.1,1), Decision("f2",0,5)]
    self.constraints = [Constraint("g1"), Constraint("g2")]
    self.evals = 0
    self.ideal_decisions = None
    self.ideal_objectives = None
    # TODO make constraint class in problem

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
