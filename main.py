import subprocess
import time
import os
import win32api

import get_all_files

nfd = 'necessary_files'  # necessary files directory


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


def get_available_drives():
    """Return the logical drive paths available on the machine."""
    try:
        return [drive for drive in win32api.GetLogicalDriveStrings().split('\0') if drive]
    except Exception as exc:
        print(f"Unable to read drive list: {exc}")
        return []


def get_pico_drive():
    """Find the drive letter for a mounted Raspberry Pi Pico."""
    for drive in get_available_drives():
        if not os.path.exists(drive):
            continue

        try:
            volume_label = win32api.GetVolumeInformation(drive)[0]
        except Exception:
            continue

        if volume_label in {"RPI-RP2", "CIRCUITPY"}:
            return drive

    return None


def check_for_rpi_pico():
    """
    Checks if the pico is plugged in and returns what "state" it's in.
    :return: volume_label either "RPI-RP2" or "CIRCUITPY"
    """
    pico_drive = get_pico_drive()
    if pico_drive:
        volume_label = win32api.GetVolumeInformation(pico_drive)[0]
        if volume_label in {"RPI-RP2", "CIRCUITPY"}:
            return volume_label, pico_drive

        print(f"Drive {pico_drive} found, but it's not a Raspberry Pi Pico (Label: {volume_label})")
    else:
        print("No Raspberry Pi Pico drive found. Hold BOOTSEL and plug in the Pico.")

    return False, None


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
    matching_files = [file for file in nfd_contents if
                      file.startswith("adafruit-circuitpython-raspberry_pi_pico-en_GB")]
    if not matching_files:
        raise NotADirectoryError(f"Error with getting circuitpython main .uf2 . Are you sure it is in {nfd}/ ? "
                                 f"It should start with 'adafruit-circuitpython-raspberry_pi_pico-en_GB'")
    circuitpython_uf2_file = matching_files[0]

    pico_state, pico_drive = check_for_rpi_pico()

    # wipe the pico
    if pico_state == 'RPI-RP2':
        print(f"Pico found at {pico_drive}, wiping it now!")
        if pico_drive and 'INDEX.HTM' in os.listdir(pico_drive) and 'INFO_UF2.TXT' in os.listdir(pico_drive):
            run_command(f"cp {nfd}/flash_nuke.uf2 {pico_drive}")

    time.sleep(10)
    pico_state, pico_drive = check_for_rpi_pico()

    # make it into circuitpy
    if pico_state == 'RPI-RP2':
        print(f"Pico found at {pico_drive}, copying {circuitpython_uf2_file} now to turn it into CIRCUITPY")
        if pico_drive and 'INDEX.HTM' in os.listdir(pico_drive) and 'INFO_UF2.TXT' in os.listdir(pico_drive):
            run_command(f"cp {nfd}/{circuitpython_uf2_file} {pico_drive}")

    time.sleep(10)
    pico_state, pico_drive = check_for_rpi_pico()
    if pico_state == 'CIRCUITPY':
        print(f"Pico found at CIRCUITPY!! Now pasting everything from {nfd}/")
        run_command(f"cp -r {nfd}/adafruit_hid {pico_drive}/lib")
        run_command(f"cp {nfd}/adafruit_debouncer.mpy {pico_drive}/lib")
        run_command(f"cp {nfd}/adafruit_ticks.mpy {pico_drive}/lib")
        run_command(f"cp -r {nfd}/asyncio {pico_drive}/lib")
        run_command(f"cp -r {nfd}/adafruit_wsgi {pico_drive}/lib")
        run_command(f"cp {nfd}/boot.py {pico_drive}")
        run_command(f"cp {nfd}/duckyinpython.py {pico_drive}")
        run_command(f"cp {nfd}/code.py {pico_drive}")
        run_command(f"cp {nfd}/keyboard_layout_win_uk.py {pico_drive}/lib")
        run_command(f"cp {nfd}/keycode_win_uk.py {pico_drive}/lib")
        update_duckyinpython_file(f"{pico_drive}/duckyinpython.py")


if __name__ == '__main__':
    main()
