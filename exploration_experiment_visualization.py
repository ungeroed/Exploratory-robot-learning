import dataloader
from textwrap import wrap
import sys
from discretization import SimplifyingDiscretizer
from normalization import normalize
from graph import MarkovChainGraph
import matplotlib.pyplot as plt
stateTranslate = {
        '0.0, 0.0, 0.0': 'nothing to see',
        '1.0, 0.0, 0.0': 'object in front',
        '1.0, 1.0, 0.0': 'facing object',
        '0.0, 0.0, 1.0': 'object grabbed',
        '1.0, 0.0, 1.0': 'object grabbed and object in front',
        '1.0, 1.0, 1.0': 'object grabbed and facing object',
        }

if __name__ == '__main__':
    plt.rcParams.update({'figure.autolayout': True})
    filename = sys.argv[1]
    sensorStates, behaviors = dataloader.load(filename)
    discretizer = SimplifyingDiscretizer()
    graph = MarkovChainGraph()
    result = {}
    ss = []
    for sensorState in sensorStates:
        sensorState = normalize(sensorState)
        s = discretizer.discretize(sensorState)
        s = graph.state_to_key(s)
        ss.append(stateTranslate[s])
        if stateTranslate[s] in result:
            result[stateTranslate[s]] += 1
        else:
            result[stateTranslate[s]] = 1

    graph.construct(ss, behaviors)
    graph.visualize(filename + '.dot', ss[0])

    dictionary = plt.figure()

    axes = plt.gca()
    axes.set_ylim([0,1000])

    values = result.values()
    plt.bar(range(len(result)), values, align='center')
    labels = [ '\n'.join(wrap(str(v) + " " + l, 10)) for (l,v) in zip(result.keys(), result.values()) ]
    plt.xticks(range(len(result)), labels)
    plt.tick_params(axis='x', labelsize=10)

    plt.savefig(filename + '.png')
    print(result)
