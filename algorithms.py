from __future__ import print_function
import util
import random
import numpy as np
from normalization import normalize
from sys import maxint
from search import RandomWalkSearch, DepthFirstSearch
from graph import MarkovChainGraph
from problem import FindStateProblem

class ProblemSolver():
    def __init__(self, discretizer, graph, search, problem, sensorStates, behaviors, graphInputFilename=None, graphOutputFilename=None):
        normSensorStates = map(normalize, sensorStates)
        print(normSensorStates[0])

        print("Training discretizer")
        self.discretizer = discretizer
        discretizer.train(normSensorStates)
        print("Done training discretizer")

        discSensorStates = map(discretizer.discretize, normSensorStates)
        
        print("Constructing graph")
        self.graph  = graph
        if graphInputFilename is None:
            graph.construct(discSensorStates, behaviors)
        else:
            graph.load(graphInputFilename)

        if graphOutputFilename:
            graph.save(graphOutputFilename)
        print("Done constructing graph")

        self.search = search
        self.problem = problem
        self.sensorStateHistory = []

    def getInitialState(self, sensorState):
        return self.action(sensorState)

    def eventHandler(self, state, sensorState, behaviorResult):
        return self.action(sensorState)

    def action(self, sensorState):
        norm = normalize(sensorState)
        dis = self.discretizer.discretize(norm)
        self.sensorStateHistory.append(dis)
        n = self.problem.required_state_sequence_length()
        if self.problem.goal(self.sensorStateHistory[-n:]):
            print("stop")
            return "stop"
        behavior, _ = self.search.choose_behavior(self.sensorStateHistory,
                self.graph, self.problem)
        print(behavior)
        return behavior

class ColorTraveller():

    def __init__(self):
        self.lookingForRed = True

    def getInitialState(self, sensorState):
        return "explore"

    def eventHandler(self, state, sensorState, behaviorResult):
        if self.lookingForRed:
            check = util.isRed
        else:
            check = util.isYellow

        if check(sensorState["groundSensors"]):
            self.lookingForRed = not self.lookingForRed
            print('Red?', self.lookingForRed)
            return "explore"
        else:
            return "explore"


class RandomCollector():

    def __init__(self, outputFile):
        self.f = outputFile
        self.behaviors = ["explore"]*80 + ["faceObject"]*10 + ["tryGrab"]*5 + ["release"]*5
    
    def getInitialState(self, sensorState):
        return self.nextBehavior(sensorState)

    def eventHandler(self, state, sensorState, behaviorResult):
        return self.nextBehavior(sensorState) 

    def nextBehavior(self, sensorState):
        print(sensorState, file=self.f)
        behavior = random.choice(self.behaviors)
        print(behavior)
        print(behavior, file=self.f)
        return behavior

class SmartCollector():

    def __init__(self, outputFile, discretizer):
        self.f = outputFile
        self.discretizer = discretizer
        self.behaviors = ["explore", "faceObject", "tryGrab", "release"]
        self.stateBehaviors = {} # State -> Behavior -> Count
        self.algorithmState = "random"
        self.graph = MarkovChainGraph()
        self.search = DepthFirstSearch()
        self.randomMoves = 0
        self.randomBehaviors = ["explore"]*80 + ["faceObject"]*10 + ["tryGrab"]*5 + ["release"]*5
        self.sinceLastNewState = 0
        self.previous_state = None
        self.previous_behavior = None
        self.last_search_behavior = None
        self.same_search_behavior = 0
        self.round = 0
    
    def getInitialState(self, sensorState):
        self.initialState = self.discretizer.discretize(normalize(sensorState))
        return self.nextBehavior(sensorState)

    def eventHandler(self, state, sensorState, behaviorResult):
        return self.nextBehavior(sensorState) 

    def selectBehavior(self, stateBehaviors):
        for b in self.behaviors:
            if b not in stateBehaviors:
                return b

        minpair = (maxint, "")
        for behavior, count in stateBehaviors.iteritems():
            if count < minpair[0]:
                minpair = (count, behavior)

        return minpair[1]
    
    def minCountState(self):
        mincount = maxint
        minstate = ""
        for state, behaviors in self.stateBehaviors.iteritems():
            if mincount > behaviors["count"]:
                mincount = behaviors["count"]
                minstate = state
        return (minstate, mincount)
    
    def randomBehavior(self, dis, discretized):
        if self.stateBehaviors[dis]["count"] == 0 or self.randomMoves > 20:
            self.randomMoves = 0
            self.algorithmState = "intelligent"
            return self.intelligentBehavior(dis, discretized)
        else:
            self.randomMoves += 1
            return random.choice(self.randomBehaviors)

    def intelligentBehavior(self, dis, discretized):
        if self.sinceLastNewState > 20:
            self.sinceLastNewState = 0
            self.algorithmState = "random"
            return self.randomBehavior(dis, discretized)

        if self.stateBehaviors[dis]["count"] > (self.minCountState()[1] + 20):
            self.sinceLastNewState = 0
            self.algorithmState = "search"
            self.goal_state, self.goal_state_count = self.minCountState()
            return self.searchBehavior(dis, discretized)

        self.sinceLastNewState += 1
        return self.selectBehavior(self.stateBehaviors[dis])
    
    def searchBehavior(self, dis, discretized):
        if dis == self.goal_state or dis not in self.stateBehaviors:
            self.goal_state = None
            self.goal_state_count = None
            self.algorithmState = "intelligent"
            return self.intelligentBehavior(dis, discretized)
        problem = FindStateProblem(self.goal_state)
        behavior, err = self.search.choose_behavior([discretized], self.graph, problem)

        print("Searching for:", self.goal_state)
        if err <= 0 or self.same_search_behavior > 5:
            print("No path, random")
            self.same_search_behavior = 0
            return random.choice(self.randomBehaviors)

        if self.last_search_behavior == behavior:
            self.same_search_behavior += 1
        else:
            self.last_search_behavior = behavior
            self.same_search_behavior = 0

        return behavior

    def nextBehavior(self, sensorState):
        self.round += 1
        print("\nRound:", self.round)
        print("Algorithm:", self.algorithmState)
        print(sensorState, file=self.f)
        normSensorState = normalize(sensorState)
        discretized = self.discretizer.discretize(normSensorState)
        dis = self.graph.state_to_key(discretized)

        if self.previous_state is not None and self.previous_behavior is not None:
            self.graph.construct([self.previous_state, discretized],
                    [self.previous_behavior])

        if dis not in self.stateBehaviors:
            self.sinceLastNewState = 0
            self.stateBehaviors[dis] = {}
            self.stateBehaviors[dis]["count"] = 0
            self.stateBehaviors[dis]["origin"] = discretized

        behavior = "explore"
        if self.algorithmState == "random":
            behavior = self.randomBehavior(dis, discretized)
        elif self.algorithmState == "intelligent":
            behavior = self.intelligentBehavior(dis, discretized)
        elif self.algorithmState == "search":
            behavior = self.searchBehavior(dis, discretized)


        if behavior not in self.stateBehaviors[dis]:
            self.stateBehaviors[dis][behavior] = 0

        self.stateBehaviors[dis][behavior] += 1
        self.stateBehaviors[dis]["count"] += 1
        print(self.stateBehaviors)
        print("State:", dis)
        print("Behavior:", behavior)
        print(behavior, file=self.f)
        self.previous_state = discretized
        self.previous_behavior = behavior
        self.graph.visualize('dot/graph.dot', self.initialState)
        self.graph.visualize('dot/graph_%d.dot' % self.round, self.initialState)
        return behavior


