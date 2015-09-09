__author__ = 'george'
import sys,os
sys.path.append(os.path.abspath("."))
from problems.problem import *

# TODO implement model here based on model.json based on the architecture in optima/utils/problem.py

class Model(Problem):
  def __init__(self, src):
    Problem.__init__(self)
    self.name = 'bCMS_SR_bCMS_AuthenticationVariation'
    self.src = src
    self.properties = 'properties.json'

f = open('properties.json', 'r')
txt = f.read()
f.close()
print(txt)


