import time;
import mouse;
import keyboard;
import math;
import sys;
import os;
import json;

config = json.load(open('config.json'))
KEYS = config.get('keybinds', {})
BASE_SPEED = config.get('base_speed', 500)
POLL_RATE = config.get('poll_rate', 100)
KEYBOARD_ID = config.get('keyboard_id', '-1')
MASTER_ID = config.get('master_id', '-1')

allKeys = []
for(key, value) in KEYS.items():
    allKeys.extend(value)

mouseKeys = {
    "1": "left",
    "2": "middle",
    "3": "right",
}

def disableX11Keyboard():
    print("Disabling X11")
    result = os.system(f"xinput float {KEYBOARD_ID}")
    if(result != 0):
        print("X11 not found")

def enableX11Keyboard():
    print("Enabling X11")
    result = os.system(f"xinput reattach {KEYBOARD_ID} {MASTER_ID}")
    if(result != 0):
        print("X11 not found")

def keyboardDefaultHook(e):
    if(e.name.lower() in allKeys): return

    if(e.event_type == 'down'):
        keyboard.press(e.name)
    else:
        keyboard.release(e.name)


def isPressed(label):
    if(not label in KEYS): return False
    for key in KEYS[label]:
        if(keyboard.is_pressed(key)):
            return True;
    return False;

def mouseHook(e):
    for(key, value) in mouseKeys.items():
        if(e.name in value):
            if(e.event_type == 'down'):
                mouseDown(key)
                break
            else:
                mouseUp(key)
                break


def mouseDown(mouseKey):
    if(sys.platform == "linux"):
        os.system(f"xdotool mousedown {mouseKey}")
    else:
        button = mouseKeys[mouseKey]
        mouse.press(button)

def mouseUp(mouseKey):
    if(sys.platform == "linux"):
        os.system(f"xdotool mouseup {mouseKey}")
    else:
        button = mouseKeys[mouseKey]
        mouse.release(button)


def main():
    # Disable x11 on linux
    if(sys.platform == "linux"):
        disableX11Keyboard()
        keyboard.hook(keyboardDefaultHook)

    while True:
        if(isPressed('quit')): 
            break;

        # HANDLE CLICKS
        for key in mouseKeys:
            if(isPressed(key) and not mouse.is_pressed(mouseKeys[key])):
                mouseDown(key)
            elif(not isPressed(key)):
                mouseUp(key)

        # HANDLE SCROLL
        scrolldown = isPressed('scroll_down')
        scrollup = isPressed('scroll_up')
        scrollleft = isPressed('scroll_left')
        scrollright = isPressed('scroll_right')

        if(scrolldown and not scrollup):
            if(sys.platform == "linux"):
                os.system(f"xdotool click 5")
            else:
                mouse.wheel(-1)
            continue;
        elif(scrollup and not scrolldown):
            if(sys.platform == "linux"):
                os.system(f"xdotool click 4")
            else:
                mouse.wheel(1)
            continue;

        # Sideways scroll on linux
        if(sys.platform == "linux" and scrollleft and not scrollright):
            os.system(f"xdotool click 6")
            continue;
        elif(sys.platform == "linux" and scrollright and not scrollleft):
            os.system(f"xdotool click 7")
            continue;

        # HANDLE MOVEMENT
        up = isPressed('up')
        down = isPressed('down')
        left = isPressed('left')
        right = isPressed( 'right')

        # Direction
        x = 0;
        y = 0;

        # Set speed
        # ! Slow is overrides fast
        speed = BASE_SPEED;
        if(isPressed('very_slow')): 
            speed = speed / 5
        elif(isPressed('slow')): 
            speed = speed / 2;
        elif(isPressed('fast')): 
            speed = speed * 3
        elif(isPressed('very_fast')): 
            speed = speed * 6

        # Set direction
        if(up and not down):
            y = -1;
        elif(down and not up):
            y = 1;
        if(left and not right):
            x = -1;
        elif(right and not left):
            x = 1;

        xDelta = 0;
        yDelta = 0;
        mag = math.sqrt(x**2 + y**2)

        # Normalize and scale speed
        if(mag > 0):
            xDelta = (x / mag * speed) / POLL_RATE;
            yDelta = (y / mag * speed) / POLL_RATE;
            # Minimum move is 1 pixel
            if(0 < abs(xDelta) < 1 ): 
                xDelta /= abs(xDelta);
            if(0 < abs(yDelta) < 1): 
                yDelta /= abs(yDelta);

        # Move mouse
        mouse.move(xDelta, yDelta, absolute=False);

        # Wait for next poll
        time.sleep(1 / POLL_RATE);

try:
    main()
except Exception as e:
    print("ERROR",e)
finally:
    # Enable x11 on linux
    if(sys.platform == "linux"):
        enableX11Keyboard()

