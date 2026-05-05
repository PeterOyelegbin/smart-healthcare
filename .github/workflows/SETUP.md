# GitHub Actions Quick Setup Guide

## 🚀 What's Installed
Your GitHub Actions CI/CD pipelines are configured and ready to run tests automatically.


## 📋 Workflows Created
1. Main Test Pipeline
- **File**: `.github/workflows/auth-service-tests.yml`
- **Trigger**: Pull requests to main or push to dev
- **Tests on**: Python 3.9, 3.10, 3.11
- **Includes**: Linting, formatting checks, security scanning, coverage reports, artifacts, Codecov integration

2. Main Deploy Pipeline
- **File**: `.github/workflows/deploy.yml`
- **Trigger**: Push to main

## ⚙️ How Workflows Work
### tests.yml - Main Testing
```
Push to main/PR created
         ↓
Trigger: tests.yml
         ↓
Setup: Python 3.9, 3.10, 3.11
         ↓
Install: dependencies from requirements.txt
         ↓
Run: pylint analysis
Run: flake8 linting
Run: black formatting check
Run: bandit security scan
         ↓
Run: 38 pytest tests
         ↓
Generate: coverage report (3.9 only)
         ↓
Upload: artifacts (coverage, results)
         ↓
Results: Available in logs
         ↓
Done! ✅
```

---

## ✅ First Steps
1. Push to GitHub
```bash
git add .github/
git commit -m "Add CI/CD workflows"
git push origin main
```

2. Check Status
- Go to your GitHub repository
- Click **Actions** tab
- Watch your first workflow run!

3. View Results
After workflow completes:
- Click the workflow run
- View test output and logs
- Download coverage report artifact


## 📊 Status Badges
Add to your `README.md`:
```markdown
![Tests](https://github.com/YOUR_ORG/smart-healthcare/workflows/Authentication%20Service%20Tests/badge.svg?branch=main)
![Quality](https://github.com/YOUR_ORG/smart-healthcare/workflows/Code%20Quality%20Checks/badge.svg?branch=main)
```
Replace `YOUR_ORG` with your GitHub username/organization.


## 🔒 Require Checks Before Merge
Protect your main branch:
- **Settings** → **Branches** → **main**
- Enable "Require status checks to pass before merging"
- Select "Authentication Service Tests"
- Save

Now PRs cannot be merged if tests fail! ✅


## 📝 Commands Reference
1. Force Re-run Workflow
```bash
# In GitHub Actions, click "Re-run jobs"
# Or use GitHub CLI:
gh run rerun <run-id>
```

2. Skip Workflow on Specific Commit
```bash
git commit -m "Update docs [skip ci]"
```

3. View Workflow Status Locally
```bash
# Using GitHub CLI
gh run list

# View specific run
gh run view <run-id>
```


## 📈 What Gets Tested
Each workflow run:
- ✅ Installs all dependencies
- ✅ Runs 38 unit tests
- ✅ Generates coverage reports
- ✅ Checks code quality
- ✅ Uploads results as artifacts


## 🎯 Expected Results
After first push:
```
✅ All tests passing
✅ 38/38 tests succeeded
✅ ~75% coverage
✅ ~5 seconds per run (cached)
✅ Coverage report uploaded
✅ HTML report available for download
```


## 🆘 Troubleshooting
1. Workflow Not Running
- [ ] Did you make PR to `main` branch?
- [ ] Did you modify files in `authentication_service/`?
- [ ] Is the YAML syntax valid?

2. Tests Failing in CI
```bash
# Run same test locally:
cd authentication_service
./.venv/bin/python -m pytest tests/test_auth.py -v

# Compare with CI Python version
python3.9 -m pytest tests/test_auth.py -v
```

3. Slow Workflow
- Clear cache and re-run
- Check GitHub Actions status page
- Reduce number of Python versions tested


## 📚 Useful Links
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Codecov Integration](https://codecov.io/github)
- [Workflow Syntax Reference](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [Python Setup Action](https://github.com/actions/setup-python)


## 🎉 You're All Set!
Your CI/CD pipeline is ready:
- Tests run automatically on push
- Coverage reports generated
- Quality checks performed
- Results available for review

Make pull request to main and watch your workflow run in the **Actions** tab! 🚀

---

For more details, see [CI_CD.md](../CI_CD.md)
