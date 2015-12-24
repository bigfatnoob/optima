from __future__ import print_function, division
import sys, os
sys.path.append(os.path.abspath("."))
from configs import REPEATS

# Problems
from problems.dtlz.dtlz1 import DTLZ1
from problems.dtlz.dtlz2 import DTLZ2
from problems.dtlz.dtlz3 import DTLZ3
from problems.dtlz.dtlz4 import DTLZ4
from problems.dtlz.dtlz5 import DTLZ5
from problems.dtlz.dtlz6 import DTLZ6
from problems.dtlz.dtlz7 import DTLZ7

# Optimizers
from algorithms.nsga3.nsga3 import NSGA3
from algorithms.nsga2.nsga2 import NSGA2
from algorithms.gale.gale import GALE
from algorithms.de.de import DE
from algorithms.moead.moea_de import MOEA_DE
from algorithms.moead.moea_tch import MOEA_TCH
from algorithms.moead.moea_pbi import MOEA_PBI

__author__ = 'panzer'

problems = [
  DTLZ1(3),
  #DTLZ1(5)
]

algorithms = [
  NSGA3,
  NSGA2,
  DE,
  GALE,
  MOEA_DE,
  MOEA_PBI,
  MOEA_TCH,
]


for problem in problems:
  print(problem.title())
  for i in range(1):
    for algo in algorithms:
      print(algo.__name__)
      opt = algo(problem)
      print(opt.settings)
      # exit()
      # opt.run()
      # opt.stat.to_json(i+1)
      # print()
      # Store and process solutions
