[app]

# (str) Title of your application
title = Ramsha

# (str) Package name
package.name = ramsha

# (str) Package domain (needed for android packaging)
package.domain = org.ramsha

# (str) Application version
version = 1.0

# (list) Source files to include (let it empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,db,html,css,js

# (list) Source files to exclude (let it empty to exclude none)
source.exclude_exts = spec

# (list) List of directory to exclude
source.exclude_dirs = bin, venv, .git, __pycache__

# (str) Application source directory (relative to buildozer.spec)
source.dir = .

# (list) Application requirements
# Add all Python dependencies your Flask app needs (e.g., flask, gunicorn, etc.)
requirements = python3,flask,gunicorn,jinja2,werkzeug,click,itsdangerous

# (str) Custom source folders for requirements
#requirements.source.kivy = ../../../kivy

# (list) Permissions
android.permissions = INTERNET

# (list) Features
#android.features = android.hardware.usb.host

# (str) Supported orientations
orientation = portrait

# (list) The orientation that the application can support.
#supported_orientations = landscape,portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (string) Presplash background color
#presplash.color = #FFFFFF

# (string) Animation to use on the splash screen
#presplash.animation = @anim/iv_loading

# (list) List of service to declare
#services = NAME:ENTRYPOINT_TO_PYTHON_SCRIPT

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) Path to build artifact, storage, the root path
bin_dir = ./bin

# (str) Path to build target
# build_dir = .buildozer

android.accept_sdk_license = True
android.api = 33
android.min_api = 21
android.sdk_build_tools_version = 33.0.2
