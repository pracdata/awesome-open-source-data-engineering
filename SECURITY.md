# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.2.x   | Yes       |
| < 0.2   | No        |

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it
responsibly:

1. **Do not** open a public GitHub issue
2. Email security concerns to the repository owner via GitHub's private
   vulnerability reporting at:
   **Settings > Security > Advisories > Report a vulnerability**
3. Include steps to reproduce, affected versions, and potential impact

You can expect an initial response within 72 hours. We will work with you to
understand the issue and coordinate a fix before any public disclosure.

## Scope

This project is a documentation crawler. Security-relevant areas include:

- **robots.txt compliance** — the crawler must always obey `ROBOTSTXT_OBEY = True`
- **URL handling** — spider must not follow arbitrary redirects to untrusted domains
- **Output sanitization** — crawled content written to `docs.jsonl` must not be
  treated as trusted input by downstream consumers
- **Dependency supply chain** — pinned dependencies are monitored by Dependabot
