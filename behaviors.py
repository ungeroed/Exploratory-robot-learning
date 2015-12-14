import random
import time
from lasso import Lasso

class Behaviors():

    def __init__(self, robot, algorithm):
        self.robot = robot 
        self.lasso = Lasso()
        self.algorithm = algorithm
        self.state = algorithm.getInitialState(self.getSensorState())
        self.terminate = False

        self.behaviors = {
            "explore": self.explore,
            "faceObject": self.faceObject,
            "stop": self.stop,
            "identifyMoveableObject": self.identifyMoveableObject,
            "grab": self.grab,
            "release": self.release,
            "tryGrab": self.tryGrab,
        }

    def run(self):
        behaviorResult = None
        while not self.terminate:
            self.state = self.algorithm.eventHandler(self.state,
                    self.getSensorState(), behaviorResult)
            behaviorResult = self.behaviors[self.state]()

    def getSensorState(self):
        return {
            "frontSensors": self.robot.getFrontSensors(),
            "groundSensors": self.robot.getGroundSensors(),
            "rearSensors": self.robot.getRearSensors(),
            "accelerometer": self.robot.getAccelerometer(),
            "micIntensity": self.robot.getMicIntensity(),
            "lassoState": self.lasso.getState()
        }

    def safe(self):
        return not self.robot.overEdge()

    def grab(self):
        self.lasso.up()
        self.robot.left(10)
        self.robot.backwards(2)
        while len(filter(lambda x: x > 2500, self.robot.getRearSensors())) > 0:
            self.robot.forward(0.1)
        self.lasso.down()

    def tryGrab(self):
        self.grab()
        self.robot.forward(5)
        time.sleep(1.5)
        if len(filter(lambda x: x > 1000, self.robot.getRearSensors())) == 0:
            self.release()
            return
        
        before_sensors = self.robot.getRearSensors()
        self.robot.forward(1)
        time.sleep(0.5)
        after_sensors = self.robot.getRearSensors()
        if len(filter(lambda (x,y): abs(x-y) > 100, zip(before_sensors, after_sensors))) == 0:
            self.release()
            return

        self.robot.left(5)
        if len(filter(lambda x: x > 1000, self.robot.getRearSensors())) == 0:
            self.release()


    def release(self):
        self.lasso.up()

    def explore(self):
        if len(filter(lambda x: x > 0, self.robot.getFrontSensors())) == 0:
            random.choice([self.robot.forward]*3 + [self.robot.left, self.robot.right])(2)
        else:
            self.robot.left(1)

    def faceObject(self):
        frontSensors = self.robot.getFrontSensors()
        if not max(frontSensors) == frontSensors[2]:
            if frontSensors[1] > frontSensors[3]:
                self.robot.left(0.25)
            else:
                self.robot.right(0.25)

    def identifyMoveableObject(self):
        self.robot.forward(5)
        before = self.robot.getFrontSensors()[2]
        time.sleep(2)
        after = self.robot.getFrontSensors()[2]
        return before-after > 1500

    def stop(self):
        self.terminate = True
