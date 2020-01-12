import gphoto2 as gp
import subprocess
import os
import time
from typing import Optional


class Cam:
    context: Optional[gp.Context] = None
    camera: Optional[gp.Camera] = None
    capturing_image: bool = False

    def capture_image(self):
        self.init_camera()
        self.capturing_image = True
        config: gp.CameraWidget = self.camera.get_config(self.context)
        child: gp.CameraWidget = config.get_child_by_name("viewfinder")
        child.set_value(0)
        self.camera.set_config(config, self.context)
        file_path = self.camera.capture(gp.GP_CAPTURE_IMAGE, self.context)
        camera_file = self.camera.file_get(
            file_path.folder, file_path.name, gp.GP_FILE_TYPE_NORMAL)
        os.makedirs("photos", exist_ok=True)
        camera_file.save(f"photos/{str(int(time.time()))}.jpg")
        self.capturing_image = False

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
            except:
                print("Failed to initialize camera")

    def release_camera(self):
        if self.camera is not None:
            self.camera.exit(self.context)
            self.camera = None
            self.context = None
