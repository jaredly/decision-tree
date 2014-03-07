#!/usr/bin/env python

from crossvalidation import nfold_arff
import sys

avg, wrong, node = nfold_arff(sys.argv[1], 10)
id, dots = node.dot()

print avg, wrong, id
open(sys.argv[2], 'w').write('digraph G {\n' + '\n  '.join(dots) + '\n}')

# vim: et sw=4 sts=4
