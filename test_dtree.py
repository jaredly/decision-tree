#!/usr/bin/env python

from dtree import Node


def pytest_funcarg__lenses():
    return Node.from_arff('./lenses.arff')


def pytest_funcarg__voting():
    return Node.from_arff('./vote.arff')


def test_info(lenses):
    result = 1.3260875253642983
    assert lenses.information < result + .000001
    assert lenses.information > result - .000001


def test_voting(voting):
    wrong = voting.run()
    assert wrong / voting.size == 0
    print voting.render()
    line = voting.data.loc[0]
    print voting.classify(line), line


''''
def test_full(lenses):
    wrong = lenses.run()
    assert wrong / lenses.size == 0
    print lenses.render()
    line = lenses.data.loc[0]
    print lenses.classify(line), line
    fail
'''

# vim: et sw=4 sts=4
