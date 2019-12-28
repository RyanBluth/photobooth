import gphoto2 as gp


class Slr:
    context: gp.Context = None
    camera: gp.Camera = None

    def capture_image(self):
        self.init_camera()
        file_path = self.camera.capture(gp.GP_CAPTURE_IMAGE, self.context)
        print(file_path)

    def capture_preview_image(self):
        self.init_camera()
        camera_file: gp.CameraFile = self.camera.capture_preview(self.context)
        image_data = camera_file.get_data_and_size()
        return image_data

    def init_camera(self):
        if self.camera is None:
            try:
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
