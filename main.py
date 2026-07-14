import subprocess
import shutil
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


def copy_path(source, destination, recursive=False):
    """Copy a file or directory to a destination in a platform-safe way."""
    if recursive:
        target_path = os.path.join(destination, os.path.basename(source)) if os.path.isdir(destination) else destination
        os.makedirs(os.path.dirname(target_path) if os.path.dirname(target_path) else '.', exist_ok=True)
        shutil.copytree(source, target_path, dirs_exist_ok=True)
        return target_path

    target_path = destination if not os.path.isdir(destination) else os.path.join(destination, os.path.basename(source))
    os.makedirs(os.path.dirname(target_path) if os.path.dirname(target_path) else '.', exist_ok=True)
    shutil.copy2(source, target_path)
    return target_path


def find_payload_file(payload_dir, payload_name=None):
    """Locate a payload file dynamically from a directory."""
    if payload_name:
        candidate = os.path.join(payload_dir, payload_name)
        if os.path.isfile(candidate):
            return candidate

    payload_candidates = []
    for entry in os.listdir(payload_dir):
        if entry.lower().endswith('.dd') or entry.lower().endswith('.txt'):
            payload_candidates.append(os.path.join(payload_dir, entry))

    if not payload_candidates:
        raise FileNotFoundError(f"No payload files found in {payload_dir}")

    payload_candidates.sort()
    return payload_candidates[0]


def copy_payload_to_pico(pico_drive, payload_dir, payload_name=None):
    """Copy the selected payload onto the Pico root as payload.dd."""
    payload_path = find_payload_file(payload_dir, payload_name)
    target_path = os.path.join(pico_drive, 'payload.dd')
    copy_path(payload_path, target_path)
    return payload_path


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


def main(payload_dir='.', payload_name=None):
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
            copy_path(os.path.join(nfd, 'flash_nuke.uf2'), pico_drive)

    time.sleep(10)
    pico_state, pico_drive = check_for_rpi_pico()

    # make it into circuitpy
    if pico_state == 'RPI-RP2':
        print(f"Pico found at {pico_drive}, copying {circuitpython_uf2_file} now to turn it into CIRCUITPY")
        if pico_drive and 'INDEX.HTM' in os.listdir(pico_drive) and 'INFO_UF2.TXT' in os.listdir(pico_drive):
            copy_path(os.path.join(nfd, circuitpython_uf2_file), pico_drive)

    time.sleep(10)
    pico_state, pico_drive = check_for_rpi_pico()
    if pico_state == 'CIRCUITPY':
        print(f"Pico found at CIRCUITPY!! Now pasting everything from {nfd}/")
        copy_path(os.path.join(nfd, 'adafruit_hid'), os.path.join(pico_drive, 'lib'), recursive=True)
        copy_path(os.path.join(nfd, 'adafruit_debouncer.mpy'), os.path.join(pico_drive, 'lib'))
        copy_path(os.path.join(nfd, 'adafruit_ticks.mpy'), os.path.join(pico_drive, 'lib'))
        copy_path(os.path.join(nfd, 'asyncio'), os.path.join(pico_drive, 'lib'), recursive=True)
        copy_path(os.path.join(nfd, 'adafruit_wsgi'), os.path.join(pico_drive, 'lib'), recursive=True)
        copy_path(os.path.join(nfd, 'boot.py'), pico_drive)
        copy_path(os.path.join(nfd, 'duckyinpython.py'), pico_drive)
        copy_path(os.path.join(nfd, 'code.py'), pico_drive)
        copy_path(os.path.join(nfd, 'keyboard_layout_win_uk.py'), os.path.join(pico_drive, 'lib'))
        copy_path(os.path.join(nfd, 'keycode_win_uk.py'), os.path.join(pico_drive, 'lib'))
        payload_path = copy_payload_to_pico(pico_drive, payload_dir, payload_name)
        print(f"Copied payload {payload_path} to {pico_drive}")
        update_duckyinpython_file(os.path.join(pico_drive, 'duckyinpython.py'))


if __name__ == '__main__':
    main()
