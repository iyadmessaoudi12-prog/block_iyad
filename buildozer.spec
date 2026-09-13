[app]
title = BLOCK IYAD
package.name = blockiyad
package.domain = org.iyad

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,wav,ogg

version = 0.1
requirements = python3,kivy

orientation = landscape
fullscreen = 1

android.api = 31
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_licenses = True

p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1
