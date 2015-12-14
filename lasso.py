import RPi.GPIO as GPIO
import time

class Lasso:
    def __init__(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(7, GPIO.OUT)
        p = GPIO.PWM(7,50)
        p.start(7)
        self.state = "up"
        self.p = p

    def cycle(self, i):
        self.p.ChangeDutyCycle(i)
        time.sleep(0.5)

    def up(self):
        self.state = "up"
        self.cycle(7)

    def down(self):
        self.state = "down"
        self.cycle(11)

    def getState(self):
        return self.state

    def close(self):
        self.p.stop()
        GPIO.cleanup()

if __name__ == "__main__":
    l = Lasso()
    while True:
        c = raw_input()
        if c == "u":
            print "Going up!"
            l.up()
        elif c == "d":
            print "Going down!"
            l.down()
        else:
            break
    l.close()
