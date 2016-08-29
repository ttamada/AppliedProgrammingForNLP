#!/usr/bin/python

import sys

with open(sys.argv[1]) as f:
    lines1 = f.readlines()
with open(sys.argv[2]) as f:
    lines2 = f.readlines()


i = 0
eq = 0
diff = 0
for line in lines1:
    if line == lines2[i]:
        eq += 1
    else:
        diff += 1
    i += 1

print "Equal: "+str(eq)+", Different: "+str(diff)