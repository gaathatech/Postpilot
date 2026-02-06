[app]
title = PostPilot
package.name = postpilot
package.domain = org.aidniglobal.postpilot
source.dir = .
source.include_exts = py,png,jpg,kv,json,ttf,txt
version = 1.0
requirements = python3,kivy,requests
icon.filename = logo.png
orientation = portrait
fullscreen = 1

# (str) Presplash of the application
# presplash.filename = presplash.png

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 1

# (list) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# Metadata
# Owner: Aidni Global LLP
# Developer: Hardik Gajjar

[buildozer]
log_level = 2
warn_on_root = 1
# (str) Directory in which python-for-android should look for your own build recipes (if any)
# p4a.local_recipes = ./recipes

# (bool) Copy library instead of making a libpymodules.so
copy_libs = 1

# (str) Path to build artifact storage, absolute or relative to spec file
# bin_dir = bin

# (int) Number of concurrent threads used
# to speed up the build process
# use -1 to autodetect
# jobs = 2

[app.android]
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,ACCESS_NETWORK_STATE

# (list) Specifies which architectures to build for
android.archs = arm64-v8a,armeabi-v7a

# (str) Android logcat filters to use
# android.logcat_filters = *:S python:D

# (dict) Android additional metadata to set in the AndroidManifest.xml
android.meta_data = \
    owner_name=Aidni Global LLP,\
    developer_name=Hardik Gajjar

# (bool) Enable AndroidX support
android.enable_androidx = 1

# (bool) Enables regular updates of the app
# android.allow_backup = 0

# (str) Android package fallback
# android.manifest_placeholders = appAuthRedirectScheme:org.aidniglobal.postpilot
