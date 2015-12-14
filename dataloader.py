import sys

def load(filename):
    sensorStates = []
    behaviors = []
    with open(filename, 'r') as f:
        b = False
        i = 0
        for l in f:
            i += 1
            line = l[:-1]
            if b:
                behaviors.append(line)
            else:
                try:
                    sensorStates.append(eval(line))
                except:
                    print("failed parsing on line", i)
                    sys.exit(1)
            b = not b
    return sensorStates, behaviors
