#!/usr/bin/env python

from crossvalidation import nfold_arff
import sys
import subprocess

def dotnode(oname, node):
    _, dots = node.dot()
    open(oname + '.dot', 'w').write('digraph G {\n  ' + '\n  '.join(dots) + '\n}')
    subprocess.call(['dot', '-Tpdf', oname + '.dot', '-o', oname + '.pdf'])

if len(sys.argv) < 3:
    print 'Usage: makedot.py arrffile.arff outname'
    sys.exit(1)

arfff = sys.argv[1]
oname = sys.argv[2]

avg, wrong, final, test, tries, nodes = nfold_arff(arfff, 10)

for i, node, testacc, valacc in zip(range(len(nodes)), nodes, test, tries):
    dotnode('%s_%d' % (oname, i), node)
    print '%d\t%0.5f\t%0.5f' % (i, 1 - testacc / node.size, 1 - valacc)
print 1 - avg

dotnode('%s_full' % oname, final)


# vim: et sw=4 sts=4
