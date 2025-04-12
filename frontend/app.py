from kivy.app import App
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.camera import Camera
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.progressbar import ProgressBar
from backend.model.inference import infer
import backend.db.utils as db
from kivy.graphics import PushMatrix, PopMatrix, Rotate
import platform


class LoadingScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation = 'vertical')
        self.loading_Label = Label(text= 'Loading . . . ')
        self.layout.add_widget(self.loading_Label)
        self.load_bar = ProgressBar(max = 500, size_hint=(0.9, 0.1),
                                    height = 300, pos_hint={'center_x': 0.5})
        self.layout.add_widget(self.load_bar)
        self.add_widget(self.layout)
        self.progress = 0
        Clock.schedule_interval(self.update, 0.01)

    def update(self, _):
        if self.progress < self.load_bar.max:
            self.progress += 1
            self.load_bar.value = self.progress
        else:
            self.manager.current = 'login'
            Clock.unschedule(self.update)

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = FloatLayout()

        # Create a contained box for login elements with fixed size
        login_container = BoxLayout(
            orientation='vertical',
            size_hint=(None, None),
            size=(200, 150),  # Reduced size
            pos_hint={'center_x': 0.5, 'top': 0.9},  # Changed to position near top
            spacing=15  # Added spacing between elements
        )

        # Title label
        login_label = Label(
            text="Log In",
            font_size=24,
            size_hint_y=None,
            height=40
        )

        # Username input
        self.username_input = TextInput(
            hint_text='Enter Username',
            size_hint_y=100,
            height=30,
            multiline=False  # Single line input
        )

        # Login button
        self.login_button = Button(
            text='Login',
            size_hint_y=None,
            height=40
        )
        self.login_button.bind(on_press=self.login)

        # Add widgets to container
        login_container.add_widget(login_label)
        login_container.add_widget(self.username_input)
        login_container.add_widget(self.login_button)

        # Add container to main layout
        self.layout.add_widget(login_container)
        self.add_widget(self.layout)

    def login(self, _):
        username = self.username_input.text.strip()
        if username:
            App.get_running_app().username = username
            db.insert_user(username)
            self.manager.current = 'camera'

class LeaderboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        self.user_label = Label(text="", font_size=16)
        self.layout.add_widget(self.user_label)
        self.leaderboard_label = Label(text="Top 5 Bird Identifiers:\n", font_size=18)
        self.layout.add_widget(self.leaderboard_label)
        self.refresh_button = Button(text="Refresh Leaderboard", on_press=self.update_leaderboard)
        self.layout.add_widget(self.refresh_button)
        nav_button = Button(text="Go to Camera", on_press=self.go_to_camera)
        self.layout.add_widget(nav_button)
        self.add_widget(self.layout)

    def update_leaderboard(self, _):
        username = App.get_running_app().username
        self.user_label.text = f"Logged in as: {username}"
        top_users = db.get_top_users()
        leaderboard_text = "Top 5 Bird Identifiers:\n" + "\n".join(
            [f"{i + 1}. {user} - Birds identified: {count}" for i, (user, count) in enumerate(top_users)])
        user_rank, user_count = db.get_user_stats(username)
        leaderboard_text += f"\n\nYour ranking:\n{user_rank}. Birds identified: {user_count}"
        self.leaderboard_label.text = leaderboard_text

    def go_to_camera(self, _):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'camera'
        self.manager.transition = SlideTransition(direction='left')

class CircularButton(ButtonBehavior, Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(1, 1, 1, 0.3)  # Semi-transparent white
            self.circle = Ellipse(size=self.size, pos=self.pos)
        self.bind(pos=self.update_circle, size=self.update_circle)

    def update_circle(self, *args):
        self.circle.size = self.size
        self.circle.pos = self.pos

# Custom Rectangle Button
class RectangleButton(ButtonBehavior, Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.label = Label(text='Leaderboard')
        self.label.pos = (self.center_x - self.label.width / 2, self.center_y - self.label.height / 2)

        with self.canvas:
            Color(1, 1, 1, 0.3)  # Semi-transparent white
            self.rectangle = Rectangle(size=self.size, pos=self.pos)
        self.add_widget(self.label)
        self.bind(pos=self.update_rectangle, size=self.update_rectangle)

    def update_rectangle(self, *args):
        self.rectangle.size = self.size
        self.rectangle.pos = self.pos

from kivy.uix.camera import Camera
from kivy.core.camera import Camera as CoreCamera

class CameraScreen(Screen):
    def __init__(self, leaderboard=None, **kwargs):
        super().__init__(**kwargs)
        self.layout = FloatLayout()
        self.leaderboard = leaderboard
        try:
            self.camera = Camera(play=True)
            self.camera.size_hint = (1, 1)
            self.camera.allow_stretch = True


            is_mac = platform.system() == 'Darwin'
            if is_mac:
                # Add rotation transformation
                with self.camera.canvas.before:
                    PushMatrix()
                    self.rot = Rotate()
                    self.rot.angle = -90  # 90 degrees rotation
                with self.camera.canvas.after:
                    PopMatrix()

            # Function to update rotation origin
            def update_rotation(*args):
                self.rot.origin = (self.camera.center_x, self.camera.center_y)

            # Schedule initial update and bind to size/position changes
            Clock.schedule_once(update_rotation, 0)
            self.camera.bind(size=update_rotation, pos=update_rotation)

        except:
            self.camera = Label(text="Camera not available", size_hint=(1, 1))

        self.layout.add_widget(self.camera)

        self.capture_button = CircularButton(
            size_hint=(None, None),
            size=(100, 100),
            pos_hint={'center_x': 0.5, 'bottom': 0.1},
        )
        self.capture_button.bind(on_press=self.capture_photo)
        self.layout.add_widget(self.capture_button)

        self.bird_label = Label(text="", pos_hint = {"center_x": 0.5, "center_y": 0.2})
        self.layout.add_widget(self.bird_label)

        self.leaderboard_button = RectangleButton(
            size_hint=(None, None),
            size=(200, 100),
            pos_hint={'x': 0.0, 'bottom': 0.1},
        )
        self.leaderboard_button.bind(on_press=self.go_to_leaderboard)
        self.layout.add_widget(self.leaderboard_button)
        self.add_widget(self.layout)

    def go_to_leaderboard(self, _):
        self.manager.current = "leaderboard"
        self.leaderboard.update_leaderboard(None)

    def capture_photo(self, _):
        self.bird_label.text = ""
        image_as_texture = self.camera.texture
        predicted_bird = infer(image_as_texture)
        if predicted_bird is not None:
            username = App.get_running_app().username
            db.update_seen_birds(username, predicted_bird)
            self.bird_label.text = predicted_bird

class BirdWatcherApp(App):
    def build(self):
        db.init_db()
        sm = ScreenManager()
        sm.add_widget(LoadingScreen(name='loading'))
        sm.add_widget(LoginScreen(name='login'))
        leaderboard_screen = LeaderboardScreen(name='leaderboard')
        sm.add_widget(leaderboard_screen)
        sm.add_widget(CameraScreen(leaderboard=leaderboard_screen, name='camera'))
        sm.current = 'loading'
        return sm

def start_app():
    BirdWatcherApp().run()
