__author__ = 'george'
import sys
sys.path.append(".")
from softgoals.parser.OMETree import *
from problems.problem import *

def test_ome_tree():
  parser = Parser('../softgoals/GMRepo/CMA12/bCMS_SR_bCMS_AuthenticationVariation.ood')
  parser.parse()
  parser.dump_json()
  parser.make_dummy_props()

if __name__ == "__main__":
  test_ome_tree()

