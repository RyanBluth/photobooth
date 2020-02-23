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


class CaptureScreen(Screen):
    NAME = "capture"
    cam: Cam

    countdown_label: Label
    countdown_second = 10
    time_since_last_countdown = 0
    ran_first_update = False

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
            self.cam.capture_image()
        except:
            # TODO
            pass

    def on_enter(self):
        Clock.schedule_interval(self.update, 1.0 / 24.0)

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
        if not self.cam.capturing_image:
            try:
                img_data = self.cam.capture_preview_image()
                img = CoreImage(BytesIO(img_data), ext='jpg')
                self.image_view.texture = img.texture
                self.message_label.opacity = 0
            except CamInitializationException as ex:
                self.message_label.opacity = 1
                self.message_label.text = "Failed to initialize camera"


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
