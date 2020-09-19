from io import BytesIO
from kivy.app import App
from kivy.clock import Clock
from kivy.core.image import Image as CoreImage
from kivy.core.window import Window
from kivy.graphics.vertex_instructions import Rectangle
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy import Config as KivyConfig
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from time import time
from cam import Cam, CamInitializationException
import printer

WIDTH = 1024
HEIGHT = 600


class PreviewScreen(Screen):
    NAME = "preview"
    file_name: str

    def __init__(self, file_name):
        super().__init__(name=PreviewScreen.NAME)
        self.file_name = file_name
        self.size = (1024, 600)
        image = Image(source=self.file_name, keep_ratio=True,
                      size_hint_y=0.73, pos_hint={'top': 1})
        self.add_widget(image)

        redo_button = Button(background_normal="./assets/image/redo_button_up.png",
                             background_down="./assets/image/redo_button_down.png",
                             size_hint=(None, None), size=(410, 137), pos=(68, 10),
                             on_press=self.redo_button_pressed
                             )
        self.add_widget(redo_button)

        print_button = Button(background_normal="./assets/image/print_button_up.png",
                              background_down="./assets/image/print_button_down.png",
                              size_hint=(None, None), size=(410, 137), pos=(546, 10),
                              on_press=self.print_button_pressed
                              )
        self.add_widget(print_button)

    def redo_button_pressed(self, instance):
        self.manager.current = CaptureScreen.NAME
        self.manager.remove_widget(self)

    def print_button_pressed(self, instance):
        pass


class CaptureErrorScreen(Screen):
    NAME = "capture_error"

    def __init__(self):
        super().__init__(name=CaptureErrorScreen.NAME)
        self.size = (1024, 600)

        error_label = Label(text="Oops, a picture couldn't be taken.\nMake sure you aren't standing too close to the camera.",
                            font_size='38', pos=(0, 167), size=(1024, 300), halign="center")
        self.add_widget(error_label)                            

        redo_button = Button(background_normal="./assets/image/redo_button_up.png",
                             background_down="./assets/image/redo_button_down.png",
                             size_hint=(None, None), size=(410, 137), pos=(307, 120),
                             on_press=self.redo_button_pressed
                             )
        self.add_widget(redo_button)

    def redo_button_pressed(self, instance):
        self.manager.current = CaptureScreen.NAME
        self.manager.remove_widget(self)


class CaptureScreen(Screen):
    NAME = "capture"
    cam: Cam

    countdown_label: Label
    countdown_second: int
    time_since_last_countdown: int
    ran_first_update: bool = False
    clock_scheduled: bool = False

    def __init__(self):
        super().__init__(name=CaptureScreen.NAME)
        self.cam = Cam()
        self.size = (1024, 600)
        self.add_widget(LiveView(self.cam, size=(1024, 683),
                                 size_hint=(None, None), pos=(0, -41)))
        self.countdown_label = Label(text="10", font_size='180sp', outline_width=6, outline_color=(
            0, 0, 0, 1), color=(1, 1, 1, 1), pos_hint={'center_x': .5, 'center_y': .5})
        self.add_widget(self.countdown_label)

    def capture_photo(self):
        try:
            file_name = self.cam.capture_image()
            self.manager.add_widget(PreviewScreen(file_name))
            self.manager.current = PreviewScreen.NAME
        except:
            self.manager.add_widget(CaptureErrorScreen())
            self.manager.current = CaptureErrorScreen.NAME
            Window.clearcolor = (0.1, 0.1, 0.1, 1)
            

    def on_enter(self):
        if not self.clock_scheduled:
            Clock.schedule_interval(self.update, 1.0 / 24.0)
            self.clock_scheduled = True
        self.countdown_label.text = "10"
        self.ran_first_update = False
        self.countdown_second = 10
        self.time_since_last_countdown = 0

    def update(self, dt):
        if self.ran_first_update:
            self.time_since_last_countdown += dt
        if self.time_since_last_countdown >= 1.0 and self.countdown_second > 0:
            self.time_since_last_countdown = 0
            self.countdown_second -= 1
            self.countdown_label.text = str(self.countdown_second)
            if self.countdown_second == 0:
                self.capture_photo()
        if self.cam.camera is not None and self.countdown_second > 0:
            self.countdown_label.opacity = 1
        else:
            self.countdown_label.opacity = 0
        self.ran_first_update = True


class IdleScreen(Screen):
    NAME = "idle"

    def __init__(self):
        super().__init__(name=IdleScreen.NAME)
        Window.clearcolor = (0.1, 0.1, 0.1, 1)
        photo_button = Button(background_normal="./assets/image/take_photo_button_up.png",
                              background_down="./assets/image/take_photo_button_down.png",
                              size_hint=(None, None), size=(621, 137), pos_hint={'center_x': .5, 'center_y': .5},
                              on_press=self.capture_photo_pressed
                              )
        self.add_widget(photo_button)

    def capture_photo_pressed(self, instance):
        self.manager.current = CaptureScreen.NAME


class LiveView(Widget):
    cam: Cam
    image_view: Image
    failed_connection_time = 0

    def __init__(self, slr, **kwargs):
        super().__init__(**kwargs)
        self.cam = slr
        self.image_view = Image(size=self.size, pos=self.pos)
        self.add_widget(self.image_view)
        self.message_label = Label()
        self.message_label.opacity = 0
        self.message_label.center = self.image_view.center
        self.message_label.color = (0, 0, 0, 1)
        self.add_widget(self.message_label)
        Clock.schedule_interval(self.update, 1.0 / 24.0)

    def update(self, dt):
        if not self.cam.capturing_image and time() - self.failed_connection_time > 2:
            try:
                img_data = self.cam.capture_preview_image()
                img = CoreImage(BytesIO(img_data), ext='jpg')
                self.image_view.texture = img.texture
                self.message_label.opacity = 0
            except CamInitializationException as ex:
                self.message_label.opacity = 1
                self.message_label.text = "Failed to initialize camera"
                self.failed_connection_time = time()


class MainApp(App):
    screen_manager: ScreenManager

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.screen_manager = ScreenManager()
        self.screen_manager.add_widget(IdleScreen())
        self.screen_manager.add_widget(CaptureScreen())
        self.screen_manager.current = IdleScreen.NAME

    def build(self):
        return self.screen_manager


if __name__ == "__main__":
    KivyConfig.set('graphics', 'width', '1024')
    KivyConfig.set('graphics', 'height', '600')
    Window.size = (1024, 600)
    MainApp().run()
    # printer.print_printers()
    # p = printer.Printer("Canon_MX920_series")
    # p.print_attributes()
    # print(p.get_printer_state())
    # p.cancel_all_jobs()
    # print(p.get_printer_state())
    # p.print_file("/home/ryan/Desktop/test.txt")
