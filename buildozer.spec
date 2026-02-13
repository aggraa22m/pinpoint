[app]
title = PinPoint
package.name = pinpoint
package.domain = org.pinpoint

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json

version = 1.0.0

requirements = python3,kivy,plyer,pillow

# android permissions
android.permissions = CAMERA,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,INTERNET

# orientation: landscape, portrait, or all
orientation = portrait

# use SDL2 backend
osx.python_version = 3
osx.kivy_version = 2.3.0

fullscreen = 0

# android-specific settings
android.api = 33
android.minapi = 26
android.ndk = 25b
android.accept_sdk_license = True
android.arch = arm64-v8a

# iOS settings
ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master

[buildozer]
log_level = 2
warn_on_root = 1
