import subprocess
import time
import os
import win32api

import get_all_files

# TODO: RENAME THESE TO WHATEVER!!
nfd = 'necessary_files' # necessary files directory
drive_letter = "D:"


def run_command(command, verbose=False, powershell=False):
    """
    Runs the given command. Prints output to the terminal if verbose is True.
    Uses PowerShell if powershell is True.
    """
    shell_cmd = ["powershell", "-Command", command] if powershell else command
    try:
        process = subprocess.run(
            shell_cmd,
            shell=True,
            check=True,
            capture_output=not verbose,
            text=True,
        )
        if verbose:
            if process.stdout is not None:
                print(process.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Command {command} failed with error: {e.stderr}")


def check_for_rpi_pico():
    if os.path.exists(drive_letter):
        volume_label = win32api.GetVolumeInformation(drive_letter)[0]

        if volume_label == "RPI-RP2":
            return volume_label
        elif volume_label == "CIRCUITPY":
            return volume_label
        else:
            print(f"Drive {drive_letter} found, but it's not a Raspberry Pi Pico (Label: {volume_label})")
    else:
        print(f"Drive {drive_letter} not found.")

    return False


def update_duckyinpython_file(file_path):
    """
    Updates lines 23 and 24 in duckyinpython.py to change the keyboard layout and keycode imports to 'uk'.
    :param file_path: The full path to duckyinpython.py.
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()

    lines[17] = "#from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS as KeyboardLayout\n"
    lines[18] = "#from adafruit_hid.keycode import Keycode\n"
    lines[22] = "from keyboard_layout_win_uk import KeyboardLayout\n"
    lines[23] = "from keycode_win_uk import Keycode\n"

    with open(file_path, 'w') as file:
        file.writelines(lines)

    print(f"Updated {file_path}: uncommented US layout and updated UK layout and keycode.")


def main():
    if not get_all_files.check_for_necessary_files():
        get_all_files.get_necessary_files()

    nfd_contents = os.listdir(nfd)
    matching_files = [file for file in nfd_contents if file.startswith("adafruit-circuitpython-raspberry_pi_pico-en_GB")]
    if not matching_files:
        raise NotADirectoryError(f"Error with getting circuitpython main .uf2 . Are you sure it is in {nfd}/ ? "
                                 f"It should start with 'adafruit-circuitpython-raspberry_pi_pico-en_GB'")
    circuitpython_uf2_file = matching_files[0]

    # wipe the pico
    if check_for_rpi_pico() == 'RPI-RP2':
        print(f"Pico found at RPI-RP2, wiping it now!")
        # run_command("ls D:", verbose=True, powershell=True)
        if 'INDEX.HTM' in os.listdir(drive_letter) and 'INFO_UF2.TXT' in os.listdir(drive_letter):
            run_command(f"cp {nfd}/flash_nuke.uf2 {drive_letter}")

    time.sleep(10)
    # make it into circuitpy
    if check_for_rpi_pico() == 'RPI-RP2':
        print(f"Pico found at RPI-RP2, copying {circuitpython_uf2_file} now to turn it into CIRCUITPY")
        # run_command("ls D:", verbose=True, powershell=True)
        if 'INDEX.HTM' in os.listdir(drive_letter) and 'INFO_UF2.TXT' in os.listdir(drive_letter):
            run_command(f"cp {nfd}/{circuitpython_uf2_file} {drive_letter}")

    time.sleep(10)
    if check_for_rpi_pico() == 'CIRCUITPY':
        print(f"Pico found at CIRCUITPY!! Now pasting everything from {nfd}/")
        run_command(f"cp -r {nfd}/adafruit_hid {drive_letter}/lib")
        run_command(f"cp {nfd}/adafruit_debouncer.mpy {drive_letter}/lib")
        run_command(f"cp {nfd}/adafruit_ticks.mpy {drive_letter}/lib")
        run_command(f"cp -r {nfd}/asyncio {drive_letter}/lib")
        run_command(f"cp -r {nfd}/adafruit_wsgi {drive_letter}/lib")
        run_command(f"cp {nfd}/boot.py {drive_letter}")
        run_command(f"cp {nfd}/duckyinpython.py {drive_letter}")
        run_command(f"cp {nfd}/code.py {drive_letter}")
        run_command(f"cp {nfd}/keyboard_layout_win_uk.py {drive_letter}/lib")
        run_command(f"cp {nfd}/keycode_win_uk.py {drive_letter}/lib")
        update_duckyinpython_file(f"{drive_letter}/duckyinpython.py")


if __name__ == '__main__':
    main()