class ObjectHomer():

    def __init__(self):
        self.Done = False
        self.leavingObject = False
        self.grabbedObject = False

    def getInitialState(self, sensorState):
        return "explore"

    def eventHandler(self, state, sensorState, behaviorResult):
        print(state)
        frontSensors = sensorState["frontSensors"]
        rearSensors = sensorState["rearSensors"]

        if self.Done:
            return "stop"

        if state == "tryGrab" and sensorState["lassoState"] == "down":
            self.grabbedObject = True
            self.grabbedColor = sensorState["groundSensors"]

        #We have grabbed an object, we now home it
        if self.grabbedObject:
            if abs(np.mean(self.grabbedColor)-np.mean(sensorState["groundSensors"])) > 50:
                self.grabbedObject = False
                self.Done = True
                print("Found my home")
                return "release"
            else:
                return "explore"

        #We are now leaving an object, rotate until we see nothing
        if self.leavingObject:
            if len(filter(lambda x: x > 0, frontSensors)) == 0:
                self.leavingObject = False
            return "explore"
        
        #We are seeing nothing, keep on exploring
        if len(filter(lambda x: x > 0, frontSensors)) == 0:
            return "explore"
        
        #We are facing an object, lets see if it is moveable
        if max(frontSensors) == frontSensors[2]:
            return "tryGrab"

        #We have met an object, lets face it.
        return "faceObject"

class NaiveCollector():

    def __init__(self, outputFile, discretizer):
        self.f = outputFile
        self.discretizer = discretizer
        self.behaviors = ["explore", "faceObject", "tryGrab", "release"]
        self.stateBehaviors = {}
    
    def getInitialState(self, sensorState):
        return self.nextBehavior(sensorState)

    def eventHandler(self, state, sensorState, behaviorResult):
        return self.nextBehavior(sensorState) 

    def selectBehavior(self, stateBehaviors):
        for b in self.behaviors:
            if b not in stateBehaviors:
                return b

        minpair = (maxint, "")
        for behavior, count in stateBehaviors.iteritems():
            if count < minpair[0]:
                minpair = (count, behavior)

        return minpair[1]

    def nextBehavior(self, sensorState):
        print(sensorState, file=self.f)
        normSensorState = normalize(sensorState)
        dis = ",".join(map(str, self.discretizer.discretize(normSensorState)))

        if dis not in self.stateBehaviors:
            self.stateBehaviors[dis] = {}

        behavior = self.selectBehavior(self.stateBehaviors[dis])

        if behavior not in self.stateBehaviors[dis]:
            self.stateBehaviors[dis][behavior] = 0

        self.stateBehaviors[dis][behavior] += 1
        print(self.stateBehaviors)
        print(behavior)
        print(behavior, file=self.f)
        return behavior
