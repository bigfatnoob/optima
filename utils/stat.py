"""
Statistics for running an
optimizer on a problem
"""
from __future__ import print_function,division
import sys, os, json
sys.path.append(os.path.abspath("."))
__author__ = 'panzer'
from lib import *
from measures.hypervolume import HyperVolume
from measures.convergence import convergence
from measures.diversity import diversity
from measures.igd import igd

class Stat(O):
  def __init__(self, problem, optimizer):
    """
    Initialize the statistic object
    :param problem: Instance of problem
    :param optimizer: Instance of optimizer
    :return:
    Stat object that contains
    - problem
    - generations: population for each generation
    - evals: total number of evaluations
    - runtime: total runtime of optimization
    - IGD: Inverse Generational Distance for each generation
    - spread: Spread for each generation
    - hyper_volume: Hyper-volume for each generation
    - problem_name: Name of the problem
    - decisions: Decisions of the problem
    - objectives: Objectives of the problem
    - optimizer: Instance of the optimizer
    - gen_evals: Evals each generation
    - solutions: Final set of solutions
    """
    O.__init__(self)
    self._problem = problem
    self.generations = None
    self.evals = 0
    self.runtime = None
    self.IGD = None
    self.spread = None
    self.hyper_volume = None
    self.problem_name = problem.name
    self.decisions = problem.decisions
    self.objectives = problem.objectives
    self._optimizer = optimizer
    self.solutions = None
    self.gen_evals = None

  def update(self, population, evals = 0):
    if self.generations is None:
      self.generations = []
    clones = []
    for one in population:
      clones.append(one.clone())
    self.generations.append(clones)
    self.evals += evals

  def update_solutions(self):
    if self.solutions:
      return
    self.solutions = []
    if not self._optimizer.is_pareto:
      # Exception for methods like gale that does
      # not generate solutions on the pareto front.
      for generation in self.generations:
        self.solutions.extend(generation)
    else:
      self.solutions = self.generations[-1]

  def to_json(self, repeat=1):
    """
    Experiment repeat number
    :param repeat:
    :return:
    """
    args = sys.argv
    if len(args) < 2:
      print("Experiment ID not provided")
      exit()
    json_dict = {}
    gens = []
    for gen in self.generations:
      pts = []
      for point in gen:
        pt = dict()
        pt["id"] = point.id
        pt["decisions"] = point.decisions
        pt["objectives"] = point.objectives
        pts.append(pt)
      gens.append(pts)
    #json_dict["generations"] = gens
    json_dict["decisions"] = [dec.__dict__ for dec in self.decisions]
    json_dict["objectives"] = [obj.__dict__ for obj in self.objectives]
    self.update_solutions()
    solutions=[]
    for point in self.solutions:
      solutions.append({
        "id" : point.id,
        "decisions" : point.decisions,
        "objectives" : point.objectives
      })
    json_dict["solutions"] = solutions
    json_dict["gen_evals"] = self.gen_evals
    objs = [one.objectives for one in self.solutions]
    true_pf = self._problem.get_pareto_front()
    if true_pf:
      json_dict["convergence"] = convergence(objs, true_pf)
      json_dict["spread"] = diversity(objs, true_pf)
      json_dict["igd"] = igd(objs, true_pf)
    reference = HyperVolume.get_reference_point(self._problem, objs)
    json_dict["hyperVolume"] = HyperVolume(reference).compute(objs)


    expt_id = sys.argv[1]
    problem_name = self._problem.name + "_d" + str(len(self.decisions)) + "_o" + str(len(self.objectives))
    folder = "results/%s/%s/%s/"%(expt_id, problem_name, self._optimizer.name)
    mkdir(folder)
    file_name = folder + "rep_%d.json"%repeat
    with open(file_name, "w") as outfile:
      json.dump(json_dict, outfile, indent=4)