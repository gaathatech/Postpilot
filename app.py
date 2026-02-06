from flask import Flask, render_template, request, redirect, url_for, flash
import requests
import os
import time

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "change-this-secret")


def get_user_pages(user_token):
    """Return list of pages with id, name and page access token."""
    url = "https://graph.facebook.com/v17.0/me/accounts"
    resp = requests.get(url, params={"access_token": user_token})
    resp.raise_for_status()
    data = resp.json()
    pages = {}
    for p in data.get("data", []):
        # p contains id, name, access_token (page token)
        pages[p["id"]] = {"name": p.get("name"), "page_token": p.get("access_token")}
    return pages


def post_to_page(page_id, page_token, message):
    url = f"https://graph.facebook.com/{page_id}/feed"
    resp = requests.post(url, data={"message": message, "access_token": page_token})
    return resp


@app.route("/", methods=["GET", "POST"])
def index():
    # If POST, we attempt to list pages using provided user token
    if request.method == "POST":
        user_token = request.form.get("user_token", "").strip()
        if not user_token:
            flash("Provide a Facebook user access token with pages permission.")
            return redirect(url_for("index"))
        try:
            pages = get_user_pages(user_token)
        except requests.HTTPError as e:
            flash(f"Failed to fetch pages: {e}")
            return redirect(url_for("index"))

        return render_template("index.html", pages=pages, user_token=user_token)

    # GET: show token input form (prefill from env if available)
    env_token = os.environ.get("FB_USER_TOKEN", "")
    return render_template("index.html", pages=None, user_token=env_token)


@app.route("/post", methods=["POST"])
def post():
    user_token = request.form.get("user_token", "").strip()
    message = request.form.get("message", "").strip()
    selected = request.form.getlist("pages")
    if not user_token or not selected or not message:
        flash("Token, message and at least one page selection are required.")
        return redirect(url_for("index"))

    # Get pages to find page access tokens
    try:
        pages = get_user_pages(user_token)
    except requests.HTTPError as e:
        flash(f"Failed to fetch pages: {e}")
        return redirect(url_for("index"))

    # Scheduling options
    try:
        repeats = int(request.form.get("repeats", 1))
    except ValueError:
        repeats = 1
    try:
        interval = int(request.form.get("interval", 60))
    except ValueError:
        interval = 60

    results = []
    for r in range(max(1, repeats)):
        for pid in selected:
            page = pages.get(pid)
            if not page or not page.get("page_token"):
                results.append({"page_id": pid, "status": "missing_page_token"})
                continue
            resp = post_to_page(pid, page["page_token"], message)
            try:
                resp.raise_for_status()
                results.append({"page_id": pid, "status": "ok", "response": resp.json()})
            except requests.HTTPError:
                results.append({"page_id": pid, "status": "error", "response_text": resp.text})
        if r < repeats - 1:
            time.sleep(max(1, interval))

    return render_template("result.html", results=results)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
