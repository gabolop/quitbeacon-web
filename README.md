# QuitBeacon Web

Public landing site, privacy policy, and support pages for QuitBeacon.

This is a dependency-free static site designed for Cloudflare Pages. The mobile and backend repositories remain private.

## Local preview

From this directory, run one of:

```powershell
py -m http.server 8080
# or
npx serve .
```

Then open <http://localhost:8080>.

## Cloudflare Pages

Create a Pages project connected to the public GitHub repository. Use the repository root as the build directory, leave the build command empty, and use `.` as the output directory. Configure the custom domain after DNS is ready.

Before launch, configure the support mailbox used by the site and replace `quitbeacon.app` in `robots.txt` and `sitemap.xml` if a different domain is selected.

## Content checklist before public launch

- [ ] Confirm the domain and configure HTTPS.
- [ ] Configure and test `support@quitbeacon.app`.
- [ ] If a launch list is added, use a privacy-reviewed signup provider; the current site only opens an email draft.
- [ ] Confirm the privacy policy with the final app data behavior.
- [ ] Add the Google Play listing URL after release.
- [ ] Test pages on mobile, keyboard navigation, and a screen reader.
