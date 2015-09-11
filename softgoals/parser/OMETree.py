from __future__ import print_function, division
import sys,os
sys.path.append(os.path.abspath("."))
from softgoals.utilities.library import *
import xml.etree.ElementTree as ET
import json
__author__ = 'george'


def default_ns():
  return {
    "xmi" : "http://www.omg.org/XMI",
    "model" : "http:///edu/toronto/cs/openome_model.ecore",
    "notation" : "http://www.eclipse.org/gmf/runtime/1.0.2/notation"
  }

class Node(O):
  def __init__(self):
    """
    Creates a node which can represent a
    a) Actor
    b) Agent
    c) Position
    d) Role
    e) Hard goal
    f) Soft goal
    g) Task
    h) Resource
    :return:
    """
    O.__init__(self)
    self.id = None
    self.name = None
    self.type = None
    self.value = None
    self.container = None
    self.to_edges = None
    self.from_edges = None

  @staticmethod
  def get_type(key):
    node_map = {
      "edu.toronto.cs.openome_model:Goal"     : "goal",
      "edu.toronto.cs.openome_model:Resource" : "resource",
      "edu.toronto.cs.openome_model:Task"     : "task",
      "edu.toronto.cs.openome_model:Softgoal" : "softgoal",
      "edu.toronto.cs.openome_model:Actor"    : "actor",
      "edu.toronto.cs.openome_model:Agent"    : "agent",
      "edu.toronto.cs.openome_model:Position" : "position",
      "edu.toronto.cs.openome_model:Role"     : "role",
    }
    return node_map.get(key)

  def __hash__(self):
    if not self.id:
      return 0
    return hash(self.id)

  def __eq__(self, other):
    if not self.id or not other.id:
      return False
    return self.id == other.id


class Edge(O):
  def __init__(self):
    """
    Creates an edge which can represent
    a) Dependency
    b) Decomposition
      - AND
      - OR
    c) Contribution
      - Help
      - Hurt
      - Make
      - Break
      - Some Plus
      - Some Minus
      - Conflict
      - Unknown
    :return:
    """
    O.__init__(self)
    self.id = None
    self.type = None
    self.value = None
    self.source = None
    self.target = None

  @staticmethod
  def get_value(key):
    edge_map = {
      # Contributions
      "edu.toronto.cs.openome_model:SomePlusContribution" : "someplus",
      "edu.toronto.cs.openome_model:SomeMinusContribution" : "someminus",
      "edu.toronto.cs.openome_model:HelpContribution" : "help",
      "edu.toronto.cs.openome_model:HurtContribution" : "hurt",
      "edu.toronto.cs.openome_model:MakeContribution" : "make",
      "edu.toronto.cs.openome_model:BreakContribution" : "break",
      "edu.toronto.cs.openome_model:ConflictContribution" : "conflict",
      "edu.toronto.cs.openome_model:UnknownContribution" : "unknown",
      # Decompositions
      "edu.toronto.cs.openome_model:AndDecomposition" : "and",
      "edu.toronto.cs.openome_model:OrDecomposition" : "or",
      #Dependency
      "edu.toronto.cs.openome_model:Dependency" : "dependency"
    }
    return edge_map.get(key)


  def __hash__(self):
    if not self.id:
      return 0
    return hash(self.id)

  def __eq__(self, other):
    if not self.id or not other.id:
      return False
    return self.id == other.id

