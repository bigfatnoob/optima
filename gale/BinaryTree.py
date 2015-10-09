__author__ = 'panzer'
import sys, os
sys.path.append(os.path.abspath("."))
from utils.lib import O

class BinaryTree(O):
  def __init__(self):
    """
    Points to root of the tree and number of children under it
    :return:
    """
    O.__init__(self)
    self.n = 0
    self.left = None
    self.right = None

  def is_leaf(self):
    """
    Check if a not is a leaf
    :return: True/False
    """
    return not self.left and not self.right

  def leaves(self):
    """
    Return all the leaf nodes
    :return: Array of nodes
    """
    if self.nodes() is None:
      return None
    return [node for node in self.nodes() if node.is_leaf()]

  def pruned_leaves(self):
    """
    Returns all the pruned leaves
    in a tree
    :return: Array of nodes
    """
    if self.nodes() is None:
      return None
    return [node for node in self.nodes() if node.is_leaf() and node.abort]

  def nonpruned_leaves(self):
    """
    Returns all the pruned leaves
    in a tree
    :return: Array of nodes
    """
    if self.nodes() is None:
      return None
    return [node for node in self.nodes() if node.is_leaf() and not node.abort]

  def nodes(self, visited = None):
    """
    Returns all the nodes in a tree as an array
    :param visited:
    :return:
    """
    if not visited: visited = []
    visited += [self]
    if self.left:
      self.left.nodes(visited)
    if self.right:
      self.right.nodes(visited)
    return visited




