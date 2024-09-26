import os
import main

nfd = main.nfd  # necessary files directory


def check_for_necessary_files():
    """
    Checks if all the necessary files needed for the pico are already present.
    :return: True if all the necessary files needed for the pico are present, False otherwise.
    """
    if not os.path.exists(nfd):
        os.makedirs(nfd)

    nfd_contents = os.listdir(nfd)
    required_files = [
        ('adafruit-circuitpython-raspberry_pi_pico-en_GB', "https://circuitpython.org/board/raspberry_pi_pico/"),
        ('adafruit-circuitpython-bundle',
         "https://github.com/adafruit/Adafruit_CircuitPython_Bundle/releases/tag/20240924")
    ]

    for prefix, link in required_files:
        if not any(file.startswith(prefix) for file in nfd_contents):
            raise FileNotFoundError(f"The file beginning with '{prefix}' wasn't found. Please download from {link}")

    for file_name in [
        'keyboard_layout_win_uk.py', 'keycode_win_uk.py', 'pico-ducky-main', 'flash_nuke.uf2'
    ]:
        if not os.path.exists(f"{nfd}/{file_name}"):
            print(f"The file {file_name} wasn't found in the directory {nfd}, so we will try to get all the files.")
            return False

    for file_name in [
        'adafruit_hid', 'adafruit_debouncer.mpy', 'adafruit_ticks.mpy', 'asyncio', 'adafruit_wsgi',
        'duckyinpython.py', 'code.py'
    ]:
        if not os.path.exists(f"{nfd}/{file_name}"):
            raise FileNotFoundError(f"The file {file_name} wasn't found in the directory {nfd}")

    print(f"All the necessary libraries/files were found in the directory {nfd}:")
    for name in nfd_contents:
        print(f"{nfd}/{name}")
    return True


def get_necessary_files():
    nfd_contents = os.listdir(nfd)
    matching_files = [file for file in nfd_contents if file.startswith("adafruit-circuitpython-bundle")]
    if not matching_files:
        raise NotADirectoryError(f"Error with getting circuitpython bundle full name. Are you sure it is in {nfd}/ ?")

    circuitpython_bundle = matching_files[0]
    main.run_command("git clone https://github.com/dbisu/pico-ducky.git", verbose=True)
    main.run_command(f'mv pico-ducky {nfd}/pico-ducky-main', verbose=True)

    files_to_copy = [
        'adafruit_hid', 'adafruit_debouncer.mpy', 'adafruit_ticks.mpy', 'asyncio', 'adafruit_wsgi'
    ]
    for file in files_to_copy:
        main.run_command(f"cp -r {nfd}/{circuitpython_bundle}/lib/{file} {nfd}", verbose=True)

    for script in ['boot.py', 'duckyinpython.py', 'code.py']:
        main.run_command(f"cp {nfd}/pico-ducky-main/{script} {nfd}", verbose=True)

    urls = {
        "flash_nuke.uf2": "https://raw.githubusercontent.com/dwelch67/raspberrypi-pico/main/flash_nuke.uf2",
        "keycode_win_uk.py": "https://raw.githubusercontent.com/Neradoc/Circuitpython_Keyboard_Layouts/main/libraries/keycodes/keycode_win_uk.py",
        "keyboard_layout_win_uk.py": "https://raw.githubusercontent.com/Neradoc/Circuitpython_Keyboard_Layouts/main/libraries/layouts/keyboard_layout_win_uk.py"
    }

    for filename, url in urls.items():
        main.run_command(f"wget -O {nfd}/{filename} {url}", powershell=True)

    check_for_necessary_files()
