import importlib
import pkg_resources
from distutils.version import LooseVersion
import webbrowser

try:
    import pip
    main = pip.main
except AttributeError:
    from pip._internal import main

version = "1.0.3"


def update_self(_version, file, version_location, script_location, install_updates):
    import requests
    if requests.get(version_location).text.strip() != _version and install_updates:
        import basic_functions
        print("You are not running the current version of the program.")
        print("You really should be. It's better. I promise.")
        if basic_functions.check("Want me to download it for you?\ny/n\n"):
            # Downloads the new version
            new = requests.get(script_location).content
            with open(file, "wb") as script:
                script.write(new)
            print("Success!")
            return False
        else:
            if basic_functions.check("Want me to take you to the page so you can update it yourself?\ny/n\n"):
                # Leads the user to the page to download the new version
                input(
                    "I'll take you to the page when you press enter. Right-click the page, click Save As... and choose "
                    "the correct file location.")
                webbrowser.open(script_location, new=2,
                                autoraise=True)
                input("Once you've done that you can restart the bot.")
                exit()
        input("You can press enter to continue running the bot with this version or close the program now.")
        return True
    return True


def pypi(_module, alt):
    try:
        importlib.import_module(_module)
    except (ImportError, ModuleNotFoundError):
        print("Package " + _module + " not found, installing now...")
        main(["install", alt])
        print("Package installed.")


def check_version(_module, _version):
    module_version = pkg_resources.get_distribution(_module).version
    if LooseVersion(module_version) < LooseVersion(_version):
        print("Package " + _module + "not up to date. Updating now.")
        main(["install", "-U", _module])
        print("Package updated.")


def check_our_package(package, location, _version, directory):
    try:
        package_version = importlib.import_module(package).version
    except (ImportError, ModuleNotFoundError):
        package_version = "0"

    if LooseVersion(package_version) < LooseVersion(_version):
        print("Downloading file...")
        import requests
        with open(directory + "/" + package + ".py", "wb") as f:
            url = location + package + ".py"
            script = requests.get(url).content
            f.write(script)
        print("Download complete.")
