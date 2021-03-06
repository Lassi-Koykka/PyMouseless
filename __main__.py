import time;
import mouse;
import keyboard;
import math;
import sys;
import os;
import json;
import psutil;

config = json.load(open(os.path.join(sys.path[0], "config.json")))
KEYS = config.get('keybinds', {})
BASE_SPEED = config.get('base_speed', 500)
SCROLL_SPEED = config.get('scroll_speed', 0.01)
MOVE_SPEEDS = config.get('move_speeds', {
        "very_slow": 100,
        "slow": 250,
        "fast": 1500,
        "very_fast": 3000 
})
POLL_RATE = config.get('poll_rate', 100)
KEYBOARD_ID = config.get('keyboard_id', '-1')
MASTER_ID = config.get('master_id', '-1')
CUSTOM_KEYBINDS = config.get('custom_keybinds', {})

allKeys = []

for(key, value) in KEYS.items():
    allKeys.extend(value)

global customKeybindStates
customKeybindStates =  {}

for key in CUSTOM_KEYBINDS:
    allKeys.append(key)
    customKeybindStates[key] = False


mouseKeys = {
    "1": "left",
    "2": "middle",
    "3": "right",
}

global mouseKeyStates
mouseKeyStates = {
    "1": False,
    "2": False,
    "3": False
}

#Enable and Disable x11 on linux
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

# Default keyboard hook for linux 
# makes it possible to use the other keys on the keyboard while in mouse mode
def keyboardDefaultHook(e):
    if(e.name.lower() in allKeys): return

    key = e.name
    # # Custom keybinds Linux Linux
    # if(e.name.lower() in CUSTOM_KEYBINDS):
    #     key = CUSTOM_KEYBINDS[e.name.lower()]

    if(key == "unknown"): 
        print("Unknown key:", key)
        return

    if(e.event_type == 'down'):
        keyboard.press(key)
    else:
        keyboard.release(key)


# Check if any key of control is pressed
def isPressed(label):
    if(not label in KEYS): return False
    for key in KEYS[label]:
        if(keyboard.is_pressed(key)):
            return True;
    return False;

# Send mousedown 
def mouseDown(mouseKey):
    if(sys.platform == "linux"):
        os.system(f"xdotool mousedown {mouseKey}")
    else:
        button = mouseKeys[mouseKey]
        mouse.press(button)

    mouseKeyStates[mouseKey] = True

# Send mouseup
def mouseUp(mouseKey):
    if(sys.platform == "linux"):
        os.system(f"xdotool mouseup {mouseKey}")
    else:
        button = mouseKeys[mouseKey]
        mouse.release(button)

    mouseKeyStates[mouseKey] = False

def mouseHook(e):
    for(key, value) in mouseKeys.items():
        if(e.name in value):
            if(e.event_type == 'down'):
                mouseDown(key)
                break
            else:
                mouseUp(key)
                break

# Check if script is running
def is_running(script):
    for q in psutil.process_iter():
        if q.name().startswith('python') or q.name().startswith('pythonw'):
            if len(q.cmdline())>1 and script in q.cmdline()[1] and q.pid != os.getpid():
                print("'{}' Process is already running".format(script))
                return True

    return False

def run_custom_keybind(key):
    print(f"Running custom keybind: {key} -> {CUSTOM_KEYBINDS[key]}")
    keyboard.send(CUSTOM_KEYBINDS[key])

def main():
    dir = os.path.dirname(os.path.realpath(__file__))
    script_name = os.path.split(dir)[-1]
    print("Script name:", script_name)
    if(is_running(script_name) or __name__ != "__main__"): 
        return

    try:
        # Disable x11 on linux
        if(sys.platform == "linux"):
            disableX11Keyboard()
            keyboard.hook(keyboardDefaultHook)
        else:
            for key in allKeys:
                try:
                    keyboard.block_key(key)
                except:
                    print(f"Unable to block key: {key} . Key unkown.")


        while True:
            if(isPressed('quit')): 
                break;

            # Handle custom keybinds
            for key in CUSTOM_KEYBINDS:
                bind = CUSTOM_KEYBINDS[key]
                if(not customKeybindStates[key] and keyboard.is_pressed(key)):
                    keyboard.press(bind)
                    customKeybindStates[key] = True
                elif(customKeybindStates[key] and not keyboard.is_pressed(key)):
                    keyboard.release(bind)
                    customKeybindStates[key] = False



            # HANDLE CLICKS
            for key in mouseKeys:
                if(isPressed(key) and not mouseKeyStates[key]):
                    # print("Mouse down", key)
                    mouseDown(key)
                elif(not isPressed(key) and mouseKeyStates[key]):
                    # print("Mouse up", key)
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
                    mouse.wheel(-SCROLL_SPEED)  # type: ignore
                continue;
            elif(scrollup and not scrolldown):
                if(sys.platform == "linux"):
                    os.system(f"xdotool click 4")
                else:
                    mouse.wheel(SCROLL_SPEED)  # type: ignore
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
            for speedModifier in MOVE_SPEEDS:
                if(isPressed(speedModifier)):
                    # print("Speed:", speedModifier)
                    speed =  MOVE_SPEEDS[speedModifier]
                    break;

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
            # print(f"Move: {xDelta}, {yDelta}")

            # Wait for next poll
            time.sleep(1 / POLL_RATE);

    except Exception as e:
        print("ERROR",e)
    finally:
        # Enable x11 on linux
        if(sys.platform == "linux"):
            enableX11Keyboard()
# RUN
main()
