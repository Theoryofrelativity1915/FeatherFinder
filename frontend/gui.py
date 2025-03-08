from kivy.app import App
from kivy.uix.camera import Camera
from kivy.graphics import Color, Ellipse
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.behaviors import ButtonBehavior
from backend.model.inference import infer


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

    def take_picture(self, _):
        image_as_texture = self.camera.texture

        predicted_bird = infer(image_as_texture)
        print(predicted_bird)


class CameraApp(App):
    def build(self):
        return CameraAppLayout()


def start_gui():
    CameraApp().run()