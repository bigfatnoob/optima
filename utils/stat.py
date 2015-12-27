"""
Statistics for running an
optimizer on a problem
"""
from __future__ import print_function,division
import sys, os
sys.path.append(os.path.abspath("."))
from lib import *
from measures.hypervolume import HyperVolume
from measures.convergence import convergence
from measures.diversity import diversity
from measures.igd import igd
from plot import *

__author__ = 'panzer'

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
      self.solutions = self.solutions[-self._optimizer.settings.pop_size:]
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
    json_dict["generations"] = gens
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
    json_dict["evals"] = sum(self.gen_evals)
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

  @staticmethod
  def plot_experiment(expt_id):
    base_dir = "results/%s"%expt_id
    problems = get_subdirectories(base_dir)
    for problem in problems:
      problem_dir = base_dir + "/%s"%problem
      algos =  get_subdirectories(problem_dir)
      convs, divs, igds, hvs, evals = {}, {}, {}, {}, {}
      for algo in algos:
        algo_dir = problem_dir + "/%s"%algo
        reps = ls(algo_dir)
        conv_list, div_list, igd_list, hv_list, eval_list = [], [], [], [], []
        for rep in reps:
          rep_file = algo_dir + "/%s"%rep
          json_data = get_json(rep_file)
          conv_val = json_data.get("convergence", None)
          if conv_val : conv_list.append(conv_val)
          div_val = json_data.get("spread", None)
          if div_val : div_list.append(div_val)
          igd_val = json_data.get("igd", None)
          if igd_val : igd_list.append(igd_val)
          hv_val = json_data.get("hyperVolume", None)
          if hv_val : hv_list.append(hv_val)
          eval_val = json_data.get("evals", None)
          if eval_val: eval_list.append(eval_val)
        if conv_list:
          mean, iqr = mean_iqr(conv_list)
          convs[algo] = (mean, iqr)
        if div_list:
          mean, iqr = mean_iqr(div_list)
          divs[algo] = (mean, iqr)
        if igd_list:
          mean, iqr = mean_iqr(igd_list)
          igds[algo] = (mean, iqr)
        if hv_list:
          mean, iqr = mean_iqr(hv_list)
          hvs[algo] = (mean, iqr)
        if eval_list:
          mean, iqr = mean_iqr(eval_list)
          evals[algo] = (mean, iqr)
      bar_plot(convs, "Convergence", problem, problem_dir)
      bar_plot(divs, "Diversity", problem, problem_dir)
      bar_plot(igds, "IGD", problem, problem_dir)
      bar_plot(hvs, "Hyper_Volume", problem, problem_dir)
      bar_plot(evals, "Evaluations", problem, problem_dir, format_unit="%d")

if __name__ == "__main__":
  Stat.plot_experiment("temp")
