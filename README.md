# Automatic Pico-Ducky Loader for UK Keyboards
### Automatically reloads a raspberry pi pico bad-usb instead of manually having to reload it with a new script every time.
## About
I was annoyed that every time you wanted to load a new script into your pico-ducky, you had to: boot into bootloader mode, wipe it, copy circuitpython to the root to set it up as circuitpy, copy all necessary libraries into the lib foler, copy all necessary python scripts into the root and then edit the duckyinpython.py script to change the keyboard layout!
## Prerequisites
[circuitpython-bundle](https://circuitpython.org/board/raspberry_pi_pico/) and [circuitpython loader uf2 file](https://github.com/adafruit/Adafruit_CircuitPython_Bundle/releases)
<br>Raspberry Pi Pico non-wireless edition.


## Full Installation Instructions
#### Mainly follows [this tutorial](https://github.com/dbisu/pico-ducky/tree/main?tab=readme-ov-file#full-install-instructions)

1. First download and unzip [circuitpython-bundle](https://circuitpython.org/board/raspberry_pi_pico/).<br>`
PLEASE NOTE: The unzipped folder will be duplicated inside of the child directory of the unzipped folder, meaning you will need to copy the child directory that is INSIDE the output of the zipped folder!!!
`
2. Once you have the folder containing lib, examples and requirements, copy and paste it into your necessary_files folder (called this by default in the working directory).
3. Then download the [circuitpython loader uf2 file](https://github.com/adafruit/Adafruit_CircuitPython_Bundle/releases) (Make sure it's english (UK)), and place this alongside your circuitpython-bundle folder, into the necessary_files folder.
<br><br>At This point you should have a folder called `necessary_files` in your working directory with a folder that starts with `adafruit-circuitpython-bundle` inside it and a file that starts with `adafruit-circuitpython-raspberry_pi_pico-en_GB` also inside it.<br><br>
4. Make sure you have everything completed in the `Usage` section, then hold the bootloader button on your pico and plug it in. It should appear as "RPI-RP2" with drive letter "D".
5. Now run main.py, which will run through the steps in the `About` section.
6. Once finished, it's ready to be loaded with any `payload.dd` file.

## Usage
````
git clone https://github.com/h0bnobs/auto-pico-ducky-loader
cd auto-pico-ducky-loader
pip install -r requirements.txt
python main.py
````