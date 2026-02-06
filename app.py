"""
Nexora Control Panel - Professional Facebook Multi-Page Posting & Scheduling
Integrated Nexora Suite & Nexora Investments Management System
"""
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import requests
import os
import time
import threading
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "nexora-secure-key-2024")

# Import Nexora modules
import visa as nexora_suite
import tour as nexora_investments
import management as nexora_management

# Global state for background posting tasks
posting_threads = {}
posting_status = {}

def get_user_pages(user_token):
    """Fetch accessible pages from Facebook Graph API"""
    url = "https://graph.facebook.com/v17.0/me/accounts"
    resp = requests.get(url, params={"access_token": user_token})
    resp.raise_for_status()
    data = resp.json()
    pages = {}
    for p in data.get("data", []):
        pages[p["id"]] = {"name": p.get("name"), "page_token": p.get("access_token")}
    return pages

def post_to_page(page_id, page_token, message, image_url=None):
    """Post message (and optional image) to a Facebook page"""
    url = f"https://graph.facebook.com/{page_id}/feed"
    data = {"message": message, "access_token": page_token}
    if image_url:
        data["link"] = image_url
    resp = requests.post(url, data=data)
    return resp

def run_posting_loop(user_token, selected_pages, message, repeats, interval, module="direct"):
    """Run posting in a background thread"""
    try:
        pages = get_user_pages(user_token)
        results = []
        
        for r in range(max(1, repeats)):
            for pid in selected_pages:
                page = pages.get(pid)
                if not page:
                    results.append({"page_id": pid, "status": "page_not_found"})
                    continue
                
                try:
                    resp = post_to_page(pid, page["page_token"], message)
                    resp.raise_for_status()
                    results.append({
                        "page_id": pid,
                        "page_name": page.get("name"),
                        "status": "success",
                        "timestamp": datetime.now().isoformat()
                    })
                except Exception as e:
                    results.append({
                        "page_id": pid,
                        "page_name": page.get("name"),
                        "status": "error",
                        "error": str(e)
                    })
            
            if r < repeats - 1:
                time.sleep(max(1, interval))
        
        posting_status[module] = {
            "status": "completed",
            "results": results,
            "completed_at": datetime.now().isoformat()
        }
    except Exception as e:
        posting_status[module] = {
            "status": "error",
            "error": str(e),
            "completed_at": datetime.now().isoformat()
        }

@app.route("/")
def dashboard():
    """Main dashboard"""
    env_token = os.environ.get("FB_USER_TOKEN", "")
    return render_template("dashboard.html", user_token=env_token, posted=posting_status)

@app.route("/pages", methods=["GET", "POST"])
def list_pages():
    """List pages for provided token.

    GET: try to use `FB_USER_TOKEN` environment variable and show pages.
    POST: accept `user_token` from a form (existing behavior).
    """
    if request.method == "POST":
        user_token = request.form.get("user_token", "").strip()
    else:
        # GET - prefer an environment-provided token so the nav link works
        user_token = os.environ.get("FB_USER_TOKEN", "").strip()

    if not user_token:
        flash("❌ Please provide a Facebook user access token")
        return redirect(url_for("dashboard"))

    try:
        pages = get_user_pages(user_token)
        if not pages:
            flash("⚠️ No pages found. Check your token permissions.")
        return render_template("pages.html", pages=pages, user_token=user_token)
    except requests.HTTPError as e:
        flash(f"❌ Token Error: {e}")
        return redirect(url_for("dashboard"))

@app.route("/post", methods=["POST"])
def post_pages():
    """Show preview of pages to post to"""
    user_token = request.form.get("user_token", "").strip()
    message = request.form.get("message", "").strip()
    selected = request.form.getlist("pages")
    
    if not user_token:
        flash("❌ Token is required")
        return redirect(url_for("dashboard"))
    
    if not selected:
        flash("❌ Please select at least one page to post to")
        return redirect(url_for("dashboard"))
    
    if not message:
        flash("❌ Message content is required")
        return redirect(url_for("dashboard"))
    
    try:
        repeats = int(request.form.get("repeats", 1))
    except ValueError:
        repeats = 1
    
    try:
        interval = int(request.form.get("interval", 60))
    except ValueError:
        interval = 60
    
    # Get page details
    try:
        pages = get_user_pages(user_token)
    except requests.HTTPError as e:
        flash(f"❌ Failed to fetch pages: {e}")
        return redirect(url_for("dashboard"))
    
    # Build selected pages dict with names
    selected_pages = {pid: pages.get(pid, {}).get("name", f"Page {pid}") for pid in selected if pid in pages}
    
    if not selected_pages:
        flash("❌ Selected pages not found")
        return redirect(url_for("dashboard"))
    
    return render_template(
        "confirm_posting.html",
        user_token=user_token,
        message=message,
        selected_pages=selected_pages,
        repeats=repeats,
        interval=interval
    )

