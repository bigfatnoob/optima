__author__ = 'george'
import sys
sys.path.append(".")
from softgoals.parser.OMETree import *
from softgoals.models.model import Model

def test_ome_tree():
  model = Model('../softgoals/GMRepo/CMA12/bCMS_SR_bCMS_exceptional.ood')
  print(model.roots)
  print(model.generate())

if __name__ == "__main__":
  test_ome_tree()

