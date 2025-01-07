import board
import analogio
import time
import pwmio
from adafruit_motor import servo
import digitalio


def init():
    global positionen, position, DEBUG, Bewegungsdauer, last_position, x_axis, y_axis, achsen, pwm1, pwm2, pwm3, pwm4, servo1, servo2, servo3, servo4, pwms, btn_rec, btn_change, axis_12, btn_play, GradProKlick

    last_position = 90
    position = 90
    positionen = [[90, 90, 90, 90]]

    DEBUG = False
    Bewegungsdauer = 0.4
    GradProKlick = 5

    x_axis = analogio.AnalogIn(board.GP26)
    y_axis = analogio.AnalogIn(board.GP27)

    achsen = [90, 90, 90, 90]

    pwm1 = pwmio.PWMOut(board.GP12, duty_cycle=0, frequency=50)
    pwm2 = pwmio.PWMOut(board.GP13, duty_cycle=0, frequency=50)
    pwm3 = pwmio.PWMOut(board.GP14, duty_cycle=0, frequency=50)
    pwm4 = pwmio.PWMOut(board.GP15, duty_cycle=0, frequency=50)

    servo1 = servo.Servo(pwm1, min_pulse=500, max_pulse=2250)
    servo2 = servo.Servo(pwm2, min_pulse=500, max_pulse=2250)
    servo3 = servo.Servo(pwm3, min_pulse=500, max_pulse=2250)
    servo4 = servo.Servo(pwm4, min_pulse=500, max_pulse=2250)

    pwms = [pwm1, pwm2, pwm3, pwm4]

    btn_rec = digitalio.DigitalInOut(board.GP20)
    btn_rec.direction = digitalio.Direction.INPUT
    btn_rec.pull = digitalio.Pull.UP

    btn_play = digitalio.DigitalInOut(board.GP21)
    btn_play.direction = digitalio.Direction.INPUT
    btn_play.pull = digitalio.Pull.UP
    
    btn_change = digitalio.DigitalInOut(board.GP19)
    btn_change.direction = digitalio.Direction.INPUT
    btn_change.pull = digitalio.Pull.UP

    axis_12 = True


init()


def get_voltage(pin):
    return (pin.value * 3.3) / 65536


def ease_in_out(t):
    if t < 0.5:
        return 4 * t * t * t
    else:
        p = 2 * t - 2
        return 0.5 * p * p * p + 1


def move_servos_eased(servos, start_positions, end_positions, duration):
    steps = 500
    for i in range(steps + 1):
        t = i / steps
        eased_t = t * t * (3 - 2 * t)
        for servo, start_pos, end_pos in zip(servos, start_positions, end_positions):
            if DEBUG:
                print("Servo: ", servo, "Start: ", start_pos, "End: ", end_pos)
            servo.angle = start_pos + (end_pos - start_pos) * eased_t
        time.sleep(duration / steps)


servo1.angle = achsen[0]
servo2.angle = achsen[1]
servo3.angle = achsen[2]
servo4.angle = achsen[3]

while True:
    x_val = get_voltage(x_axis)
    y_val = get_voltage(y_axis)
    
    if last_position is None or position != last_position:
        print(position)
        if position > (90 / GradProKlick):
            position = (90 / GradProKlick)

        if position < -(90 / GradProKlick):
            position = -(90 / GradProKlick)

        winkel = 90 + position * 5
        servo1.angle = winkel
    last_position = position
    
    time.sleep(0.1)
    
    
    if axis_12:
        axis1 = 1
        axis2 = 2
    else:
        axis1 = 0
        axis2 = 3
    
    if y_val < 1.6:
        bewegung = abs(y_val - 1.6)
        if achsen[axis1] < 170:
            achsen[axis1] -= int(bewegung * 5)
            if achsen[axis1] > 180:
                achsen[axis1] = 180
            if axis_12:
                servo2.angle = achsen[axis1]
            else:
                servo1.angle = achsen[axis1]
            print(f"Joystick nach links {axis1} {achsen[axis1]}")
    if y_val > 1.7:
        bewegung = y_val - 1.7
        if achsen[axis1] > 10:
            achsen[axis1] += int(bewegung * 5)
            if achsen[axis1] < 0:
                achsen[axis1] = 0
            if axis_12:
                servo2.angle = achsen[axis1]
            else:
                servo1.angle = achsen[axis1]
            print(f"Joystick nach rechts {axis1} {achsen[axis1]}")
    if x_val < 1.6:
        bewegung = abs(x_val - 1.6)
        if achsen[axis2] < 170:
            achsen[axis2] += int(bewegung * 5)
            if achsen[axis2] > 180:
                achsen[axis2] = 180
            if axis_12:
                servo3.angle = achsen[axis2]
            else:
                servo4.angle = achsen[axis2]
            print(f"Joystick nach unten {axis2} {achsen[axis2]}")
            print(x_val)
    elif x_val > 1.7:   
        bewegung = x_val - 1.7
        if achsen[axis2] > 10:
            achsen[axis2] -= int(bewegung * 5)
            if achsen[axis2] < 0:
                achsen[axis2] = 0
            if axis_12:
                servo3.angle = achsen[axis2]
            else:
                servo4.angle = achsen[axis2]
            print(f"Joystick nach oben {axis2} {achsen[axis2]}")
            print(x_val)
    if not btn_play.value:
        print("PLAY is pressed")
        for i in range(len(positionen)):
            print(positionen[i])
            move_servos_eased([servo1, servo2, servo3, servo4], achsen, positionen[i], Bewegungsdauer)
            achsen = positionen[i]
        print("Ende")
        
        time.sleep(1)
    if not btn_rec.value:
        print("REC is pressed")
        if positionen[-1] != achsen:
            positionen.append(achsen.copy())
            print("Position hinzugefügt")
        else:
            print("Position schon vorhanden")
        print(positionen)
        time.sleep(1)

    if not btn_change.value:
        print("CHANGE is pressed")
        axis_12 = not axis_12
        print(axis_12)
        time.sleep(1)
