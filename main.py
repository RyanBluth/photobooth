from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label


class RootWidget(Widget):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(Label(text='Hello world'))


class PhotoBoothApp(App):
    def build(self):
        return RootWidget()


if __name__ == '__main__':
    PhotoBoothApp().run()