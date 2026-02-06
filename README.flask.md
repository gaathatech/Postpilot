# Postpilot (Flask)

This repository now includes a small Flask app that lists Facebook Pages accessible by a user token and allows posting a message to selected pages in a simple loop.

Quick start

1. Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

2. Run (optionally export a default token):

```bash
export FB_USER_TOKEN="<your_user_token_here>"
export FLASK_APP=app.py
flask run --host=0.0.0.0 --port=5000
```

3. Open http://localhost:5000, paste your user access token (or rely on `FB_USER_TOKEN`), list pages, select which pages to post to, enter a message, and start posting.

Security and notes
- Keep your tokens private and do not commit them to version control.
- The user access token must have permission to manage pages (so the Graph API returns page access tokens via `/me/accounts`).
- This simple app posts plain messages (via `/{page_id}/feed`). For images/media use the Pages `/photos` endpoint.

This is a minimal migration from the original Kivy UI to a Flask web UI and is meant to be extended for production use.
