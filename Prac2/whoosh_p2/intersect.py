"""
intersect.py
Author: Jorge Pagan Saiz and Jiahao Ye
Last update: 2025-10-14
"""

def intersect(Xmin, Xmax, Ymin, Ymax, West, East, South, North):
    if (Xmin <= East and Xmax >= West and Ymin <= North and Ymax >= South): 
        return True
    else:
        return False