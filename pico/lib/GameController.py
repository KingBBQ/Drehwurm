import time
import board
import neopixel
import math
import busio
import pwmio
import usb_hid


# alles für die Tastatur:
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode


# Diesse Bibliothek kümmert sich um den Neigungsmesser
from adafruit_lsm6ds.lsm6ds3 import LSM6DS3

# Erstellen Sie eine I2C-Instanz 
# i2c ist ein "Protokoll", also die Sprache, die verschiedene elektronische Bauteile miteinander sprechen.
# nerd fact: es wird "i quadrat c" ausgesprochen
# Der kleine Sensor in der Mitte der Platine wird an den Anschlüssen GP6 und GP7 am Pico angeschlossen.
i2c = busio.I2C(scl=board.GP7, sda=board.GP6)  # SCL an GP7, SDA an GP6

# jetzt wird der Sensor "initialisiert", also angeschaltet.
sensor = LSM6DS3(i2c)

# Der Pico hat zum Messen eine Spannung von 3.3 Volt.
# Das müssen wir wissen, wenn wir zum Beispiel die Bewegung des Joysticks messen.
MAX_SPANNUNG = 3.3

# Auf den farbigen LEDs sind in wirklichkeit 3 LEDs mit nur einer Farbe.
# Die Farben der LEDs sind in Rot, Grün, Blau definiert.
# 255 bedeutet, die entsprechende Farbe ist voll an.
# 0 bedeutet, die Farbe ist aus.

# Um es beim Programmieren einnfacher zu machen, erstellen wir Variablen, die die passenden Farb-Codes gespeichert haben.
ROT = (255, 0, 0)
GRÜN = (0, 255, 0)
BLAU = (0, 0, 255)
GELB = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)
LILA = (128, 0, 128)
WEISS = (255, 255, 255)
SCHWARZ = (0, 0, 0)
ROSA = (255, 192, 203)
BRAUN = (165, 42, 42)



# Anzahl der LEDs und der Pin
anzLEDs = 25
pinLED = board.GP12

LEDs = neopixel.NeoPixel(pinLED, anzLEDs, brightness=0.2, auto_write=True)

def setzeLEDFarbe(pixel, farbe):
    LEDs[pixel] = farbe

def setzeLEDaus(pixel):
    LEDs[pixel] = SCHWARZ

def setzeAlleFarbe(farbe):
    for i in range(anzLEDs):
        setzeLEDFarbe(i,farbe)

    
def setzeAlleAus():
    for i in range(anzLEDs):
        setzeLEDaus(i)

def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        return (0, 0, 0)
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    if pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    pos -= 170
    return (pos * 3, 0, 255 - pos * 3)


def chase_effect(farbe = ROT, wartezeit = 0.1):
    """Erzeugt einen Chase-Effekt auf den Neopixel-LEDs."""
   
    for i in range(anzLEDs):
        setzeLEDFarbe(i, farbe)
        time.sleep(wartezeit)
        setzeLEDaus(i)  # LED ausschalten

    for i in range(anzLEDs - 1, -1, -1): # wir zählen rückwärts!
        setzeLEDFarbe(i, farbe)
        time.sleep(wartezeit)
        setzeLEDaus(i)  # LED ausschalten

def regenbogen(pause = 0.01):
    for j in range(255):
        for i in range(anzLEDs):
            pixel_index = (i * 256 // anzLEDs) + j
            LEDs[i] = wheel(pixel_index & 255)
        time.sleep(pause)


setzeAlleAus()




###########################################################
## Neigungssensor                                         #
###########################################################



def neigung_roh():
    """Gibt die x, y, z Werte vom Neigungssensor zurück."""
    accel_x, accel_y, accel_z = sensor.acceleration
    return accel_x, accel_y, accel_z

# Diese Funktion gibt dir die Neigung für die 3 verschiedenen Richtungen oder "Achsen" zurück.

def temperatur():
    return sensor.temperature

def drehung():
    return sensor.gyro

def neigung(): 
    """Gibt die Winkel für x, y, z zurück."""
    accel_x, accel_y, accel_z = neigung_roh()
    # pfui, jetzt kommt hier auch noch Mathe - bitte nicht hinschauen!
    angle_x = math.atan2(accel_y, accel_z) * 180 / math.pi
    angle_y = math.atan2(accel_x, accel_z) * 180 / math.pi
    angle_z = math.atan2(accel_x, accel_y) * 180 / math.pi
    return angle_x, angle_y, angle_z


def ist_bewegung_stark(schwelle=1):
    """Überprüft, ob die Bewegung stark ist."""
    drehung_x, drehung_y, drehung_z = drehung()

    magnitude = math.sqrt(drehung_x**2 + drehung_y**2 + drehung_z**2)
    print(magnitude)
    return magnitude > schwelle


###########################################################
## Touch-Steuerung                                        #
###########################################################

if board.board_id == "raspberry_pi_pico":

    import touchio

    # Die Touch-Pins sind an den Pins GP14 bis 17 angeschlossen.
    # Der Pico braucht da immer einen bestimmten Widerstand, die sind auf der Platine 

    touch_pins = [
        touchio.TouchIn(board.GP14),
        touchio.TouchIn(board.GP15),
        touchio.TouchIn(board.GP16),
        touchio.TouchIn(board.GP17)
    ]

else:
    touch_pins = [] 
    print("Dieses Board unterstützt keine Touch-Pins")

## und der kleine Piepsi-Lautsprecher:

# Initialisieren Sie den PWM-Ausgang für den Lautsprecher
lautsprecher = pwmio.PWMOut(board.GP20, duty_cycle=0, frequency=440, variable_frequency=True)


def spiele_ton(frequenz, laenge):
    """Spielt einen Ton mit einer bestimmten Frequenz und Dauer."""
    lautsprecher.frequency = frequenz
    lautsprecher.duty_cycle = 49152  # 75% Duty Cycle
    time.sleep(laenge)
    lautsprecher.duty_cycle = 0  # Ton ausschalten
    time.sleep(0.05)  # Kurze Pause zwischen den Tönen



###########################################################
## Alles für die Tastatur....                            ##
###########################################################

# Initialisieren Sie die Tastatur

if usb_hid.devices:
    global tastatur
    # tastatur = Keyboard(usb_hid.devices)
else:
    print("No HID devices are present.")




def drueckeTaste(taste, dauer = 0.2):
    if 'tastatur' not in globals():
        global tastatur
        tastatur = Keyboard(usb_hid.devices)
    """Drückt eine Taste für eine bestimmte Dauer und lässt sie dann los."""
    tastatur.press(taste)
    time.sleep(dauer)
    tastatur.release(taste)
  
