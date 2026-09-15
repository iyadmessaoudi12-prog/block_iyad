[app]

# (str) Title of your application
title = BLOCK IYAD

# (str) Package name
package.name = blockiyad

# (str) Package domain (needed for android/ios packaging)
package.domain = com.iyad.blockgame

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include
source.include_exts = py,png,jpg,jpeg,json

# (list) Application version
version = 1.0.0

# (list) Application requirements
requirements = python3,pygame

# (str) Supported orientations (portrait)
orientation = portrait

# (bool) Fullscreen
fullscreen = 1

# (list) Permissions
android.permissions = INTERNET

# (int) Target Android API
android.api = 33

# (int) Minimum API required
android.minapi = 21

# (int) Android NDK version
android.ndk = 25b

# (bool) Use private storage
android.private_storage = True

# (bool) Copy library
android.copy_libs = 1

# (list) Architectures to build for
android.archs = arm64-v8a, armeabi-v7a

# (bool) Accept SDK license automatically
android.accept_sdk_license = True

[buildozer]

# (int) Log level (2 = debug)
log_level = 2

# (int) Display warning if buildozer is run as root
warn_on_root = 1
