from io import BytesIO
from kivy.app import App
from kivy.clock import Clock
from kivy.core.image import Image as CoreImage
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy import Config as KivyConfig
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition

from cam import Cam, CamInitializationException
import printer


class CaptureScreen(Screen):
    NAME = "capture"
    cam: Cam

    def __init__(self):
        super().__init__(name=CaptureScreen.NAME)
        self.cam = Cam()
        self.size = (1024, 600)
        photo_button = Button(text="Take Photo", pos=(0, 0), size_hint=(1, 0.1), on_press=self.capture_photo_pressed)
        self.add_widget(photo_button)
        self.add_widget(LiveView(self.cam, size=(720, 480), pos=(152, 80)))

    def capture_photo_pressed(self, instance):
        try:
            self.cam.capture_image()
        except:
            # TODO
            pass


class IdleScreen(Screen):
    NAME = "idle"

    def __init__(self):
        super().__init__(name=IdleScreen.NAME)
        photo_button = Button(text="Take Photo", pos=(0, 0), size_hint=(1, 0.1), on_press=self.capture_photo_pressed)
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
        self.screen_manager = ScreenManager(transition=FadeTransition())
        self.screen_manager.add_widget(IdleScreen())
        self.screen_manager.add_widget(CaptureScreen())
        self.screen_manager.current = IdleScreen.NAME

    def build(self):
        return self.screen_manager


if __name__ == "__main__":
    # KivyConfig.set('graphics', 'width', '1024')
    # KivyConfig.set('graphics', 'height', '600')
    # MainApp().run()
    printer.print_printers()
    p = printer.Printer("Canon_MX920_series")
    p.print_attributes()
    print(p.get_printer_state())
    p.cancel_all_jobs()
    print(p.get_printer_state())
    p.print_file("/home/ryan/Desktop/test.txt")