class Parser(O):

  def __init__(self, src, ns = None):
    """
    Initialize Parser with source file
    :param src:
    :param ns: Namespace with source
    :return:
    """
    O.__init__(self)
    self.src = src
    if not ns:
      ns = default_ns()
    self.ns = ns
    Parser.register_namespace(self.ns)
    self.nodes = None
    self.edges = None

  @staticmethod
  def register_namespace(ns):
    """
    Registers a dictionary of namespace in the parse tree
    :param ns:
    :return:
    """
    for key, val in ns.iteritems():
      ET.register_namespace(key, val)

  def add_node(self, node):
    """
    Add a node to list of nodes for graph
    :param node: Node to be added
    :return:
    """
    if not self.nodes:
      self.nodes = set()
    self.nodes.add(node)

  def add_edge(self, edge):
    """
    Add an edge to set of edges for graph
    :param edge: Edge to be added
    :return:
    """
    if not self.edges:
      self.edges = set()
    self.edges.add(edge)

  def get_attribute(self, element, key):
    """
    Retrieve and attribute from an element of xml
    :param element:
    :param key:
    :return:
    """
    parts = key.split(":")
    if len(parts) == 2:
      val = self.ns[parts[0]]
      if not val:
        raise RuntimeError(key + " not found in namespace.")
      attrib_key = "{" + val + "}" + parts[-1]
    else:
      attrib_key = parts[-1]
    return element.attrib.get(attrib_key, None)

  def parse_node(self, element, container=None):
    """
    Method to parse a node element and create an object
    :param element: Node Element
    :param container: Its parent container
    """
    node = Node()
    node.id = self.get_attribute(element, 'xmi:id')
    node.name = self.get_attribute(element, 'name')
    node.type = Node.get_type(self.get_attribute(element, 'xmi:type'))
    from_edges = []
    froms = self.get_attribute(element, 'contributesFrom')
    if froms:
      from_edges += froms.split(" ")
    froms = self.get_attribute(element, 'dependencyFrom')
    if froms:
      from_edges += froms.split(" ")
    froms = self.get_attribute(element, 'decompositions')
    if froms:
      from_edges += froms.split(" ")
    node.from_edges = from_edges
    # Means - Ends From
    to_edges = []
    tos = self.get_attribute(element, 'contributesTo')
    if tos:
      to_edges += tos.split(" ")
    tos = self.get_attribute(element, 'dependencyTo')
    if tos:
      to_edges += tos.split(" ")
    tos = self.get_attribute(element, 'parentDecompositions')
    if tos:
      to_edges += tos.split(" ")
    node.to_edges = to_edges
    # Means - Ends To
    if container:
      node.container = container
    self.add_node(node)

  def parse_edge(self, element, edge_type):
    """
    Method to parse an edge element and create an object
    :param element: Edge Element
    :param edge_type: type of the edge
    """
    edge = Edge()
    edge.id = self.get_attribute(element, 'xmi:id')
    edge.type = edge_type
    edge.value = Edge.get_value(self.get_attribute(element, 'xmi:type'))
    source = self.get_attribute(element, 'source')
    if not source:
      source = self.get_attribute(element, 'dependencyFrom')
    edge.source = source
    target = self.get_attribute(element, 'target')
    if not target:
      target = self.get_attribute(element, 'dependencyTo')
    edge.target = target
    self.add_edge(edge)

  def parse(self):
    """
    Parse xml tree for the file
    :param ns: Namespace to follow
    :return: XML Tree object
    """
    tree = ET.parse(self.src)
    model = tree.getroot().find("model:Model", self.ns)
    for child in model.findall("intentions"):
      self.parse_node(child)
    for child in model.findall("contributions"):
      self.parse_edge(child, "contribution")
    for child in model.findall("dependencies"):
      self.parse_edge(child, "dependency")
    for child in model.findall("decompositions"):
      self.parse_edge(child, "decompositions")
    for container in model.findall("containers"):
      self.parse_node(container)
      container_id = self.get_attribute(container, 'xmi:id')
      for child in container.findall("intentions"):
        self.parse_node(child, container_id)

  def dump_json(self, filepath = None):
    if filepath:
      f = open(filepath, 'w')
      f.write(self.to_json())
      f.close()
    else:
      print(self.to_json())

  def store_json(self):
    folder_name = "softgoals/models/" + self.src.split("/")[-1].split(".")[0]
    if not os.path.exists(folder_name):
      os.makedirs(folder_name)
    self.parse()
    self.dump_json(folder_name + "/model.json")

  def make_dummy_props(self):
    folder_name = "softgoals/models/" + self.src.split("/")[-1].split(".")[0]
    if not os.path.exists(folder_name):
      os.makedirs(folder_name)
    self.parse()
    goals = {}
    for node in self.nodes:
      goals[node.id] = random.choice([0,1])
    props = {
      "src"   : self.src,
      "goals" : goals
    }
    f = open(folder_name + "/properties.json", 'w')
    f.write(json.dumps(props, indent=4, separators=(',', ': ')))
    f.close()

  @staticmethod
  def filter_nodes(nodes, node_type):
    return [node for node in nodes if node.type == node_type]

  def get_roots(self):
    nodes = []
    for node in self.nodes:
      if not node.from_edges and node.to_edges:
        nodes.append(node)
    return nodes


  @staticmethod
  def from_json(json_obj):
    #TODO implement method to load from json
    pass