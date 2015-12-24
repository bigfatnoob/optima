#    Original Author : Simon Wessing
#    From : TU Dortmund University
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function,division
import sys, os
sys.path.append(os.path.abspath("."))
__author__ = 'george'

def gt(a, b): return a>b

def lt(a, b): return a<b

def gte(a, b): return a>=b

def lte(a, b): return a<=b

class HyperVolume:
  """
  Hypervolume computation based on variant 3 of the algorithm in the paper:
  C. M. Fonseca, L. Paquete, and M. Lopez-Ibanez. An improved dimension-sweep
  algorithm for the hypervolume indicator. In IEEE Congress on Evolutionary
  Computation, pages 1157-1163, Vancouver, Canada, July 2006.
  Minimization is implicitly assumed here!
  """
  def __init__(self, reference):
    self.reference = reference
    self.list = None

  def compute(self, front):
    """
    Returns the hyper-volume that is dominated by a non-dominated front.
    Before the HV computation, front and reference point are translated, so
    that the reference point is [0, ..., 0].
    :param front:
    :return: hyper-volume value
    """
    def weak_dominate(one, two):
      """
      Check if one dominates two
      :param one: First set of objectives
      :param two: Second set of objectives
      :return:
      """
      for i in xrange(len(one)):
        if one[i] > two[i]:
          return False
      return True

    relevants = []
    reference = self.reference
    d = len(reference)
    for point in front:
      if weak_dominate(point, reference): relevants.append(point)

    if any(reference):
      for j in xrange(len(relevants)):
        relevants[j] = [relevants[j][i] - reference[i] for i in xrange(d)]
    self.pre_process(relevants)
    bounds = [-1.0e308]*d
    return self.recurse(d-1, len(relevants), bounds)

  def recurse(self, d, length, bounds):
    """
    Recursive call for hyper volume calculation.
    In contrast to the paper, the code assumes that the reference point
    is [0, ..., 0]. This allows the avoidance of a few operations.
    :param d: Dimension Index
    :param length: Number of relevant points
    :param bounds: Bounding Values
    :return: hyper-volume
    """
    hvol = 0.0
    sentinel = self.list.sentinel
    if length == 0:
      return hvol
    elif d == 0:
      # Single Dimension
      return -sentinel.next[0].value[0]
    elif d == 1:
      # 2 dimensional problem
      q = sentinel.next[1]
      h = q.value[0]
      p = q.next[1]
      while p is not sentinel:
        p_value = p.value
        hvol += h * (q.value[1] - p_value[1])
        if p_value[0] < h:
          h = p_value[0]
        q = p
        p = q.next[1]
      hvol += h * q.value[1]
      return hvol
    else:
      remove = MultiList.remove
      reinsert = MultiList.reinsert
      recurse = self.recurse
      p = sentinel
      q = p.prev[d]
      while q.value is not None:
        if q.ignore < d:
          q.ignore = 0
        q = q.prev[d]
      q = p.prev[d]
      while length > 1 and (q.value[d] > bounds[d] or q.prev[d].value[d] >= bounds[d]):
        p = q
        remove(p, d, bounds)
        q = p.prev[d]
        length -= 1
      q_area = q.area
      q_value = q.value
      q_prev_d = q.prev[d]
      if length > 1:
        hvol = q_prev_d.volume[d] + q_prev_d.area[d] * (q_value[d] - q_prev_d.value[d])
      else:
        q_area[0] = 1
        q_area[1:d+1] = [q_area[i] * -q_value[i] for i in xrange(d)]
      q.volume[d] = hvol
      if q.ignore >= d:
        q_area[d] = q_prev_d.area[d]
      else:
        q_area[d] = recurse(d-1, length, bounds)
        if q_area[d] < q_prev_d.area[d]:
          q.ignore = d
      while p is not sentinel:
        p_value_d = p.value[d]
        hvol += q.area[d] * (p_value_d - q.value[d])
        bounds[d] = p_value_d
        reinsert(p, d, bounds)
        length += 1
        q = p
        p = p.next[d]
        q.volume[d] = hvol
        if q.ignore >= d:
          q.area[d] = q.prev[d].area[d]
        else:
          q.area[d] = recurse(d-1, length, bounds)
          if q.area[d] <= q.prev[d].area[d]:
            q.ignore = d
      hvol - q.area[d] * q.value[d]
      return hvol

  def pre_process(self, front):
    d = len(self.reference)
    multi_list = MultiList(d)
    nodes = [MultiList.Node(d, point) for point in front]
    for i in xrange(d):
      HyperVolume.dimension_sort(nodes, i)
      multi_list.extend(nodes, i)
    self.list = multi_list

  @staticmethod
  def dimension_sort(nodes, i):
    decorated = [(node.value[i], node) for node in nodes]
    decorated.sort()
    nodes[:] = [node for (_, node) in decorated]

  @staticmethod
  def get_reference_point(problem, points):
    reference = [-sys.maxint if obj.to_minimize else sys.maxint for obj in problem.objectives]
    for point in points:
      for i, obj in enumerate(problem.objectives):
        if obj.to_minimize:
          if point[i] > reference[i]:
            reference[i] = point[i]
        else:
          if point[i] < reference[i]:
            reference[i] = point[i]
    for i, obj in enumerate(problem.objectives):
      if obj.to_minimize:
        reference[i] += 1
      else:
        reference[i] -= 1
    return reference


