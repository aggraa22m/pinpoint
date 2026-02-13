"""Platform permission helpers.

On Android/iOS we need runtime permissions for camera, location, etc.
On desktop these are usually granted automatically.
plyer handles most of this but we wrap it so the rest of the app
doesn't need to know the details.
"""
from kivy.utils import platform
from kivy.logger import Logger

# only import android-specific stuff when actually on android
if platform == "android":
    from android.permissions import request_permissions, Permission  # noqa

    REQUIRED_PERMISSIONS = [
        Permission.CAMERA,
        Permission.ACCESS_FINE_LOCATION,
        Permission.ACCESS_COARSE_LOCATION,
    ]
else:
    REQUIRED_PERMISSIONS = []


def request_app_permissions(callback=None):
    """Request all permissions the app needs.

    On desktop this is a no-op. On mobile it triggers the OS permission dialogs.
    """
    if platform == "android":
        Logger.info("Permissions: requesting android permissions")
        request_permissions(REQUIRED_PERMISSIONS, callback)
    else:
        Logger.info("Permissions: desktop platform, skipping permission request")
        if callback:
            callback([], [])


def check_permission(permission_name):
    """Check if a specific permission has been granted."""
    if platform != "android":
        return True  # always granted on desktop
    try:
        from android.permissions import check_permission as _check
        return _check(permission_name)
    except ImportError:
        return True
