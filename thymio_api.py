#!/usr/bin/env python
import dbus
import dbus.mainloop.glib
import gobject
import sys
import time
from util import avg

def intArr(dbusArr):
    return map(lambda x: x*1, dbusArr)

class ThymioAPI:
    def __init__(self):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

        bus = dbus.SessionBus()

        #Create Aseba network 
        self.network = dbus.Interface(bus.get_object('ch.epfl.mobots.Aseba', '/'), dbus_interface='ch.epfl.mobots.AsebaNetwork')

    def getFrontSensors(self):
        #get the values of the sensors
        return intArr(self.network.GetVariable("thymio-II", "prox.horizontal"))[:5]

    def getRearSensors(self):
        return intArr(self.network.GetVariable("thymio-II", "prox.horizontal"))[5:7]


    # prox.ground.ambiant : ambient light intensity at the ground, varies between 0 (no light) and 1023 (maximum light)
    # prox.ground.reflected : amount of light received when the sensor emits infrared, varies between 0 (no reflected light) and 1023 (maximum reflected light)
    # prox.ground.delta : difference between reflected light and ambient light, linked to the distance and to the ground colour.
    def getGroundSensors(self):
        ambient = self.network.GetVariable("thymio-II", "prox.ground.ambiant")
        reflected = self.network.GetVariable("thymio-II", "prox.ground.reflected")
        delta = self.network.GetVariable("thymio-II", "prox.ground.delta")
        return (avg(ambient), avg(reflected), avg(delta))

    def overEdge(self):
        delta = self.network.GetVariable("thymio-II", "prox.ground.delta")
        return delta[0] < 300 and delta[1] < 300
    
    # acc[0] : x-axis (from right to left, positive towards left)
    # acc[1] : y-axis (from front to back, positive towards the rear)
    # acc[2] : z-axis (from top to bottom, positive towards ground)
    # The values in this array vary from -32 to 32, with 1 g 
    # (the acceleration of the earth's gravity) corresponding to the value 23. 
    # Thymio updates this array at a frequency of 16 Hz, 
    def getAccelerometer(self):
        return intArr(self.network.GetVariable("thymio-II", "acc"))

    def getMicIntensity(self):
        return self.network.GetVariable("thymio-II", "mic.intensity")[0]*1

    def safe(self):
        return not self.overEdge()

    def sleep(self, amount):
        d = 0.01
        t = 0
        while t < amount:
            if not self.safe():
                return
            time.sleep(d)
            t += d
    def move(self, left, right, amount):
        if self.safe():
            self.network.SetVariable("thymio-II", "motor.left.target", [left])
            self.network.SetVariable("thymio-II", "motor.right.target", [right])
            time.sleep(amount*0.1)
            self.network.SetVariable("thymio-II", "motor.left.target", [0])
            self.network.SetVariable("thymio-II", "motor.right.target", [0])

    def forward(self, amount):
        self.move(500, 500, amount)

    def backwards(self, amount):
        self.move(-500, -500, amount)

    def left(self, amount):
        self.move(-500, 500, amount)

    def right(self, amount):
        self.move(500, -500, amount)
