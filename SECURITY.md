# Security policy

## Never commit

- Google Ads developer tokens, OAuth client secrets, refresh tokens, access tokens, API keys, or service-account keys.
- Google Ads customer IDs, conversion IDs/labels, GTM/GA4 IDs, phone numbers, CRM exports, client names, addresses, or private screenshots.
- Search-term reports, lead records, budgets tied to an identifiable location, or any data that identifies a customer or franchisee.

## Deployment boundary

The repository supports planning and validation. It is not a credential store. A deployment agent must receive credentials through the host platform's secret manager, use least-privilege access, run a read-only preflight, show a proposed diff, and wait for explicit human approval before writes.

## If a secret is exposed

1. Stop the deployment.
2. Revoke/rotate the exposed credential in the owning platform.
3. Remove it from the working tree and Git history using the platform's approved procedure.
4. Review audit logs for unauthorized access.
5. Notify the repository owner.

Report suspected vulnerabilities privately to the repository owner; do not open a public issue with secrets or personal data.
