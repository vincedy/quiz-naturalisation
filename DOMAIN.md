# Custom domain — swissnaturalizationtest.ch

Operational record for the domain this site is served from. Everything here is public
information (DNS is public by design). No account numbers, invoices or payment details.

## Domains

| Domain | Role |
|---|---|
| `swissnaturalizationtest.ch` | **Main.** GitHub Pages serves the site here. |
| `swissnaturalizationtest.com` | Defensive. Redirects to the main domain. |
| `swissnaturalisationtest.ch` | Defensive (British spelling). Redirects to the main domain. |

Registrar: Infomaniak, name servers `ns11/ns12.infomaniak.ch`, DNSSEC on. All three first
registered 16.09.2026 for one year, with auto-renewal. Expiry dates live in the Infomaniak
Manager (the `.ch` registry does not publish them; the `.com` registry says 16.09.2027).

The `.ch` registry publishes no holder data in public WHOIS (`whois -h whois.nic.ch`).

DNS records can be managed through the Infomaniak API
(`https://api.infomaniak.com/2/zones/<domain>/records`, token scopes `domain:read`,
`dns:read`, `dns:write`). The token is never stored in this repository.

## DNS records for the main domain

Values from GitHub's documentation, *Managing a custom domain for your GitHub Pages site*.

| Type | Name | Value |
|---|---|---|
| TXT | `_github-pages-challenge-vincedy` | `15124318e4eda7232cf63fb6e3ee31` |
| A | `@` | `185.199.108.153` |
| A | `@` | `185.199.109.153` |
| A | `@` | `185.199.110.153` |
| A | `@` | `185.199.111.153` |
| AAAA | `@` | `2606:50c0:8000::153` |
| AAAA | `@` | `2606:50c0:8001::153` |
| AAAA | `@` | `2606:50c0:8002::153` |
| AAAA | `@` | `2606:50c0:8003::153` |
| CNAME | `www` | `vincedy.github.io` |

**The TXT record stays forever.** It proves to GitHub that the account owns the domain;
removing it lets the domain be claimed by another GitHub Pages site.

## Order of operations — zero downtime

GitHub's docs say "add the domain to the repo, then DNS". On a site that is already live
that order breaks it: the moment the repo declares the domain, `github.io` starts
redirecting to an address that does not resolve yet. Verifying the domain first removes the
takeover risk that order protects against, so the safe sequence is:

1. Verify the domain on the GitHub **account** (`github.com/settings/pages`) with the TXT record.
2. Add the A, AAAA and CNAME records.
3. Wait until the domain resolves to GitHub (checks below).
4. Only then set the custom domain on the repo:
   `gh api -X PUT repos/vincedy/quiz-naturalisation/pages -f cname=swissnaturalizationtest.ch`
5. When the certificate is issued, enforce HTTPS:
   `gh api -X PUT repos/vincedy/quiz-naturalisation/pages -F https_enforced=true`

## What depends on this domain

- **Printed QR codes** in `print/` point to `vincedy.github.io/quiz-naturalisation/landing.html`.
  They keep working only through GitHub's redirect to the custom domain.
- **App binary**: `storeLinks.ts` (`go.html`) and `legalLinks.ts` (terms, privacy) in the app repo.
- **Store listings**: website, privacy policy and account-deletion URLs (Play Console);
  support, marketing and privacy URLs (App Store Connect, changeable only with a new version).
- **Open Graph** `og:image` URLs and cross-page links on this site.

**Never remove the custom domain from this repo, and never let the main domain expire.**
Paper cannot be updated.

## Checks

```bash
dig +short NS    swissnaturalizationtest.ch
dig +short A     swissnaturalizationtest.ch
dig +short AAAA  swissnaturalizationtest.ch
dig +short       www.swissnaturalizationtest.ch
dig +short TXT   _github-pages-challenge-vincedy.swissnaturalizationtest.ch
# delegation straight from the .ch registry (NXDOMAIN = not yet published)
dig +norecurse NS swissnaturalizationtest.ch @a.nic.ch
curl -sI https://swissnaturalizationtest.ch/ | head -3
curl -sI https://vincedy.github.io/quiz-naturalisation/landing.html | head -3
```
