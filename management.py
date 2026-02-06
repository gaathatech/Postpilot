"""Nexora Management - General Management & Announcements Posting Module"""
import requests, time, random, os, json
from threading import Event

stop_event = Event()
# Use environment variable or default
ACCESS_TOKEN = os.environ.get("FB_PAGE_TOKEN", "")
PAGE_ID = os.environ.get("NEXORA_MANAGEMENT_PAGE_ID", "178168346255851")
IMAGE_FOLDER = "images"
POST_INTERVAL = 30 * 60
FB_API_URL = f"https://graph.facebook.com/v19.0/{PAGE_ID}/photos"
POSTS_FILE = "posts/management_posts.json"
MODULE_NAME = "Nexora Management"

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
    """Run Nexora Management posting cycle"""
    posts = load_posts()
    if not posts:
        print(f"[{MODULE_NAME}] No posts to schedule")
        return
    random.shuffle(posts)
    while not stop_event.is_set():
        for post in posts:
            if stop_event.is_set():
                break
            post_on_facebook(post.get("message", ""), post.get("image_filename", ""))
            time.sleep(POST_INTERVAL)

def stop():
    """Stop Nexora Management posting cycle"""
    stop_event.set()


def post_once():
    """Post a single management announcement immediately (returns True on success)."""
    posts = load_posts()
    if not posts:
        print(f"[{MODULE_NAME}] No posts available to post once")
        return False
    post = random.choice(posts)
    return post_on_facebook(post.get("message", ""), post.get("image_filename", ""))


def post_specific(index):
    """Post a specific management post by index (0-based). Returns True on success."""
    posts = load_posts()
    if not posts:
        print(f"[{MODULE_NAME}] No posts available to post")
        return False
    if index < 0 or index >= len(posts):
        print(f"[{MODULE_NAME}] Invalid post index: {index}")
        return False
    post = posts[index]
    return post_on_facebook(post.get("message", ""), post.get("image_filename", ""))