class MultiList:
  """A special data structure needed by FonsecaHyperVolume.

  It consists of several doubly linked lists that share common nodes. So,
  every node has multiple predecessors and successors, one in every list.
  """
  class Node:
    def __init__(self, count, value=None):
      self.value = value
      self.next = [None] * count
      self.prev = [None] * count
      self.ignore = 0
      self.area = [0.0] * count
      self.volume = [0.0] * count

    def __str__(self):
      return str(self.value)

  def __init__(self, count):
    """
    Build 'count' number of doubly linked lists.
    :param count: Number of doubly linked lists
    :return:
    """
    self.count = count
    self.sentinel = MultiList.Node(count)
    self.sentinel.next = [self.sentinel] * count
    self.sentinel.prev = [self.sentinel] * count

  def __str__(self):
    strings = []
    for i in xrange(self.count):
      current_list = []
      node = self.sentinel.next[i]
      while node != self.sentinel:
        current_list.append(str(node))
        node = node.next[i]
      strings.append(str(current_list))
    string_repr = ""
    for string in strings:
      string_repr += string + "\n"
    return string_repr

  def __len__(self):
    """
    Returns the number of lists that are included in this MultiList.
    """
    return self.count

  def size(self, index):
    """
    Returns the length of the i-th list.
    """
    length = 0
    sentinel = self.sentinel
    node = sentinel.next[index]
    while node != sentinel:
      length += 1
      node = node.next[index]
    return length

  def append(self, node, index):
    """
    Appends a node to the end of the list at the given index.
    :param node: Node to be appended
    :param index: Index of list to be appended into
    """
    penultimate = self.sentinel.prev[index]
    node.next[index] = self.sentinel
    node.prev[index] = penultimate
    self.sentinel.prev[index] = node
    penultimate.next[index] = node

  def extend(self, nodes, index):
    """
    Extend the list at the given index with nodes
    :param nodes: Nodes to be appended
    :param index: Index of list to be extended
    """
    sentinel = self.sentinel
    for node in nodes:
      penultimate = sentinel.prev[index]
      node.next[index] = sentinel
      node.prev[index] = penultimate
      sentinel.prev[index] = node
      penultimate.next[index]= node

  @staticmethod
  def remove(node, index, bounds):
    """
    Removes and returns node from all lists in [0, index]
    :param node: Node to be removed
    :param index: Index to be removed till
    :param bounds:
    :return: Removed node
    """
    for i in xrange(index):
      pred = node.prev[i]
      succ = node.next[i]
      pred.next[i] = succ
      succ.prev[i] = pred
      if bounds[i] > node.value[i]:
        bounds[i] = node.value[i]
    return node

  @staticmethod
  def reinsert(node, index, bounds):
    """
    Inserts 'node' at the position it had in all lists in [0, 'index'[
    before it was removed. This method assumes that the next and previous
    nodes of the node that is reinserted are in the list.
    :param node: Node to be reinserted
    :param index: Index to be reinserted at
    :param bounds:
    """
    for i in xrange(index):
      node.prev[i].next[i] = node
      node.next[i].prev[i] = node
      if bounds[i] > node.value[i]:
        bounds[i] = node.value[i]


def _test():
  reference_point = [2,2,2]
  hv = HyperVolume(reference_point)
  front = [[1,0,1], [0,1,0]]
  print(hv.compute(front))

if __name__ == "__main__":
  _test()
