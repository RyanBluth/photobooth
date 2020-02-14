import gphoto2 as gp
import subprocess
import os
import time
from typing import Optional


class CamInitializationException(Exception):
    def __init__(self, message: str, cause: Exception):
        super().__init__(message)
        self.cause = cause


class CaptureImageException(Exception):
    def __init__(self, cause: Exception):
        super().__init__("Failed to capture image")
        self.cause = cause


class Cam:
    context: Optional[gp.Context] = None
    camera: Optional[gp.Camera] = None
    capturing_image: bool = False

    def capture_image(self):
        self.init_camera()
        try:
            self.capturing_image = True
            self.lower_mirror()
            file_path = self.camera.capture(gp.GP_CAPTURE_IMAGE, self.context)
            camera_file = self.camera.file_get(
                file_path.folder, file_path.name, gp.GP_FILE_TYPE_NORMAL)
            os.makedirs("photos", exist_ok=True)
            camera_file.save(f"photos/{str(int(time.time()))}.jpg")
            self.capturing_image = False
        except Exception as ex:
            print("Failed to capture image: " + str(ex))
            self.capturing_image = False
            raise CaptureImageException(ex)

    def capture_preview_image(self):
        self.init_camera()
        camera_file: gp.CameraFile = self.camera.capture_preview(self.context)
        image_data = camera_file.get_data_and_size()
        return image_data

    def init_camera(self):
        if self.camera is None:
            try:
                subprocess.call(["pkill", "gvfs"])
                self.context = gp.Context()
                self.camera = gp.Camera()
                self.camera.init(self.context)
            except Exception as ex:
                self.camera = None
                raise CamInitializationException("Failed to initialize camera", ex)

    def lower_mirror(self):
        self.init_camera()
        config: gp.CameraWidget = self.camera.get_config(self.context)
        child: gp.CameraWidget = config.get_child_by_name("viewfinder")
        child.set_value(0)
        self.camera.set_config(config, self.context)

    def release_camera(self):
        if self.camera is not None:
            self.camera.exit(self.context)
            self.camera = None
            self.context = None
