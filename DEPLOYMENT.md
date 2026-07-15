# Deployment



## Target environment (accepted)



| Item | Decision |

|------|----------|

| Host | JMA shared web server (wholesaler), **cPanel** |

| URL | `https://tankcalc.jmagroup.com.au` (subdomain **TBC**) |

| TLS | cPanel AutoSSL / Let's Encrypt |

| Secrets | cPanel env vars or `.env` outside web root — never Git |



## Pre-deploy checklist (when ready)



1. Confirm subdomain DNS → server IP.

2. Create subdomain in cPanel; enable SSL.

3. Confirm **Python / ASGI** support on plan (FastAPI + uvicorn) or upgrade plan if needed.

4. Build frontend (`npm run build`); deploy `dist/` to document root.

5. Deploy backend; configure reverse proxy so `/api` reaches FastAPI.

6. Set environment variables (DB path, secret key, SMTP — later).

7. Run database migrations / initial admin user creation (secure channel).

8. Smoke test: login, MFA, calculate, save costing.



## Current (development)



Local only: `.\scripts\start.ps1` — API `:8080`, UI `:5173`.



## CI (GitHub Actions)



On push to `main`: lint, pytest, frontend build. **Does not auto-deploy to cPanel yet.**



## Planned pipeline



```

Local dev → git push → GitHub Actions (build, test, lint)

  → manual or cPanel Git deploy → Production (tankcalc.jmagroup.com.au)

```



Staging subdomain optional (e.g. `tankcalc-staging.jmagroup.com.au`) if needed before go-live.



## Environment variables



See `.env.example`. Production adds (minimum):



- `SECRET_KEY` — session/JWT signing

- `DATABASE_URL` or `DB_PATH`

- `SMTP_*` — configured via admin UI once built; fallback env for bootstrap



## Rollback



- Keep previous release folder or git tag on server.

- Database backup before schema changes (KarBec standard).



## Database backups



- Schedule cPanel backup or cron dump of SQLite/PostgreSQL.

- Backup before every migration in production.



## Shared hosting notes



- **Python on server:** up to **3.13.13** in Setup Python App; **use 3.12.13** (host recommended) for production.
- **Setup Python App** confirmed — persistent app via Passenger is expected.
- Prefer **single subdomain** serving static UI + proxied API.

- If Python app cannot run persistently on plan, options: upgrade hosting, use passenger, or host API on a small VPS and UI only on shared server (split — last resort).



## MFA (production policy)



- **Admin:** MFA every login.

- **Other users:** MFA first login per browser/device; optional **Trust this device**.

- Requires working SMTP before auth go-live.

