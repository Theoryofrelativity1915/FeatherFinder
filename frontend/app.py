from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.camera import Camera
from kivy.graphics import Color, Ellipse
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.behaviors import ButtonBehavior
from backend.model.inference import infer
import sqlite3

# Database setup
def init_db():
    conn = sqlite3.connect("birdwatcher.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            bird_count INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def update_bird_count(username, count):
    conn = sqlite3.connect("birdwatcher.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, bird_count) VALUES (?, ?) ON CONFLICT(username) DO UPDATE SET bird_count = bird_count + ?",
        (username, count, count))
    conn.commit()
    conn.close()

def get_top_users():
    conn = sqlite3.connect("birdwatcher.db")
    cursor = conn.cursor()
    cursor.execute("SELECT username, bird_count FROM users ORDER BY bird_count DESC LIMIT 5")
    users = cursor.fetchall()
    conn.close()
    return users

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        self.username_input = TextInput(hint_text='Enter Username')
        self.layout.add_widget(self.username_input)
        self.login_button = Button(text='Login', on_press=self.login)
        self.layout.add_widget(self.login_button)
        self.add_widget(self.layout)

    def login(self, instance):
        username = self.username_input.text.strip()
        if username:
            self.manager.current = 'leaderboard'
            self.manager.get_screen('leaderboard').set_user(username)
            conn = sqlite3.connect("birdwatcher.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username) VALUES (?) ON CONFLICT(username) DO NOTHING", (username,))
            conn.commit()
            conn.close()

class LeaderboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.username = ""
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
        self.update_leaderboard()

    def set_user(self, username):
        self.username = username
        self.user_label.text = f"Logged in as: {username}"

    def update_leaderboard(self, instance=None):
        top_users = get_top_users()
        leaderboard_text = "Top 5 Bird Identifiers:\n" + "\n".join(
            [f"{idx + 1}. {user} - {count}" for idx, (user, count) in enumerate(top_users)])
        self.leaderboard_label.text = leaderboard_text

    def go_to_camera(self, instance):
        self.manager.current = 'camera'

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

class CameraScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = FloatLayout()
        self.camera = Camera(play=True)
        self.camera.size_hint = (1, 1)
        self.camera.allow_stretch = True
        self.layout.add_widget(self.camera)

        self.capture_button = CircularButton(
            size_hint=(None, None),
            size=(100, 100),
            pos_hint={'center_x': 0.5, 'bottom': 0.1},
        )
        self.capture_button.bind(on_press=self.capture_photo)
        self.layout.add_widget(self.capture_button)
        self.add_widget(self.layout)

    def capture_photo(self, _):
        image_as_texture = self.camera.texture
        predicted_bird = infer(image_as_texture)
        username = self.manager.get_screen('leaderboard').username
        update_bird_count(username, 1)
        print(predicted_bird)

class BirdWatcherApp(App):
    def build(self):
        init_db()
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(LeaderboardScreen(name='leaderboard'))
        sm.add_widget(CameraScreen(name='camera'))
        return sm

if __name__ == '__main__':
    BirdWatcherApp().run()
