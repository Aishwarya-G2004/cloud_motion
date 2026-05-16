# 📋 QUICK START: Push to GitHub

Fast reference for pushing your production-ready project to GitHub.

---

## 5-Minute Setup

### 1️⃣ Create GitHub Repository

Go to https://github.com/new
- Name: `insat-cloud-forecasting`
- Description: Cloud forecasting using INSAT-3DR and DDPM
- Public or Private (your choice)
- **Don't** initialize with README
- Click "Create repository"

### 2️⃣ Configure Git (First Time Only)

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 3️⃣ Initialize & Push

```bash
cd d:\Insat_data

# Add GitHub as remote
git remote add origin https://github.com/YOUR_USERNAME/insat-cloud-forecasting.git

# Verify
git remote -v

# Stage files (respects .gitignore)
git add .

# Verify .env is NOT included
git check-ignore .env

# Commit
git commit -m "Initial commit: Production-ready INSAT cloud forecasting project

- Dynamic configuration via config.py
- Environment variables support
- Credentials removed from code
- Flexible data processing (50-163 files)
- .gitignore excludes large files and sensitive data
- Team deployment documentation
- GitHub integration guide"

# Create main branch
git branch -M main

# Push
git push -u origin main
```

---

## ✅ Verify on GitHub

After pushing, check your repository:
- [ ] Code files present (*.py, *.md)
- [ ] `.env` NOT in repository
- [ ] `.env.example` IS in repository
- [ ] `config.py` present
- [ ] No `.h5` or `.pth` files
- [ ] No large data directories

---

## 👥 Share with Team

Send team members the GitHub link and have them:

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/insat-cloud-forecasting.git

# 2. Follow DEPLOYMENT.md
# (in the cloned repository)
```

---

## 📚 Documentation for Your Team

When team members clone, they'll find:
- **DEPLOYMENT.md** - Complete setup guide
- **GITHUB_PUSH.md** - Git workflow guide
- **PRODUCTION_CHECKLIST.md** - What changed and why
- **.env.example** - Configuration template
- **config.py** - Dynamic configuration system

---

## 🔒 Security Check

Before pushing, verify:

```bash
# These should ALL fail (good!)
git ls-files | grep "\.env$"           # Should be empty
git ls-files | grep "\.h5$"            # Should be empty
git ls-files | grep "\.pth$"           # Should be empty
git ls-files | grep "auto_download"    # Should show only without hardcoded creds

# This should succeed (good!)
git check-ignore .env                  # Should output: .env
```

---

## 🚀 After Push

### For you (maintainer):
```bash
# Future commits
git add .
git commit -m "Feature: description"
git push
```

### For team members:
```bash
# Setup (one time)
git clone <your-repo-url>
cd insat-cloud-forecasting
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with their values

# Then use normally
python train.py
```

---

## 📞 If Something Goes Wrong

### Oops, I committed .env!

```bash
git rm --cached .env
git commit --amend -m "Remove .env (not meant to be committed)"
git push --force-with-lease
# Regenerate MOSDAC credentials (they were exposed)
```

### Oops, I pushed large files!

```bash
# See what got pushed
git ls-files | grep "\.h5\|\.pth"

# Remove them (advanced)
# Consider using BFG Repo Cleaner or git-filter-branch
# OR start fresh with new repo
```

---

## ✨ That's It!

Your project is now:
- ✅ Production-ready
- ✅ On GitHub
- ✅ Shareable with your team
- ✅ Secure (credentials not exposed)
- ✅ Flexible (supports different setups)

**Congratulations!** 🎉
