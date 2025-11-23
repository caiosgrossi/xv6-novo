#!/usr/bin/env python3
"""
Simple plotting helper for lottery scheduler CSV output.
Usage:
  python3 tools/plot_lottery.py data.csv
Expects CSV with header: sample,pidA,pidB,pidC
"""
import sys
import csv
import matplotlib.pyplot as plt

if len(sys.argv) < 2:
  print("Usage: plot_lottery.py data.csv [out.png]")
  sys.exit(1)

fn = sys.argv[1]
outpng = sys.argv[2] if len(sys.argv) >= 3 else None
S = []
A = []
B = []
C = []
with open(fn) as f:
  r = csv.reader(f)
  # skip any prefix lines until we find the header starting with 'sample'
  header = None
  for row in r:
    if not row:
      continue
    if row[0].strip().lower().startswith('sample'):
      header = row
      break
    # ignore lines like 'pids: ...'
  if header is None:
    # file might have no header; rewind and parse numeric rows
    f.seek(0)
    r = csv.reader(f)
  else:
    # continue with remaining rows from the iterator `r`
    pass

  for row in r:
    if not row:
      continue
    if row[0].strip().lower().startswith('pids'):
      continue
    if row[0].strip().lower() == 'sample':
      # skip header line if repeated
      continue
    try:
      s = int(row[0])
      a = int(row[1])
      b = int(row[2])
      c = int(row[3])
    except Exception:
      # skip malformed rows
      continue
    S.append(s)
    A.append(a)
    B.append(b)
    C.append(c)

# Raw ticks plot
fig, axs = plt.subplots(2, 1, figsize=(10, 8))
axs[0].plot(S, A, label='procA')
axs[0].plot(S, B, label='procB')
axs[0].plot(S, C, label='procC')
axs[0].set_xlabel('sample')
axs[0].set_ylabel('ticks')
axs[0].legend()
axs[0].set_title('Lottery Scheduler: ticks over time (raw)')
axs[0].grid(True)

# Normalized proportions plot
total = [a+b+c for a,b,c in zip(A,B,C)]
propA = [a/t if t>0 else 0 for a,t in zip(A,total)]
propB = [b/t if t>0 else 0 for b,t in zip(B,total)]
propC = [c/t if t>0 else 0 for c,t in zip(C,total)]
axs[1].plot(S, propA, label='procA')
axs[1].plot(S, propB, label='procB')
axs[1].plot(S, propC, label='procC')
axs[1].set_xlabel('sample')
axs[1].set_ylabel('proportion')
axs[1].legend()
axs[1].set_title('Lottery Scheduler: normalized proportions over time')
axs[1].grid(True)

plt.tight_layout()
if outpng:
  plt.savefig(outpng, dpi=200)
  print(f"Saved plot to {outpng}")
else:
  plt.show()
