# 🚀 Deployment Guide

## Deploying to Streamlit Cloud

### Prerequisites
- GitHub account
- Streamlit Cloud account (free at [share.streamlit.io](https://share.streamlit.io))
- Project pushed to GitHub repository

---

### Step 1: Prepare Your Repository
Ensure all files are committed:

```bash
git add .
git commit -m "Prepare for deployment"
git push origin main
```

**Verify these files exist:**
- `app.py`
- `requirements.txt`
- `data/` folder with `.gitkeep`

**Create `.gitignore` if not exists:**
```text
.streamlit/secrets.toml
__pycache__/
*.pyc
.env
data/*.csv
```

---

### Step 2: Deploy to Streamlit Cloud
1. Go to [https://share.streamlit.io](https://share.streamlit.io)
2. Click **"New app"**
3. Select your repository: `<username>/expense_tracker`
4. Set:
   - **Branch:** `main`
   - **Main file path:** `app.py`
5. Click **"Deploy"**

---

### Step 3: Configure Secrets (For AI Features)
In the Streamlit Cloud dashboard, go to the app settings:
1. Click **"Secrets"**
2. Add:
```toml
GOOGLE_API_KEY = "your-actual-api-key-here"
```
3. Save and restart app.

---

### Step 4: Custom Domain (Optional)
Streamlit provides a free subdomain: `<app-name>.streamlit.app`
For custom domain, upgrade to Teams plan.

---

## 🛠️ Troubleshooting

- **Import errors**: Check `requirements.txt` has all dependencies.
- **File not found**: Ensure `data/` folder exists with `.gitkeep`.
- **Secrets not working**: Verify TOML syntax in secrets.

---

## 🧪 Local Testing Before Deployment

```bash
# Test with production-like settings
streamlit run app.py --server.port 8501
```
