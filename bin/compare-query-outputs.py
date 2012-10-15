#!/usr/bin/env python

### This script compares the output of a plaintext run and a
### run from monomi, and checks if they deliver the same results

import math
import re
import sys

N_ROW_REGEX=re.compile(r'\(\d+ rows\)')
def plaintext_row_ignore(row):
  '''returns true if row should be ignored'''
  if row.startswith("Timing is on."):
    return True
  if row.startswith("Time:"):
    return True
  if N_ROW_REGEX.match(row):
    return True
  return False

TYPE_ROW_REGEX=re.compile(r'TYPE_[A-Z]+:')
def monomi_row_ignore(row):
  '''returns true if row should be ignored'''
  if N_ROW_REGEX.match(row):
    return True
  if TYPE_ROW_REGEX.match(row):
    return True
  return False

FIXED_PT_REGEX=re.compile(r'-?[0-9]+\.[0-9]*')
INT_REGEX=re.compile(r'-?[1-9][0-9]*')
def heuristic_parse(elem):
  if FIXED_PT_REGEX.match(elem):
    return float(elem)
  if INT_REGEX.match(elem):
    return int(elem)
  return elem

SEP='|'
def ingest_plaintext(filename):
  with open(filename, 'r') as fp:
    i = 0
    rows = []
    for line in fp.readlines():
      line = line.strip()
      if not line or plaintext_row_ignore(line):
        continue
      if i >= 2: # skip headers
        rows.append([heuristic_parse(x.strip()) for x in line.split(SEP)])
      i += 1
    return rows

def ingest_monomi(filename):
  with open(filename, 'r') as fp:
    rows = []
    for line in fp.readlines():
      line = line.strip()
      if not line or monomi_row_ignore(line):
        continue
      rows.append([heuristic_parse(x.strip()) for x in line.split(SEP)])
    return rows

def diff_outputs(lhs, rhs):
  '''returns either (True, None), or (False, message)'''
  if len(lhs) != len(rhs):
    return (False, 'output lengths not the same (lhs = %d, rhs = %d)' % (len(lhs), len(rhs)))
  for (a, b) in zip(lhs, rhs):
    if len(a) != len(b):
      return (False, 'number columns not the same (lhs = %d, rhs = %d)' % (len(a), len(b)))
    for (x, y) in zip(a, b):
      if type(x) != type(y):
        return (False, 'types do not match up (lhs = %s, rhs = %s)' % (x, y))
      if isinstance(x, float):
        # allow lots of slack
        if math.fabs(x - y) >= 1e-2:
          return (False, 'values do not match up in row (lhs_value = %s, rhs_value = %s) [lhs = %s, rhs = %s]' % (x, y, a, b))
      else:
        if x != y:
          return (False, 'values do not match up in row (lhs_value = %s, rhs_value = %s) [lhs = %s, rhs = %s]' % (x, y, a, b))
  return (True, None)

if __name__ == '__main__':
  if len(sys.argv[1:]) != 2:
    print >>sys.stderr, '[Usage]: %s <plaintext> <monomi>' % sys.argv[0]
    sys.exit(1)
  (pf, mf) = sys.argv[1:]
  pr = ingest_plaintext(pf)
  mr = ingest_monomi(mf)
  (ret, msg) = diff_outputs(pr, mr)
  if not ret:
    print msg
    sys.exit(2)
