from kivy.app import App
from kivy.uix.widget import Widget


class RootWidget(Widget):
    pass


class PhotoBoothApp(App):
    def build(self):
        return RootWidget()


if __name__ == '__main__':
    PhotoBoothApp().run()