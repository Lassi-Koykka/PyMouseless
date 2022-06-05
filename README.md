# PyMouseless
A cross-platform python script which allows you to control your mouse using the keyboard

## How to use
#### 1. First install the dependecies
- **Globally** (**Linux:** Recommended, use sudo): \
    `pip install keyboard mouse`

- **Using pipenv:** \
    `pipenv install keyboard mouse`

#### 1.5 Linux users: install xdotool
- Linux mouse clicks require xdotool to work due to limitations of the mouse library on linux

#### 2.0 Set your configurations in config.json
- `"base_speed"` : Sets the base speed of the cursor
- `"poll_rate"` : Sets the amount of times the mouse will be updated in one second
- `"keybinds"` : Contains all your keybinds
    - **"scroll_left" and "scroll_right" only available in linux** \
        However sideways scrolling can be achieved by not assigning the shift key in keybinds and pressing it while scrolling
- `"keyboard_id"` : **Linux only**
    - Id of the keyboard which will be disabled
    - Needed for disabling and re-enabling the x11 keyboard
    - **[How to get the id](https://askubuntu.com/a/178741)**
- `"master_id"` : **Linux only**
    - Id of the master keyboard
    - Needed for disabling and re-enabling the x11 keyboard
    - **[How to get the id](https://askubuntu.com/a/178741)**

### 3.0 make the script easily runnable
- Run it using python3 **OR** Create a shell script to run it and add it to the path
