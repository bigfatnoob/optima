from __future__ import print_function, division
import sys, os
sys.path.append(os.path.abspath("."))
from configs import REPEATS

from utils.stat import Stat

# Problems
from problems.dtlz.dtlz1 import DTLZ1
from problems.dtlz.dtlz2 import DTLZ2
from problems.dtlz.dtlz3 import DTLZ3
from problems.dtlz.dtlz4 import DTLZ4
from problems.dtlz.dtlz5 import DTLZ5
from problems.dtlz.dtlz6 import DTLZ6
from problems.dtlz.dtlz7 import DTLZ7
from problems.zdt.zdt1 import ZDT1

# Optimizers
from algorithms.nsga3.nsga3 import NSGA3
from algorithms.nsga2.nsga2 import NSGA2
from algorithms.gale.gale import GALE
from algorithms.de.de import DE
from algorithms.moead.moea_de import MOEA_DE
from algorithms.moead.moea_tch import MOEA_TCH
from algorithms.moead.moea_pbi import MOEA_PBI
from algorithms.spea2.spea2 import SPEA2

__author__ = 'panzer'

problems = [
  #DTLZ1(3),
  #DTLZ1(5),
  ZDT1(),
]

algorithms = [
  #NSGA3,
  #NSGA2,
  #DE,
  #GALE,
  #MOEA_DE,
  #MOEA_PBI,
  #MOEA_TCH,
  SPEA2,
]

expt_id = sys.argv[1]
for problem in problems:
  print(problem.title())
  for i in range(1):
  #for i in range(REPEATS):
    for algo in algorithms:
      print(algo.__name__)
      opt = algo(problem)
      opt.run()
      opt.stat.to_json(i+1)
      print()
      # Store and process solutions
Stat.plot_experiment(expt_id)