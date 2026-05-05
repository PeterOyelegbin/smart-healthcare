# GitHub Workflows Directory
This directory contains GitHub Actions workflows that automate testing and quality checks for the Smart Healthcare project.

## 📁 Files Overview

### Workflows
| File | Purpose | Trigger | Speed |
|------|---------|---------|-------|
| `tests.yml` | Python linting, code quality & security checks, comprehensive test suite | PR to main | 3-5 min |

### Documentation
| File | Purpose |
|------|---------|
| `SETUP.md` | Quick setup guide (start here!) |
| `README.md` | This file |

---

## 🚀 Quick Start
1. **First Time?** Read [SETUP.md](SETUP.md)
2. **Need Details?** See [../CI_CD.md](../CI_CD.md)
3. **Pull request to main** and watch workflows run!

---

## 🔍 Workflow Triggers
All workflows are triggered by:
```yaml
- Push to main branch (if authentication_service/* changed)
- Pull requests to main branch (if authentication_service/* changed)
```

To skip a workflow, add to commit message:
```
git commit -m "Skip tests [skip ci]"
```

---

## 🔐 Secrets (Optional)
For advanced features, set up secrets in Repository Settings:
```
Settings → Secrets and variables → Actions
```

Common secrets:
- `CODECOV_TOKEN` - For Codecov integration
- `SLACK_WEBHOOK` - For Slack notifications
- `MAIL_TOKEN` - For email notifications

Then use in workflows:
```yaml
env:
  CODECOV_TOKEN: ${{ secrets.CODECOV_TOKEN }}
```

---

## ✨ Best Practices
✅ **Do**:
- Keep workflows simple and focused
- Use caching for speed
- Pin action versions
- Document changes
- Monitor workflows regularly
- Review logs for issues

❌ **Don't**:
- Use `latest` tag for actions
- Commit secrets to repo
- Ignore failing tests
- Skip tests to merge faster
- Run unnecessary jobs

---

## 🔄 Workflow Events
Workflows respond to:
```yaml
push:              # On code push
  branches: [main]
  
pull_request:      # On PR to main
  branches: [main]
  
schedule:          # On timer (not enabled)
  - cron: '0 2 * * *'  # Daily at 2 AM UTC
```

To add scheduled runs, uncomment `schedule` section.

---

## 📞 Support
Issues with workflows?
1. Check [SETUP.md](SETUP.md) for quick answers
2. See [../CI_CD.md](../CI_CD.md) for detailed docs
3. Review GitHub Actions documentation
4. Check workflow logs for error messages

---

## 🎉 Status
✅ Workflows configured and ready!
Your CI/CD pipeline automatically:
- Runs tests on every push to main
- Checks code quality
- Generates coverage reports
- Uploads results

Push to main and watch it go! 🚀
