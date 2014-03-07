#!/usr/bin/env python

from scipy.io.arff import loadarff
import numpy as np
from dtree import Node
from pandas import DataFrame, concat


def nfold_arff(fname, num, target=None):
    data, meta = loadarff(fname)
    if target is None:
        target = meta.names()[-1]
    data = DataFrame(data)
    return nfold(meta, data, target, num)


def nfold(meta, data, target, num=10):
    total = len(data)
    validate = total // num

    ix = np.array(data.index)
    np.random.shuffle(ix)

    test = []
    tries = []
    for i in range(num):
        print 'val with', validate, total
        first = ix[:i*validate]
        second = ix[(i+1)*validate:]
        training = concat([data.loc[first], data.loc[second]])
        validating = data.loc[ix[i*validate:(i+1)*validate]]
        node = Node(meta, training, target)
        test.append(node.run())
        tries.append(node.validate(validating)[1])
    avg = sum(tries)/len(tries)
    print avg
    node = Node(meta, data, target)
    wrong = node.run()
    return avg, wrong, node


# vim: et sw=4 sts=4
