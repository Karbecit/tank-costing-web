# Deployment

## Current (Stage 1)

Local development only. No staging or production yet.

## Planned pipeline

```
Local dev → git push → GitHub Actions (build, test, lint)
  → auto deploy Staging
  → manual approval → Production
```

## Environment variables

See `.env.example`. Production secrets will use GitHub Secrets.

## Rollback

To be defined when staging/production hosting is chosen (Stage 4).

## Database backups

Production migrations will require backup before execution (per KarBec platform standard).
