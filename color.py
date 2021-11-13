import os
import csv
import unittest
import datetime
import genetic
import webbrowser

def load_data(fileName):
    with open(fileName, mode = 'r') as infile:
        reader = csv.reader(infile)
        lookup = {row[0]: row[1].split(';') for row in reader if row}
    return lookup

class Rule:
    def __init__(self, node, adjacent):
        if node < adjacent:
            node, adjacent = adjacent, node
        self.Node = node
        self.Adjacent = adjacent

    def __eq__(self, other):
        return self.Node == other.Node and \
            self.Adjacent == other.Node

    def __hash__(self):
        return hash(self.Node) * 397 ^ hash(self.Adjacent)

    def __str__(self):
        return self.Node + " -> " + self.Adjacent

    def IsValid(self, genes, nodeIndexLookup):
        index = nodeIndexLookup[self.Node]
        adjacentStateIndex = nodeIndexLookup[self.Adjacent]
        return genes[index] != genes[adjacentStateIndex]

def build_rules(items):
    rulesAdded = {}

    for state, adjacent in items.items():
        for adjacentState in adjacent:
            if adjacentState == '':
                continue
            rule = Rule(state, adjacentState)
            if rule in rulesAdded:
                rulesAdded[rule] += 1
            else:
                rulesAdded[rule] = 1

            """
            for k,v in rulesAdded.items():
                if v != 2:
                    print("rule {} is not bidirectional".format(k))
            """

    return rulesAdded.keys()

class GraphColoringTests(unittest.TestCase):
    def test(self):
        states = load_data("adjacent_states.csv")
        rules = build_rules(states)
        optimalValue = len(rules) - 10 
        stateIndexLookup = {key: index
                            for index, key in enumerate(sorted(states))}

        colors = ["Orange", "Yellow", "Green", "Blue"]
        colorLookup = {color[0]: color for color in colors}
        geneset = list(colorLookup.keys())

        startTime = datetime.datetime.now()

        def fnDisplay(candidate):
            display(candidate, startTime)

        def fnGetFitness(genes):
            return get_fitness(genes, rules, stateIndexLookup)

        best = genetic.get_best(fnGetFitness, len(states),
                                optimalValue, geneset, fnDisplay)
        self.assertTrue(not optimalValue > best.Fitness)

        keys = sorted(states.keys())
        for index in range(len(states)):
            print(keys[index] + " is " + colorLookup[best.Genes[index]])
            print(keys[index] + ":" + "{name: 'State', description: 'default', color: '" + colorLookup[best.Genes[index]] + "',  hover_color: 'default', url: 'default'},")
            textfile = open("colorData.js", "a")
            textfile.write("simplemaps_usmap_mapdata.state_specific." + keys[index] + ".color = " + '"' + colorLookup[best.Genes[index]] + '"' + "; \n")
            textfile.close()

        #webUrl = urllib.request.urlopen('https://www.javatpoint.com/python-tutorial')
        webbrowser.open('file://{}/test.html'.format(os.getcwd()))

def display(candidate, startTime):
    timeDiff = datetime.datetime.now() - startTime

    print("{}\t{}\t{}".format(
        ''.join(map(str, candidate.Genes)),
        candidate.Fitness,
        timeDiff))

def get_fitness(genes, rules, stateIndexLookup):
    rulesThatPass = sum(1 for rule in rules
                        if rule.IsValid(genes, stateIndexLookup))
    return rulesThatPass

if __name__ == '__main__':
    unittest.main()
