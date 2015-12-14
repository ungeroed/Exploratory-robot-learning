import signal, sys, time

from thymio_api import ThymioAPI
from behaviors import Behaviors
from algorithms import ColorTraveller, ObjectHomer, RandomCollector, ProblemSolver, SmartCollector
from graph import MarkovChainGraph, ANNGraph
from discretization import SOMDiscretizer, RoundingDiscretizer, SimplifyingDiscretizer, KMeansDiscretizer
from search import DepthFirstSearch, RandomWalkSearch
from problem import BallPickupProblem
from normalization import normalize
import dataloader
    
if __name__ == '__main__':
    robot = ThymioAPI() 

    def signal_handler(signal, frame):
        robot.forward(1)
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)

    with open("/root/test.out", "a") as f:
        #algorithm = ColorTraveller()
        #algorithm = ObjectHomer()
        #algorithm = RandomCollector(f)
        algorithm = SmartCollector(f, SimplifyingDiscretizer())
        behaviors = Behaviors(robot, algorithm)
        behaviors.run()

    #sensorStates, behaviors = dataloader.load("test.out")
    #discretizer = SOMDiscretizer()
    #discretizer = RoundingDiscretizer()
    #discretizer = SimplifyingDiscretizer()
    #discretizer = KMeansDiscretizer(5)
    #graph = MarkovChainGraph()
    #graph = ANNGraph(round_output=True)
    #search = DepthFirstSearch()
    #search = RandomWalkSearch()
    #problem = BallPickupProblem()

    #algorithm = ProblemSolver(discretizer, graph, search, problem, sensorStates, behaviors)
    #algorithm = ObjectHomer()
    #behaviors = Behaviors(robot, algorithm)
    #behaviors.run()
