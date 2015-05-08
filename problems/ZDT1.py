from problem import *
from math import sqrt

"""
No of Decisions = n = 30.
Range of each imput = [0,1]
Objectives:
  f1(x) = x1
  f2(x) = g(x)(1 - (x1/g(x))**0.5 )
  where g(x) = 1 + 9*(sum_(i = 2 to n) x_i)/ n-1
"""
class ZDT1(Problem):
  def __init__(i):
    i.name = "ZDT1"
    i.desc = "No of Decisions = n = 30. \n \
              Range of each input = [0,1] \n \
              Objectives: \n \
              f1(x) = x1 \n \
              f2(x) = g(x)(1 - (x1/g(x))**0.5 ) \n \
              where g(x) = 1 + 9*(sum_(i = 2 to n) x_i)/ n-1"
    i.decisions = [Decision("x"+str(index+1),0,1) for index in range(30)]
    i.objectives = [Objective("f1", True), Objective("f2", True)]

  def evaluate(i, decisions = None):
    if decisions:
      for index, decision in enumerate(i.decisions):
        decision.value = decisions[index]
    decisions = [decision.value for decision in i.decisions]
    g  = 1 + 9 * sum(decisions[1:]) / (len(decisions)-1)
    i.objectives[0].value = decisions[0]
    i.objectives[1].value = g * (1 - sqrt(decisions[0]/g))
    return [i.objectives[0].value, i.objectives[1].value]
