[app]
title = Call Screen
package.name = callscreen
package.domain = org.callscreen
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy==2.2.1,kivymd @ https://github.com/kivymd/KivyMD/archive/master.zip,plyer==2.1.0
orientation = portrait
fullscreen = 0
android.permissions = RECEIVE_SMS,READ_SMS,READ_PHONE_STATE,READ_CALL_LOG
android.api = 31
android.minapi = 21
android.ndk = 23b
android.sdk = 31
android.accept_sdk_license = True
android.arch = arm64-v8a
android.enable_androidx = True

# Performance optimizations
android.enable_hardware_acceleration = True
android.allow_backup = True
android.meta_data = android.max_aspect=2.5

[buildozer]
log_level = 2
warn_on_root = 1
