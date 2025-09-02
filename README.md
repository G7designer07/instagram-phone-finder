# Instagram followers exporter (with login)

**IMPORTANT:** Do NOT paste your Instagram username/password into a public repo or chat. This project reads credentials from environment variables. Store them securely (Render environment variables, or local environment).

## What this does
- Logs into Instagram using `instagrapi`
- Fetches followers of a given profile
- Tries to read public phone numbers when available
- Displays results in a table and allows CSV download

## Files in this package
- `app.py` - Flask app
- `requirements.txt`
- `templates/index.html`, `templates/results.html`
- `test_login.py` - helper to test login locally and dump session JSON
- `.gitignore` (recommended to add): session_*.json

## Local testing
1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Export environment variables (replace placeholders):

   **Linux / macOS**
   ```
   export INSTAGRAM_USER="your_instagram_user"
   export INSTAGRAM_PASS="your_instagram_pass"
   export FLASK_SECRET="some_secret_value"
   ```

   **Windows PowerShell**
   ```
   $env:INSTAGRAM_USER='your_instagram_user'
   $env:INSTAGRAM_PASS='your_instagram_pass'
   $env:FLASK_SECRET='some_secret'
   ```

3. (Optional but recommended) Run `python test_login.py` to perform a login and create `session_<user>.json`. If Instagram prompts for 2FA/challenge, solve it locally — once session file is saved you can reuse it in Render.

4. Run the app:
   ```
   python app.py
   ```
   Open http://127.0.0.1:5000

## Deploy on Render (UI)
1. Push this repository to GitHub.
2. Create a new Web Service in Render and connect to the repo.
3. In Render service settings -> **Environment**, add the following Environment Variables:
   - `INSTAGRAM_USER` = gseventech
   - `INSTAGRAM_PASS` = Esbloba123@
   - `FLASK_SECRET` = Gseven
   - (Optional) `INSTAGRAM_SESSION` = the full session JSON (raw or base64). If you had to solve a challenge locally, copy the contents of `session_<user>.json` into this variable so Render can reuse the session and avoid the login challenge.
4. Build command: `pip install -r requirements.txt`
5. Start command: `python app.py`
6. Deploy and wait for the build to finish. Open the public URL and test.

## Notes / best practices
- Instagram may block logins from new IP addresses (Render's servers). If you hit a challenge, solve it locally and use the session file approach above.
- Do NOT commit credentials or session files to GitHub.
- Consider using a dedicated test account to avoid impacting your real account.
- Use small limits / delays to reduce risk of temporary blocks.
