from __future__ import print_function,division
import sys, os
sys.path.append(os.path.abspath("."))
import numpy as np
import matplotlib.pyplot as plt

__author__ = 'panzer'

COLORS = ["blue", "green", "red", "cyan", "magenta", "yellow", "saddlebrown", "orange", "darkgreen"]

def bar_plot(data, y_label, title, path, format_unit="%0.4f"):
  if not data:
    return
  fig, ax = plt.subplots()
  def auto_label(bars):
    for bar in bars:
      height = bar.get_height()
      ax.text(bar.get_x() + bar.get_width()/2., 1.05*height,
                format_unit % height,
                ha='center', va='bottom')

  means = []
  iqrs = []
  labels = data.keys()
  for label in labels:
    mean, iqr = data[label]
    means.append(mean)
    iqrs.append(iqr)
  indices = np.arange(len(labels))
  rects = ax.bar(indices, means, yerr=iqrs, color=COLORS[:len(labels)])
  width = rects[0].get_width()/2
  ax.set_ylabel(y_label)
  ax.set_title(title)
  ax.set_xticks(indices + width)
  ax.set_xticklabels(labels)
  auto_label(rects)
  plt.savefig(path+"/%s.png"%y_label)



