import math

def mean(xs): return sum(xs) / len(xs)
def std(xs): return math.sqrt(sum((x - mean(xs))**2 for x in xs) / (len(xs)-1))
def cv(xs): return std(xs) / mean(xs) if mean(xs) else 999
def min_(xs): return min(4.0,math.log1p(xs))