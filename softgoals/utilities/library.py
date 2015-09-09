from __future__ import division, print_function
import random, json

"""
Default class which everything extends.
"""
class O():
  def __init__(self,**d): self.has().update(**d)
  def has(self): return self.__dict__
  def update(self,**d): self.has().update(d); return self
  def __repr__(self)   :
    show=[':%s %s' % (k,self.has()[k])
      for k in sorted(self.has().keys() )
      if k[0] is not "_"]
    txt = ' '.join(show)
    if len(txt) > 60:
      show=map(lambda x: '\t'+x+'\n',show)
    return '{'+' '.join(show)+'}'
  def __getitem__(self, item):
    return self.has().get(item)
  def to_json(self):
    def dflt(obj):
      if isinstance(obj, set): return list(obj)
      return obj.__dict__
    return json.dumps(self, default=dflt, sort_keys=True, indent=4)

"""
An accumulator for reporting on numbers.
"""
class N():
  "Add/delete counts of numbers."
  def __init__(self,inits=[]):
    self.zero()
    map(self.__iadd__,inits)
  def zero(self):
    self.n = self.mu = self.m2 = 0
    self.cache= Cache()
  def sd(self)  :
    if self.n < 2:
      return 0
    else:
      return (max(0,self.m2)/(self.n - 1))**0.5
  def __iadd__(self,x):
    self.cache += x
    self.n     += 1
    delta       = x - self.mu
    self.mu    += delta/(1.0*self.n)
    self.m2    += delta*(x - self.mu)
    return self
  def __isub__(self,x):
    self.cache = Cache()
    if self.n < 2: return self.zero()
    self.n  -= 1
    delta = x - self.mu
    self.mu -= delta/(1.0*self.n)
    self.m2 -= delta*(x - self.mu)
    return self

CACHE_SIZE=128
class Cache:
  "Keep a random sample of stuff seen so far."
  def __init__(self, inits=[]):
    self.all,self.n,self._has = [],0,None
    map(self.__iadd__,inits)
  def __iadd__(self,x):
    self.n += 1
    if len(self.all) < CACHE_SIZE: # if not full
      self._has = None
      self.all += [x]               # then add
    else: # otherwise, maybe replace an old item
      if random.random() <= CACHE_SIZE/self.n:
        self._has=None
        self.all[int(random.random()*CACHE_SIZE)] = x
    return self
  def has(self):
    if self._has == None:
      lst  = sorted(self.all)
      med,iqr = medianIQR(lst,ordered=True)
      self._has = O(
        median = med,      iqr = iqr,
        lo     = self.all[0], hi  = self.all[-1])
    return self._has

def medianIQR(lst, ordered=False):
  if not ordered:
    lst = sorted(lst)
  n = len(lst)
  q = n//4
  iqr = lst[q*3] - lst[q]
  if n % 2:
    return lst[q*2],iqr
  else:
    p = max(0,q-1)
    return (lst[p] + lst[q]) * 0.5,iqr