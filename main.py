import json
import threading
import os

from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserIconView
from kivy.properties import StringProperty, ObjectProperty

import tour
import visa
import insta

POSTS_DIR = "posts"
NZ_FILE = os.path.join(POSTS_DIR, "visa_posts.json")
TOUR_FILE = os.path.join(POSTS_DIR, "tour_posts.json")
INSTA_FILE = os.path.join(POSTS_DIR, "insta_posts.json")  # Add if you want to save insta posts similarly

def load_posts(filepath):
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except:
        return []

def save_posts(filepath, posts):
    with open(filepath, 'w') as f:
        json.dump(posts, f, indent=2)

class AddPostPopup(Popup):
    post_type = StringProperty('')
    parent_widget = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.image_path = ''
        self.description = ''
        self.delay = '10'

    def select_image(self, selection):
        if selection:
            self.image_path = selection[0]

    def save_post(self):
        desc = self.ids.desc_input.text
        delay = self.ids.delay_input.text or '10'
        self.parent_widget.add_post(self.post_type, self.image_path, desc, delay)
        self.dismiss()

class PostEditor(BoxLayout):
    def __init__(self, post_data, save_callback, remove_callback, **kwargs):
        super().__init__(orientation='vertical', size_hint_y=None, height='200dp', spacing=5, **kwargs)

        self.post_data = post_data
        self.save_callback = save_callback
        self.remove_callback = remove_callback

        self.caption_input = TextInput(text=post_data.get("message", ""), multiline=True, size_hint_y=None, height=100)
        self.image_input = TextInput(text=post_data.get("image_filename", ""), multiline=False, size_hint_y=None, height=30)

        save_btn = Button(text="💾 Save", size_hint_y=None, height=30)
        remove_btn = Button(text="❌ Delete", size_hint_y=None, height=30)

        save_btn.bind(on_press=lambda _: self.save_callback(self))
        remove_btn.bind(on_press=lambda _: self.remove_callback(self))

        self.add_widget(Label(text="📝 Caption:"))
        self.add_widget(self.caption_input)
        self.add_widget(Label(text="🖼 Image Filename:"))
        self.add_widget(self.image_input)
        self.add_widget(save_btn)
        self.add_widget(remove_btn)

    def get_data(self):
        return {
            "message": self.caption_input.text,
            "image_filename": self.image_input.text
        }

