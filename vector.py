#!/usr/bin/env python

__OOGUEVERSION__ = 1593122571

import math

def add( a, b ):
  """a + b"""
  return (a[0] + b[0], a[1] + b[1], a[2] + b[2])

def subtract( a, b ):
  """a-b"""
  return (a[0] - b[0], a[1] - b[1], a[2] - b[2])

def length( a ):
  return math.fabs( math.sqrt( a[0] * a[0] + a[1] * a[1] + a[2] * a[2] ) )
