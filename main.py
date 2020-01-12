from io import BytesIO
from kivy.app import App
from kivy.clock import Clock
from kivy.core.image import Image as CoreImage
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.widget import Widget

from cam import Cam
import printer


class LiveView(Widget):
    cam: Cam
    image_view: Image

    def __init__(self, slr, **kwargs):
        super().__init__(**kwargs)
        self.cam = slr
        self.image_view = Image(size=self.size, pos=self.pos)
        self.add_widget(self.image_view)
        Clock.schedule_interval(self.update, 1.0 / 24.0)

    def update(self, dt):
        if not self.cam.capturing_image:
            img_data = self.cam.capture_preview_image()
            img = CoreImage(BytesIO(img_data), ext='jpg')
            self.image_view.texture = img.texture


class MainApp(App):
    slr: Cam

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.slr = Cam()

    def build(self):
        layout = FloatLayout(size=(720, 640))
        photo_button = Button(text="Take Photo", pos=(0, 0), size_hint=(1, 0.1), on_press=self.capture_photo_pressed)
        layout.add_widget(photo_button)
        layout.add_widget(LiveView(self.slr, size=(720, 480), pos=(0, 160)))
        return layout

    def capture_photo_pressed(self, instance):
        self.slr.capture_image()


if __name__ == "__main__":
    MainApp().run()
    # printer.print_printers()
    # p = printer.Printer("MX920LAN")
    # p.print_attributes()
