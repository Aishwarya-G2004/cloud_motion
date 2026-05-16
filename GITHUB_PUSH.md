# 📤 GitHub Setup & Push Guide

Step-by-step instructions for pushing your production-ready INSAT project to GitHub.

---

## 📋 Prerequisites

- GitHub account (free at https://github.com)
- Git installed on your machine
- SSH key configured (recommended) OR GitHub personal access token

---

## 🔑 Option 1: Setup SSH Key (Recommended)

### Generate SSH key (if you don't have one):

```bash
# Windows / macOS / Linux
ssh-keygen -t ed25519 -C "your.email@example.com"

# Press Enter 3 times to use default location and no passphrase
# (or add passphrase for security)
```

### Add to GitHub:

1. Copy your public key:
   ```bash
   # Windows (PowerShell)
   Get-Content $env:USERPROFILE\.ssh\id_ed25519.pub | Set-Clipboard
   
   # macOS/Linux
   cat ~/.ssh/id_ed25519.pub | pbcopy
   ```

2. Go to https://github.com/settings/keys
3. Click "New SSH key"
4. Paste the key and save

### Test connection:

```bash
ssh -T git@github.com
# Should output: Hi <username>! You've successfully authenticated...
```

---

## 🔑 Option 2: GitHub Personal Access Token

### Create token:

1. Go to https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Name: `insat-deploy-token`
4. Scopes: Select `repo` (full control of private repositories)
5. Copy the token and save securely

### Use token for cloning:

```bash
# When prompted for password, use the token instead
git clone https://github.com/your-username/insat-cloud-forecasting.git
```

---

## 📦 Step 1: Create GitHub Repository

### Option A: Via Web Interface

1. Go to https://github.com/new
2. Repository name: `insat-cloud-forecasting`
3. Description: `Cloud motion forecasting using INSAT-3DR satellite imagery and diffusion models`
4. Choose:
   - **Public** (for team collaboration)
   - **Private** (for proprietary data)
5. **Do NOT initialize with README** (we'll push existing files)
6. Click "Create repository"

### Option B: Via GitHub CLI

```bash
# Install GitHub CLI from https://cli.github.com

gh repo create insat-cloud-forecasting \
  --description "Cloud forecasting using INSAT-3DR and DDPM" \
  --public \
  --remote=origin \
  --source=. \
  --remote-name=origin \
  --push
```

---

## 📤 Step 2: Push Your Code to GitHub

### Initialize git (if not already done):

```bash
# Navigate to project root
cd insat-cloud-forecasting

# Check if git is initialized
git status

# If not, initialize
git init

# Configure git (do this once per machine)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### Add remote and push:

```bash
# Add GitHub as remote
git remote add origin https://github.com/your-username/insat-cloud-forecasting.git
# OR (if using SSH)
git remote add origin git@github.com:your-username/insat-cloud-forecasting.git

# Verify remote
git remote -v

# Create main branch and push
git branch -M main

# Stage all files (respects .gitignore)
git add .

# Verify what will be committed
git status

# IMPORTANT: Verify .env is NOT included
git check-ignore .env
# Should output: .env

# Commit
git commit -m "Initial commit: Production-ready INSAT cloud forecasting project"

# Push to GitHub
git push -u origin main

# For subsequent pushes:
git push
```

---

## ✅ Verification Checklist

### On GitHub, verify:

- ✅ Code files are present (*.py, *.md, requirements.txt, etc.)
- ✅ `.env` is NOT in the repository
- ✅ `.env.example` IS in the repository (for team reference)
- ✅ `.gitignore` is present
- ✅ Large data files (*.h5, *.npy) are NOT present
- ✅ Model checkpoint files are NOT present
- ✅ Results folder is empty or not included

### Run these checks before pushing:

```bash
# Verify nothing sensitive is staged
git status

# Check specific files won't be pushed
git ls-files | grep -E "\.env|\.h5|\.pth|\.npy"
# Should return NOTHING

# See what will be pushed
git log origin/main..HEAD

# Verify .env is ignored
git check-ignore .env
# Should output: .env
```

---

## 👥 Step 3: Add Team Members

### Option A: For public repo (anyone can clone)

No action needed! Team can clone with:
```bash
git clone https://github.com/your-username/insat-cloud-forecasting.git
```

### Option B: For private repo (add collaborators)

1. Go to your GitHub repo
2. Settings → Collaborators
3. Click "Add people"
4. Enter team member username/email
5. Choose access level:
   - **Read**: View only
   - **Triage**: Read + manage issues
   - **Write**: Read + Push code ⭐ (for active developers)
   - **Maintain**: Write + manage settings
   - **Admin**: Full control

---

## 🔄 Step 4: Team Workflow

### Each team member does:

```bash
# 1. Clone the repo
git clone https://github.com/your-username/insat-cloud-forecasting.git
cd insat-cloud-forecasting

# 2. Setup environment
python -m venv venv
venv\Scripts\activate  # or source venv/bin/activate on macOS/Linux
pip install -r requirements.txt

# 3. Create .env from template
cp .env.example .env
# Edit .env with personal credentials/paths

# 4. Work on code/features
git checkout -b feature/my-feature
# ... make changes ...
git add .
git commit -m "Feature: description"

# 5. Push feature branch
git push origin feature/my-feature

# 6. Create Pull Request on GitHub for code review
```

---

## 📝 Git Commit Best Practices

### Good commit messages:

```bash
# ✅ Clear and descriptive
git commit -m "Add data augmentation for training"
git commit -m "Fix: Correct batch size in config"
git commit -m "Refactor: Extract preprocessing to module"

# ❌ Avoid vague messages
git commit -m "Update stuff"
git commit -m "Fix"
git commit -m "WIP"
```

### Atomic commits:

```bash
# ❌ Bad: Too many changes
git add . && git commit -m "Many changes"

# ✅ Good: Focused changes
git add config.py && git commit -m "Add dynamic path configuration"
git add requirements.txt && git commit -m "Add python-dotenv dependency"
```

---

## 🚀 Continuous Integration (Optional)

### Add GitHub Actions for CI/CD:

Create `.github/workflows/tests.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.11', '3.12']
    
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Lint
      run: |
        pip install flake8
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
    
    - name: Verify config loads
      run: python config.py
```

Then push:
```bash
git add .github/workflows/tests.yml
git commit -m "CI: Add GitHub Actions workflow"
git push
```

---

## 🏷️ Create Release Tags (Optional)

After reaching milestones:

```bash
# Create a version tag
git tag -a v1.0.0 -m "Initial production release"

# Push tags to GitHub
git push origin v1.0.0

# Or push all tags
git push origin --tags
```

Then on GitHub:
1. Go to "Releases"
2. Tag appears as a release
3. Add release notes/changelog

---

## 📚 Repository README Template

Your README.md should include:

```markdown
# INSAT Cloud Forecasting

Cloud motion forecasting using INSAT-3DR satellite imagery and diffusion models (DDPM).

## Quick Start

### For Team Members:

```bash
git clone <repo-url>
cd insat-cloud-forecasting
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Configure with your credentials
python train.py
```

### For Detailed Setup:

See [DEPLOYMENT.md](DEPLOYMENT.md)

## Project Structure

- `config.py` - Dynamic configuration (environment variables)
- `train.py` - DDPM model training
- `evaluate.py` - Model evaluation
- `streamlit_app.py` - Interactive dashboard
- `preprocessor/` - Data preprocessing
- `.env.example` - Environment template (copy to .env)

## Important Security Notes

- **NEVER commit `.env`** - It contains credentials
- Keep `python-dotenv` in requirements.txt
- Share `.env` values securely (not on GitHub)
- Use GitHub Secrets for CI/CD credentials

## Team Collaboration

See [DEPLOYMENT.md](DEPLOYMENT.md) for:
- Setting up development environment
- Data management strategies
- Processing different data subsets (50 vs 163 files)
- Troubleshooting

## License

[Your License] - See LICENSE file
```

---

## 🔐 Security Checklist Before Pushing

### ✅ Before EVERY push to GitHub:

```bash
# 1. Verify .env not included
git check-ignore .env          # Should output: .env

# 2. Verify no large data files
git status | grep -i "\.h5\|\.pth\|\.npy"  # Should be empty

# 3. See what you're about to push
git log origin/main..HEAD      # Should show your commits

# 4. Final safety check
git diff --cached --name-only  # See files being committed

# 5. If everything looks good
git push
```

---

## 📞 Common Git Commands for Team

```bash
# Update local repo with latest from GitHub
git pull origin main

# See what changed
git log --oneline -10

# Create feature branch
git checkout -b feature/description

# Switch between branches
git checkout main

# Merge feature into main (after code review)
git merge feature/description

# Delete branch (after merge)
git branch -d feature/description

# Undo last commit (before push)
git reset --soft HEAD~1

# See unpushed commits
git log origin/main..HEAD
```

---

## 🐛 Oops! Accidentally Committed Secret?

### If you committed .env:

```bash
# Remove from git history (IMPORTANT!)
git rm --cached .env
git commit --amend -m "Remove .env"
git push --force-with-lease

# Then regenerate your credentials
# (since they were exposed in git history)
```

---

## 📊 Monitor Repository

### After pushing, you can:

1. **View GitHub Page**: https://github.com/your-username/insat-cloud-forecasting
2. **Check Collaborators**: Settings → Collaborators
3. **View Commits**: Insights → Network
4. **Track Issues**: Issues tab
5. **Manage Releases**: Releases tab

---

## 🎯 Final Checklist

Before considering your repo production-ready:

- [ ] All code pushed to main branch
- [ ] `.env` is NOT in repository
- [ ] `.env.example` IS in repository with comments
- [ ] requirements.txt includes all dependencies (including python-dotenv)
- [ ] `.gitignore` correctly excludes large files
- [ ] README.md updated with quick start instructions
- [ ] DEPLOYMENT.md provides team setup guidance
- [ ] All team members can clone and run code
- [ ] Tested on Windows, macOS, and/or Linux
- [ ] No hardcoded paths remaining (all use config.py)

---

**You're ready to collaborate!** 🎉

Push your code and share with your team.