@app.route("/post/execute", methods=["POST"])
def execute_posting():
    """Execute the actual posting after confirmation"""
    user_token = request.form.get("user_token", "").strip()
    message = request.form.get("message", "").strip()
    selected = request.form.getlist("pages")
    
    if not user_token or not selected or not message:
        flash("❌ Invalid posting data")
        return redirect(url_for("dashboard"))
    
    try:
        repeats = int(request.form.get("repeats", 1))
    except ValueError:
        repeats = 1
    
    try:
        interval = int(request.form.get("interval", 60))
    except ValueError:
        interval = 60
    
    # Start posting in background
    module = "direct_posting"
    thread = threading.Thread(
        target=run_posting_loop,
        args=(user_token, selected, message, repeats, interval, module),
        daemon=True
    )
    thread.start()
    posting_threads[module] = thread
    posting_status[module] = {"status": "running", "started_at": datetime.now().isoformat()}
    
    flash(f"✅ Posting started to {len(selected)} page(s)")
    return redirect(url_for("dashboard"))

@app.route("/nexora/suite", methods=["GET", "POST"])
def nexora_suite_control():
    """Control Nexora Suite (Visa Services)"""
    if request.method == "POST":
        action = request.form.get("action")
        if action == "start":
            thread = threading.Thread(target=nexora_suite.run, daemon=True)
            thread.start()
            posting_threads["nexora_suite"] = thread
            posting_status["nexora_suite"] = {
                "status": "running",
                "started_at": datetime.now().isoformat()
            }
            flash("✅ Nexora Suite posting started")
        elif action == "stop":
            nexora_suite.stop()
            posting_status["nexora_suite"] = {
                "status": "stopped",
                "stopped_at": datetime.now().isoformat()
            }
            flash("⏸️ Nexora Suite posting stopped")
        return redirect(url_for("nexora_suite_control"))
    
    status = posting_status.get("nexora_suite", {"status": "idle"})
    return render_template("nexora_suite.html", status=status)

@app.route("/nexora/investments", methods=["GET", "POST"])
def nexora_investments_control():
    """Control Nexora Investments (Travel & Investment)"""
    if request.method == "POST":
        action = request.form.get("action")
        if action == "start":
            thread = threading.Thread(target=nexora_investments.run, daemon=True)
            thread.start()
            posting_threads["nexora_investments"] = thread
            posting_status["nexora_investments"] = {
                "status": "running",
                "started_at": datetime.now().isoformat()
            }
            flash("✅ Nexora Investments posting started")
        elif action == "stop":
            nexora_investments.stop()
            posting_status["nexora_investments"] = {
                "status": "stopped",
                "stopped_at": datetime.now().isoformat()
            }
            flash("⏸️ Nexora Investments posting stopped")
        return redirect(url_for("nexora_investments_control"))
    
    status = posting_status.get("nexora_investments", {"status": "idle"})
    return render_template("nexora_investments.html", status=status)


@app.route("/nexora/management", methods=["GET", "POST"])
def nexora_management_control():
    """Control Nexora Management (Announcements & Admin)"""
    if request.method == "POST":
        action = request.form.get("action")
        if action == "start":
            thread = threading.Thread(target=nexora_management.run, daemon=True)
            thread.start()
            posting_threads["nexora_management"] = thread
            posting_status["nexora_management"] = {
                "status": "running",
                "started_at": datetime.now().isoformat()
            }
            flash("✅ Nexora Management posting started")
        elif action == "stop":
            nexora_management.stop()
            posting_status["nexora_management"] = {
                "status": "stopped",
                "stopped_at": datetime.now().isoformat()
            }
            flash("⏸️ Nexora Management posting stopped")
        return redirect(url_for("nexora_management_control"))
    
    status = posting_status.get("nexora_management", {"status": "idle"})
    return render_template("nexora_management.html", status=status)


@app.route("/nexora/management/post_now", methods=["POST"])
def nexora_management_post_now():
    """Trigger a single immediate post from the management module."""
    try:
        success = nexora_management.post_once()
        if success:
            flash("✅ Management post sent")
        else:
            flash("❌ Failed to send management post (check images/posts files)")
    except Exception as e:
        flash(f"❌ Error posting: {e}")
    return redirect(url_for("nexora_management_control"))


@app.route("/nexora/management/manual", methods=["GET"])
def nexora_management_manual():
    """Show manual UI for management posts where user can preview and send specific posts."""
    try:
        posts = nexora_management.load_posts()
    except Exception:
        posts = []
    return render_template("management_manual.html", posts=posts)


@app.route("/nexora/management/post/<int:idx>", methods=["POST"])
def nexora_management_post_index(idx):
    """Trigger posting of a specific management post by index."""
    try:
        success = nexora_management.post_specific(idx)
        if success:
            flash("✅ Management post sent")
        else:
            flash("❌ Failed to send management post (check images/posts files)")
    except Exception as e:
        flash(f"❌ Error posting: {e}")
    return redirect(url_for("nexora_management_manual"))

@app.route("/api/status")
def api_status():
    """API endpoint for live status"""
    return jsonify(posting_status)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
