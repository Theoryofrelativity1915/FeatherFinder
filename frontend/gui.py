from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.camera import Camera
from kivy.graphics import Color, Ellipse
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior
import os


class CircularButton(ButtonBehavior, Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(1, 1, 1, 0.1)  # Semi-transparent white
            self.circle = Ellipse(size=self.size, pos=self.pos)
        self.bind(pos=self.update_circle, size=self.update_circle)

    def update_circle(self, *args):
        self.circle.size = self.size
        self.circle.pos = self.pos


class CameraAppLayout(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.camera = Camera(play=True)
        self.camera.size_hint = (1, 1)
        self.camera.allow_stretch = True
        self.add_widget(self.camera)

        self.capture_button = CircularButton(
            size_hint=(None, None),
            size=(100, 100),
            pos_hint={'center_x': 0.5, 'bottom': 0.1},
        )
        self.capture_button.bind(on_press=self.take_picture)
        self.add_widget(self.capture_button)

    def take_picture(self, instance):
        pictures_dir = os.path.expanduser("~") + "/Pictures"
        if not os.path.exists(pictures_dir):
            os.makedirs(pictures_dir)

        file_path = os.path.join(pictures_dir, "captured_image.png")
        self.camera.export_to_png(file_path)
        print(f"Picture saved at: {file_path}")


class CameraApp(App):
    def build(self):
        return CameraAppLayout()


if __name__ == "__main__":
    CameraApp().run()