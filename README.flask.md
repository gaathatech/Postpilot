# Nexora Control Panel

Professional in-house Facebook multi-page management system featuring:
- **Nexora Suite** - Immigration & Visa Services automation
- **Nexora Investments** - Travel & Investment Opportunities automation
- **Manual Posting** - Direct posting to multiple pages with scheduling controls

## Quick Start

### 1. Install Dependencies

```bash
python3 -m pip install -r requirements.txt
```

### 2. Run the Application

```bash
export FLASK_APP=app.py
export FB_USER_TOKEN="your_facebook_user_token_here"  # Optional: prefill token on load
flask run --host=0.0.0.0 --port=5000
```

### 3. Access the Dashboard

Open http://localhost:5000 in your browser.

## Features

### 📊 Dashboard
- Quick overview of all modules and running tasks
- Recent activity log
- Navigation to all control panels

### 🏢 Nexora Suite
Automated posting system for professional immigration & visa services:
- Posts from `posts/visa_posts.json`
- Images from `images/` folder
- 30-minute default interval between posts
- Start/Stop controls

### 💼 Nexora Investments
Automated posting system for travel & investment opportunities:
- Posts from `posts/tour_posts.json`
- Images from `images/` folder
- 30-minute default interval between posts
- Start/Stop controls

### 📱 Manual Posting
Post custom messages to selected pages:
- Token-based page discovery
- Multi-page selection
- Custom message content
- Repeat scheduling with configurable intervals

## Environment Variables

```bash
FB_USER_TOKEN        # Facebook user access token (optional, for prefill)
FB_PAGE_TOKEN        # Facebook page access token (used by modules)
NEXORA_SUITE_PAGE_ID          # Page ID for visa module
NEXORA_INVESTMENTS_PAGE_ID    # Page ID for tour module
FLASK_SECRET         # Secret key for sessions
PORT                 # Server port (default: 5000)
```

## Configuration Files

- `posts/visa_posts.json` - Visa/Suite posts (message + image_filename)
- `posts/tour_posts.json` - Investment/Tour posts (message + image_filename)
- `images/` - All images referenced in post files

Example post structure:
```json
[
  {
    "message": "Your visa post message here",
    "image_filename": "nz.jpeg"
  }
]
```

## Security Notes

⚠️ **Do NOT commit tokens to version control**

- Use environment variables for all tokens
- Create a `.env` file locally (never commit to git):
  ```
  FB_USER_TOKEN=your_token_here
  FB_PAGE_TOKEN=your_page_token_here
  ```
- Load with: `source .env` before running

## Module Structure

Each module (Nexora Suite & Investments) has:
- `run()` - Start automated posting cycle
- `stop()` - Stop the posting cycle
- `load_posts()` - Load posts from JSON file
- `post_on_facebook()` - Handle the actual posting

Modules use threading for background operation.

## Troubleshooting

**Token Error (400 - Bad Request)?**
- Ensure your token is valid and complete
- Check token permissions include page management
- Tokens may expire; get a new access token from Facebook Developer Console

**No Pages Found?**
- Verify token has `pages_read_engagement` and `pages_manage_posts` permissions
- Ensure pages are admin-managed by the token account

**Posts Not Showing?**
- Check `posts/` JSON files exist and are valid
- Verify image filenames match files in `images/` folder
- Check `image_filename` field is spelled correctly in JSON

## Production Deployment

For production:
1. Set `FLASK_ENV=production`
2. Use a production WSGI server (gunicorn, etc.)
3. Implement proper database for task history
4. Add OAuth authentication for token management
5. Use environment-based configuration
6. Set up logging and monitoring

Example with Gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

**Nexora Control Panel** - Built for professional in-house operations.

