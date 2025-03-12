from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.camera import Camera
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
import sqlite3
import os


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
        upload_button = Button(text="Upload Photo", on_press=self.go_to_upload)
        self.layout.add_widget(upload_button)
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

    def go_to_upload(self, instance):
        self.manager.current = 'upload'


class CameraScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        self.camera = Camera(index=0, play=True, resolution=(640, 480))
        self.layout.add_widget(self.camera)
        save_button = Button(text='Capture', on_press=self.capture_photo)
        self.layout.add_widget(save_button)
        back_button = Button(text="Back to Leaderboard", on_press=self.go_to_leaderboard)
        self.layout.add_widget(back_button)
        self.add_widget(self.layout)

    def capture_photo(self, instance):
        username = self.manager.get_screen('leaderboard').username
        update_bird_count(username, 1)
        photo_path = os.path.join(os.getcwd(), 'bird_photo.png')
        self.camera.export_to_png(photo_path)
        print(f"Photo saved at {photo_path}")

    def go_to_leaderboard(self, instance):
        self.manager.current = 'leaderboard'


class FileUploadScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        self.file_chooser = FileChooserIconView()
        self.layout.add_widget(self.file_chooser)
        select_button = Button(text='Select', on_press=self.load_selected_photo)
        self.layout.add_widget(select_button)
        self.image_display = Image()
        self.layout.add_widget(self.image_display)
        back_button = Button(text="Back to Leaderboard", on_press=self.go_to_leaderboard)
        self.layout.add_widget(back_button)
        self.add_widget(self.layout)

    def load_selected_photo(self, instance):
        selected = self.file_chooser.selection
        if selected:
            username = self.manager.get_screen('leaderboard').username
            update_bird_count(username, 1)
            self.image_display.source = selected[0]
            self.image_display.reload()

    def go_to_leaderboard(self, instance):
        self.manager.current = 'leaderboard'


class BirdWatcherApp(App):
    def build(self):
        init_db()
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(LeaderboardScreen(name='leaderboard'))
        sm.add_widget(CameraScreen(name='camera'))
        sm.add_widget(FileUploadScreen(name='upload'))
        return sm


if __name__ == '__main__':
    BirdWatcherApp().run()