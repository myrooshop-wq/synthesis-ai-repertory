import os

device_js = r"d:\software by me\synthesis homeopathy\build_apk\assets\www\plugins\cordova-plugin-device\www\device.js"
with open(device_js, "r", encoding="utf-8") as f:
    text = f.read()

target = 'utils.alert("[ERROR] Error initializing Cordova: " + e);'
replacement = 'console.warn("[Cordova] Device init error:", e); channel.onCordovaInfoReady.fire();'
if target in text:
    text = text.replace(target, replacement)
    with open(device_js, "w", encoding="utf-8") as f:
        f.write(text)
    print("Patched device.js successfully")
else:
    print("Target already replaced or not found in device.js")

appinfo_js = r"d:\software by me\synthesis homeopathy\build_apk\assets\www\plugins\cordova-plugin-appinfo\www\appinfo.js"
with open(appinfo_js, "r", encoding="utf-8") as f:
    text2 = f.read()

replacement2 = 'console.warn("[Cordova] AppInfo init error:", e); channel.onAppInfoReady.fire();'
if target in text2:
    text2 = text2.replace(target, replacement2)
    with open(appinfo_js, "w", encoding="utf-8") as f:
        f.write(text2)
    print("Patched appinfo.js successfully")
else:
    print("Target already replaced or not found in appinfo.js")

# Also patch cordova.js utils.alert directly so ANY unhandled error never pops up an ugly blocking dialog
cordova_js = r"d:\software by me\synthesis homeopathy\build_apk\assets\www\cordova.js"
with open(cordova_js, "r", encoding="utf-8") as f:
    cord = f.read()

old_alert = """utils.alert = function(msg) {
    if (window.alert) {
        window.alert(msg);
    } else if (console && console.log) {
        console.log(msg);
    }
};"""

new_alert = """utils.alert = function(msg) {
    if (msg && msg.indexOf("Error initializing Cordova") !== -1) {
        console.warn("[Cordova Ignored Error]", msg);
        return;
    }
    if (window.alert) {
        window.alert(msg);
    } else if (console && console.log) {
        console.log(msg);
    }
};"""

if old_alert in cord:
    cord = cord.replace(old_alert, new_alert)
    with open(cordova_js, "w", encoding="utf-8") as f:
        f.write(cord)
    print("Patched cordova.js utils.alert successfully")
