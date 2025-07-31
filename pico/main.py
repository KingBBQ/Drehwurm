import board
import rotaryio
import digitalio
import time
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
import neopixel
import random
import math

# Setup
keyboard = Keyboard(usb_hid.devices)
pixels = neopixel.NeoPixel(board.GP12, 25, brightness=0.3, auto_write=False)
encoder = rotaryio.IncrementalEncoder(board.GP16, board.GP17)
button = digitalio.DigitalInOut(board.GP14)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP

# Variablen
last_position = 0
button_pressed = False
idle_counter = 0

# Erweiterter Wurm mit Augen
class FunWorm:
    def __init__(self):
        # Korrigierter Pfad für das tatsächliche Layout
        # Basierend auf Ihrer Angabe (1-basiert zu 0-basiert konvertiert):
        # Rechts runter: 1,10,11,20,21 → 0,9,10,19,20
        # Links runter: 5,6,15,16,25 → 4,5,14,15,24
        
        self.path = [
            # Oben (vermutlich 1,2,3,4,5 → 0,1,2,3,4)
            0, 1, 2, 3, 4,
            # Rechts runter (5→6→15→16→25 in 1-basiert = 4→5→14→15→24 in 0-basiert)
            5, 14, 15, 24,
            # Unten (vermutlich rückwärts 25,24,23,22,21 → 24,23,22,21,20)
            23, 22, 21, 20,
            # Links hoch (21→20→11→10→1 in 1-basiert = 20→19→10→9→0 in 0-basiert)
            19, 10, 9
        ]
        
        self.head_position = 0
        self.length = 6
        self.body_positions = [0]
        self.direction = "right"
        self.eye_blink_counter = 0
        
    def move(self, direction):
        """Bewegt den Wurm"""
        self.direction = direction
        
        # Kopf bewegen
        if direction == "right":
            self.head_position = (self.head_position + 1) % len(self.path)
        else:
            self.head_position = (self.head_position - 1) % len(self.path)
        
        # Körper nachziehen
        self.body_positions.insert(0, self.head_position)
        if len(self.body_positions) > self.length:
            self.body_positions.pop()
        
        self.eye_blink_counter += 1
        self.draw()
    
    def draw(self):
        """Zeichnet den Wurm mit Kopf-Details"""
        # Bildschirm leeren mit Trail
        for i in range(25):
            current = pixels[i]
            pixels[i] = (current[0] // 3, current[1] // 3, current[2] // 3)
        
        # Wurm zeichnen
        for i, pos in enumerate(self.body_positions):
            pixel_index = self.path[pos]
            
            if i == 0:  # Kopf
                # Hauptfarbe basierend auf Richtung
                if self.direction == "right":
                    head_color = (255, 150, 0)  # Helles Orange
                else:
                    head_color = (0, 150, 255)  # Helles Blau
                
                # Blinzeln alle 20 Bewegungen
                if self.eye_blink_counter % 20 < 2:
                    head_color = tuple(c // 3 for c in head_color)  # Dunkel = Augen zu
                
                pixels[pixel_index] = head_color
                
            elif i == 1:  # Hals (etwas heller als Körper)
                if self.direction == "right":
                    pixels[pixel_index] = (200, 80, 0)
                else:
                    pixels[pixel_index] = (0, 80, 200)
                    
            else:  # Körper
                # Wellenmuster im Körper
                wave = math.sin(i * 0.5 + time.monotonic() * 5) * 0.3 + 0.7
                intensity = int(200 * (1 - (i / self.length)) * wave)
                
                if self.direction == "right":
                    color = (intensity, intensity // 3, 0)
                else:
                    color = (0, intensity // 3, intensity)
                
                pixels[pixel_index] = color
        
        pixels.show()

# Feuerwerk mit Herz am Ende
def love_firework():
    """Spezial-Feuerwerk mit Herz"""
    # Angepasst für das tatsächliche Layout
    patterns = [
        [12],  # Zentrum
        [12, 7, 11, 13, 17],  # Kleines Kreuz
        [6, 7, 8, 11, 12, 13, 16, 17, 18],  # Größeres Kreuz
        [0, 2, 4, 10, 14, 20, 22, 24],  # Diagonalen/Ecken
        # Herz-Form
        [1, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 22]
    ]
    
    # Explosion
    for i, frame in enumerate(patterns[:-1]):
        pixels.fill((0, 0, 0))
        for pixel in frame:
            color = (random.randint(150, 255),
                    random.randint(150, 255),
                    random.randint(150, 255))
            pixels[pixel] = color
        pixels.show()
        time.sleep(0.06)
    
    # Herz pulsieren
    for pulse in range(3):
        pixels.fill((0, 0, 0))
        for pixel in patterns[-1]:
            brightness = 255 if pulse % 2 == 0 else 100
            pixels[pixel] = (brightness, 0, brightness // 2)
        pixels.show()
        time.sleep(0.2)
    
    # Ausblenden
    for fade in range(5):
        for i in range(25):
            current = pixels[i]
            pixels[i] = (current[0] // 2, current[1] // 2, current[2] // 2)
        pixels.show()
        time.sleep(0.05)

# Wurm initialisieren
worm = FunWorm()

# Hauptschleife
while True:
    position = encoder.position
    
    # Encoder Bewegung
    if position != last_position:
        if position > last_position:
            steps = position - last_position
            for _ in range(steps):
                keyboard.press(Keycode.DOWN_ARROW)
                keyboard.release(Keycode.DOWN_ARROW)
                worm.move("right")
        else:
            steps = last_position - position
            for _ in range(steps):
                keyboard.press(Keycode.UP_ARROW)
                keyboard.release(Keycode.UP_ARROW)
                worm.move("left")
        
        last_position = position
        idle_counter = 0
        
    # Taster
    if not button.value and not button_pressed:
        keyboard.press(Keycode.SPACE)
        keyboard.release(Keycode.SPACE)
        
        love_firework()
        idle_counter = 0
        button_pressed = True
        
    elif button.valu e:
        button_pressed = False
    
    # Idle: Wurm bewegt sich langsam von selbst
    idle_counter += 1
    if idle_counter > 100:  # Nach ~2 Sekunden
        if idle_counter % 20 == 0:  # Langsame Bewegung
            worm.move("right")
    
    time.sleep(0.02)