class MainPanel(TabbedPanel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.do_default_tab = False

        self.nz_posts = load_posts(NZ_FILE)
        self.tour_posts = load_posts(TOUR_FILE)
        self.insta_posts = load_posts(INSTA_FILE)

        self.insta_running = False
        self.nz_running = False
        self.tour_running = False

        self.build_controls_tab()
        self.build_post_editor_tab("NZ Posts", self.nz_posts, NZ_FILE)
        self.build_post_editor_tab("Tour Posts", self.tour_posts, TOUR_FILE)
        self.build_post_editor_tab("Insta Posts", self.insta_posts, INSTA_FILE)

    def build_controls_tab(self):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        tab = self.create_tab("Controls", layout)

        self.insta_btn = Button(text="▶ Start Insta Sync")
        self.nz_btn = Button(text="▶ Start Visa Posts")
        self.tour_btn = Button(text="▶ Start Tour Posts")

        self.insta_btn.bind(on_press=self.toggle_insta)
        self.nz_btn.bind(on_press=self.toggle_nz)
        self.tour_btn.bind(on_press=self.toggle_tour)

        run_all_btn = Button(text="▶ Run All")
        stop_all_btn = Button(text="⏹ Stop All")

        run_all_btn.bind(on_press=self.run_all_scripts)
        stop_all_btn.bind(on_press=self.stop_all_scripts)

        layout.add_widget(self.insta_btn)
        layout.add_widget(self.nz_btn)
        layout.add_widget(self.tour_btn)
        layout.add_widget(run_all_btn)
        layout.add_widget(stop_all_btn)

    def build_post_editor_tab(self, tab_name, posts, filepath):
        layout = BoxLayout(orientation='vertical', padding=10)
        scroll = ScrollView(size_hint=(1, 1))
        post_list = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10)
        post_list.bind(minimum_height=post_list.setter('height'))
        scroll.add_widget(post_list)
        layout.add_widget(scroll)

        def refresh():
            post_list.clear_widgets()
            for p in posts:
                editor = PostEditor(p, lambda w: self.save_post(w, posts, filepath, refresh), lambda w: self.delete_post(w, posts, filepath, refresh))
                post_list.add_widget(editor)

        add_btn = Button(text="➕ Add Post", size_hint_y=None, height=40)
        add_btn.bind(on_press=lambda _: self.open_add_post_popup(tab_name.lower().split()[0], posts, filepath, refresh))

        layout.add_widget(add_btn)
        refresh()
        self.create_tab(tab_name, layout)

        # Save references for popup use
        if tab_name == "NZ Posts":
            self.nz_post_list = post_list
            self.nz_refresh = refresh
            self.nz_filepath = filepath
            self.nz_posts_ref = posts
        elif tab_name == "Tour Posts":
            self.tour_post_list = post_list
            self.tour_refresh = refresh
            self.tour_filepath = filepath
            self.tour_posts_ref = posts
        elif tab_name == "Insta Posts":
            self.insta_post_list = post_list
            self.insta_refresh = refresh
            self.insta_filepath = filepath
            self.insta_posts_ref = posts

    def create_tab(self, name, content_widget):
        tab = TabbedPanelItem(text=name)
        tab.add_widget(content_widget)
        self.add_widget(tab)
        return tab

    def open_add_post_popup(self, post_type, posts, filepath, refresh):
        self.popup = AddPostPopup(post_type=post_type)
        self.popup.parent_widget = self
        self._current_add_post_data = (posts, filepath, refresh)
        self.popup.open()

    def add_post(self, post_type, image, description, delay):
        # Add post to correct list
        if post_type == "nz":
            posts, filepath, refresh = self.nz_posts_ref, self.nz_filepath, self.nz_refresh
        elif post_type == "tour":
            posts, filepath, refresh = self.tour_posts_ref, self.tour_filepath, self.tour_refresh
        elif post_type == "insta":
            posts, filepath, refresh = self.insta_posts_ref, self.insta_filepath, self.insta_refresh
        else:
            return

        new_post = {
            "message": description,
            "image_filename": image,
            "delay": delay
        }
        posts.append(new_post)
        save_posts(filepath, posts)
        refresh()

    def add_post_direct(self, posts, filepath, refresh):
        new_post = {"message": "", "image_filename": ""}
        posts.append(new_post)
        save_posts(filepath, posts)
        refresh()

    def save_post(self, widget, posts, filepath, refresh):
        index = posts.index(widget.post_data)
        posts[index] = widget.get_data()
        save_posts(filepath, posts)
        refresh()

    def delete_post(self, widget, posts, filepath, refresh):
        posts.remove(widget.post_data)
        save_posts(filepath, posts)
        refresh()

    def toggle_insta(self, instance):
        if not self.insta_running:
            self.insta_thread = threading.Thread(target=insta.run_insta_sync, daemon=True)
            self.insta_thread.start()
            self.insta_running = True
            self.insta_btn.text = "⏹ Stop Insta Sync"
        else:
            insta.stop_insta_sync()
            self.insta_running = False
            self.insta_btn.text = "▶ Start Insta Sync"

    def toggle_nz(self, instance):
        if not self.nz_running:
            self.visa_thread = threading.Thread(target=visa.run_nz, daemon=True)
            self.visa_thread.start()
            self.nz_running = True
            self.nz_btn.text = "⏹ Stop Visa Posts"
        else:
            visa.stop_nz()
            self.nz_running = False
            self.nz_btn.text = "▶ Start Visa Posts"

    def toggle_tour(self, instance):
        if not self.tour_running:
            self.tour_thread = threading.Thread(target=tour.run_tour, daemon=True)
            self.tour_thread.start()
            self.tour_running = True
            self.tour_btn.text = "⏹ Stop Tour Posts"
        else:
            tour.stop_tour()
            self.tour_running = False
            self.tour_btn.text = "▶ Start Tour Posts"

    def run_all_scripts(self, instance):
        if not self.insta_running:
            self.toggle_insta(None)
        if not self.nz_running:
            self.toggle_nz(None)
        if not self.tour_running:
            self.toggle_tour(None)

    def stop_all_scripts(self, instance):
        if self.insta_running:
            self.toggle_insta(None)
        if self.nz_running:
            self.toggle_nz(None)
        if self.tour_running:
            self.toggle_tour(None)

class PostPilotApp(App):
    def build(self):
        return MainPanel()

if __name__ == "__main__":
    PostPilotApp().run()
# This code is a Kivy application that allows users to manage and post content to Facebook and Instagram.
# It includes features to add, edit, and delete posts, as well as start and stop posting scripts for different categories.
# The application uses threading to run posting scripts in the background, ensuring a responsive UI.