"""Nexora Suite - Professional Immigration & Visa Services Posting Module"""
import requests, time, random, os, json
from threading import Event

stop_event = Event()
# Use environment variable or default
ACCESS_TOKEN = os.environ.get("FB_PAGE_TOKEN", "EAAT3Q4oZCLo0BO5C8QjWvvtOXLE9gT4g0F8i2hU9Snpf6c8T2hWul5BXsmgOi8wQGapJE41NkspbRxDhO21E9G1jv9yRr2WVeA7uJ5RVm73bR5IUHfts98FZAgzqp61HeM2G3s3xDdYXEL98ZBsXrIZCZCGHMdE0H98T1oiWOI1SwsTCZBS23sBxcB8SdZAZA1Yr3D5sQDWxAviOJFaEgQZDZD")
PAGE_ID = os.environ.get("NEXORA_SUITE_PAGE_ID", "967550829768297")  # Nexora Suite
IMAGE_FOLDER = "images"
POST_INTERVAL = 30 * 60
FB_API_URL = f"https://graph.facebook.com/v19.0/{PAGE_ID}/photos"
POSTS_FILE = "posts/visa_posts.json"
MODULE_NAME = "Nexora Suite"

def load_posts():
    if not os.path.exists(POSTS_FILE):
        return []
    with open(POSTS_FILE, 'r') as f:
        return json.load(f)

def post_on_facebook(message, image_filename):
    path = os.path.join(IMAGE_FOLDER, image_filename)
    if not os.path.exists(path):
        print(f"[{MODULE_NAME}] Image not found: {path}")
        return False

    try:
        with open(path, 'rb') as img:
            files = {'source': (image_filename, img, 'image/jpeg')}
            data = {"message": message, "access_token": ACCESS_TOKEN}
            res = requests.post(FB_API_URL, files=files, data=data).json()
            success = "id" in res
            print(f"[{MODULE_NAME}] {'✅ Posted' if success else '❌ Failed:'} {res}")
            return success
    except Exception as e:
        print(f"[{MODULE_NAME}] Error: {e}")
        return False

def run():
    """Run Nexora Suite posting cycle"""
    posts = load_posts()
    if not posts:
        print(f"[{MODULE_NAME}] No posts to schedule")
        return
    random.shuffle(posts)
    while not stop_event.is_set():
        for post in posts:
            if stop_event.is_set():
                break
            post_on_facebook(post["message"], post["image_filename"])
            time.sleep(POST_INTERVAL)

def stop():
    """Stop Nexora Suite posting cycle"""
    stop_event.set()
