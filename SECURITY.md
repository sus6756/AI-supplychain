# Security Policy

## Supported versions

Traqify is a single-branch project. Only the latest `main` is supported.

| Version | Supported |
| ------- | --------- |
| `main` (v3.1.x) | ✅ |
| Older commits   | ❌ |

## Reporting a vulnerability

**Please do not open a public issue for security problems.**

Report privately through GitHub's
[Report a vulnerability](https://github.com/sus6756/AI-supplychain/security/advisories/new)
form, or email **sashankmidhun@gmail.com** with the subject line
`[SECURITY] AI-supplychain`.

Please include:

- A description of the issue and its impact.
- Steps to reproduce, or a proof-of-concept.
- Any suggested remediation.

You can expect an acknowledgement within a few days. This is a student project
maintained in spare time, so please be patient — but security reports are taken
seriously and prioritised above feature work.

## Scope

In scope:

- Authentication and session handling in `project.py`
- SQL handling in the MySQL console and all `mysql.connector` call sites
- Credential, secret and PII exposure
- Email / SMTP abuse (e.g. OTP or report endpoints usable as an open relay)

Out of scope:

- The public demo deployment being in "sleep mode"
- Missing hardening on a self-hosted MySQL instance you control
- Denial of service through deliberately absurd file uploads
- Reports that require the attacker to already hold valid credentials

## Hardening checklist for self-hosters

Traqify is a teaching project, not a hardened multi-tenant product. Before
exposing it publicly, consider:

1. **Hash passwords** — the current schema stores them as plain text. Swap in
   `bcrypt`/`argon2` before any real use.
2. **Use least-privilege DB credentials** — the app only needs DML on its own
   schema, not `GRANT` or `FILE`.
3. **Keep secrets out of git** — `.streamlit/secrets.toml` is git-ignored; keep it
   that way, and load real deployments from the platform's secret store.
4. **Restrict the SQL Console** — it currently accepts arbitrary SQL from the admin
   account. Disable it, or gate it behind a read-only DB user.
5. **Serve over HTTPS only** and set a strong admin password.
