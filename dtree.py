#!/usr/bin/env python

from scipy.io.arff import loadarff
from pandas import DataFrame
from math import log
# import pdb


class Node:
    def __init__(self, meta, data, target, rules=(), attrs=None):
        self.meta = meta
        self.data = data
        self.target = target
        self.rules = rules

        self.size = float(len(data))
        _, self.tvalues = meta[target]

        if attrs is None:
            attrs = set(meta.names())
            attrs.remove(target)
        self.attrs = attrs

        self.attr = None
        self.information = 0
        self.children = {}
        self.parts = {}
        if self.size:
            self._calc_information()

    def mydot(self, name, value=None):
        label = 'Size: %(size)d\\nInfo: %(info)0.5f' % {
            'size': self.size,
            'info': self.information
        }
        for part, n in self.parts.items():
            label += '\\n%s: %d' % (part.strip("'"), n)
        if value:
            label = value.strip("'") + '\\n' + label
        if self.attr:
            label += '\\n%s' % self.attr
        return name + ' [shape=box,label="' + label + '"]'

    def dot(self, id=0, value=None):
        '''What do I want?
        - attribute name
        - total number
        - number of each class
        - information
        Returns next_id, lines
        '''
        clines = []
        ids = []
        for v, child in self.children.items():
            id, lines = child.dot(id, v)
            ids.append(id)
            id += 1
            clines += lines
        name = 'node_%d' % id
        lines = []
        lines.append(self.mydot(name, value))
        for ci in ids:
            lines.append(name + ' -> node_%d' % ci)
        return id, lines + clines

    @classmethod
    def from_arff(self, name, target=None):
        data, meta = loadarff(name)
        data = DataFrame(data)
        if target is None:
            target = meta.names()[-1]
        return Node(meta, data, target)

    def validate(self, data):
        wrong = 0
        for i in data.index:
            if not self.amirite(data.loc[i]):
                wrong += 1
        return wrong, wrong / float(len(data))

    ## main functions
    def run(self):
        '''Do the next level of this tree thing'''
        # pdb.set_trace()
        if not self.size:
            return 0
        if not self.information:
            return 0
        if not len(self.attrs):
            return self.size - self.nmajority
        best = None
        for attr in self.attrs:
            gain, nodes = self.gain(attr)
            # print 'gain', gain, attr
            if best is None or gain > best[0]:
                best = gain, nodes, attr
        # print '> best', best[0], best[2]
        self.gained = best[0]
        self.children = dict(best[1])
        self.attr = best[2]
        wrong = 0
        for node in self.children.values():
            wrong += node.run()
        return wrong

    def classify(self, line):
        if not self.information or not self.children:
            return self.majority
        val = line[self.attr]
        node = self.children[val]
        if not node.size:
            return self.majority
        return node.classify(line)

    def amirite(self, line):
        val = self.classify(line)
        return val == line[self.target]

    def render(self, indent=0):
        lines = []
        if self.rules:
            line = '%s = %s (%0.5f) %d' % (
                self.rules[-1][0], self.rules[-1][1],
                self.information, self.size)
            line += '\t\t\t%s' % self.parts
            lines.append(line)
        space = ' ' * (indent * 2)
        for v, node in self.children.items():
            lines.append(v + ' ' + node.render(indent + 1))
        return (' ' * (indent * 2 - 2)) + ('\n' + space).join(lines)

    ## Infternal functions

    def _calc_information(self):
        info = 0
        most = None
        self.parts = {}
        for c in self.tvalues:
            part = self.part(c)
            if most is None or part > most[0]:
                most = part, c
            self.parts[c] = part
            part /= self.size
            info -= part * log(part, 2) if part else 0
        # print 'info', most, info
        self.majority = most[1]
        self.nmajority = most[0]
        self.information = info

    def part(self, targetval):
        '''Get the number of items that are that value for target'''
        return len(self.data[self.data[self.target] == targetval])

    def split(self, attr):
        '''Split on an attribute, yielding new nodes'''
        _, values = self.meta[attr]
        attrs = self.attrs.difference(set((attr,)))
        for v in values + ('?',):
            rules = self.rules + ((attr, v),)
            datas = self.data[self.data[attr] == v]
            yield v, Node(self.meta, datas, self.target, rules, attrs)

    def gain(self, attr):
        '''Calculate the gain of splitting on an attribute'''
        nodes = list(self.split(attr))
        info_attr = 0
        for v, node in nodes:
            info_attr += node.information * node.size / self.size
        return self.information - info_attr, nodes

# vim: et sw=4 sts=4
