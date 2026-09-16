# Local Migration Validation

Date: 2026-09-16 (Asia/Shanghai).

Target: `https://shapeofai.cn/`, supplied by the user. No server has been purchased or assigned an IP for this migration. No DNS changes, remote SSH/SCP, certificate issuance or purchase was performed. Publishing the separately reviewed changes to the existing GitHub Pages site does not constitute migration to this target.

Google DoH snapshot obtained during the audit on the same date: NS `house.dnspod.net` / `octagon.dnspod.net`; apex A returned NOERROR with an empty Answer; www CNAME returned NXDOMAIN. DNSPod is the currently reported authoritative DNS provider, not Cloudflare. This was recorded, not changed.

## Checks

- Read `README.md` and `.github/workflows/pages.yml`; this deployment work left both untouched. The main agent subsequently changed CI to invoke this builder with the GitHub project URL and upload only `public/`. The updated command/output contract was checked locally; the complete Actions workflow has not been run.
- `bash -n deploy/deploy.sh`: passed.
- Python standard-library unittest suite: 12 tests passed with local Caddy enabled, no skips. Without `CADDY_BIN`, the one optional HTTP integration test is explicitly skipped.
- Public source allowlist: 85 files, including `js/reading.js`, `hub.css`, `commercial.css`, `course.css`; 24 notebooks and 24 matching rendered pages.
- Generated files: `404.html`, `robots.txt`, `sitemap.xml`; 88 public files, 38 HTML files including 404, 34 sitemap URLs.
- Every notebook was compared byte-for-byte against the input. Source file hashes remain unchanged by building.
- Synthetic private files under `.git`, `docs`, `scripts`, `labs`, `assets`, `js`, notebooks and repository root were excluded even when their extension was otherwise public. Missing allowlisted files, traversal entries and symlinks were rejected.
- Metadata and URL rewriting tested with `https://shapeofai.cn/`, a target subpath and the original GitHub Pages URL. Duplicate canonical links were removed in output only. Public static HTML links resolved to existing packaged files.
- Two builds from the same source fixture produced identical gzip archive SHA-256 hashes. Archive members and payload hashes matched the external build report exactly.
- Default deploy command tested with a deliberately fake test-only host and fixture known_hosts: dry-run succeeded without invoking SSH/SCP. Root deployment rejected.
- Real remote shell payload executed against local temporary releases with mocked HTTPS and mv/flock compatibility: first activation, failed-health restoration, second activation, explicit rollback and tampered-release rejection all passed. This is not an Ubuntu or live SSH acceptance test.

## Caddy HTTP Evidence

Used the official Caddy v2.11.4 macOS arm64 release in an isolated temporary directory, not a system installation. Its archive matched the SHA-512 value in the official release checksums file:

```text
3190ae0df98b59ab4b6021556fa35adc3c526a4f3e138776b0eaec8a037cc26121cbbb1ad53453f565551b47d37d5ba4755e2c2c3652256737fe2ce9e53c8ec0
```

The production Caddyfile adapted successfully. HTTP tests changed only the test copy to an ephemeral `127.0.0.1` HTTP port, disabled admin/automatic HTTPS/persisted config and used temporary Caddy storage. The process was stopped after testing.

- All packaged HTML (except intentional 404), JS, CSS and 24 notebooks returned 200 and the expected bytes.
- Hub, directory indexes, robots and sitemap returned `no-cache, max-age=0, must-revalidate`.
- JS/CSS/notebooks returned `public, max-age=3600, must-revalidate`.
- gzip response decompressed to the exact Hub content; conditional ETag request returned 304.
- Missing extensionless/JS paths, blocked private paths, `404.html` and an unlisted directory index returned 404 with the custom body and `no-store`, not 200.
- The 404 template is Simplified Chinese, uses the existing local `hub.css`, and keeps CSS and return links root-relative so nested missing URLs work.
- Both legacy root and nested `/ai-thinking-labs/` paths returned 308 with query-preserving Location headers.

An initial integration run exposed Caddy header ordering overriding asset cache policy. The default policy was changed to a conditional `?Cache-Control` header and the full suite was rerun successfully.

## Remaining Boundaries

No live public TLS, renewal, Ubuntu systemd, Tencent firewall, external DNS, SSH host fingerprint, live release deployment, throughput or browser visual/interaction acceptance has been tested. Domain ownership/DNS readiness is not inferred from the supplied domain. Other work in the shared repository may continue changing source pages; rebuild the reviewed package after those changes settle.

## Intermediate Local Packages

Both builds below succeeded against the shared working tree. A post-build check found no differences between their recorded 85 input-file hashes and the then-current source files. These are local temporary artifacts, not remote deployments; rebuild after any further source change.

| Package | Public bytes | gzip archive bytes |
| --- | ---: | ---: |
| `/tmp/ai-thinking-migration.77eUGh/shapeofai-reviewed` | 17,553,692 | 11,577,960 |
| `/tmp/ai-thinking-migration.77eUGh/github-reviewed` | 17,559,463 | 11,578,704 |

Each package contains its `public/`, `site.tar.gz` and `build-report.json`. Only the domain-root package contains a production Caddyfile. The GitHub package preserves `/ai-thinking-labs/` and is compatible with the updated CI's `public/` artifact path.

`site.tar.gz` SHA-256:

```text
shapeofai-reviewed  336f67b9f99238197f154f4bb3cab77c9170e79b6d00e18597aa3876b72dff2f
github-reviewed     da09e15eeba997b29ab26e058a69ac055af137c35794796f9bb0980a4f20d016
```

Final test command and result:

```text
PYTHONDONTWRITEBYTECODE=1 CADDY_BIN=/tmp/ai-thinking-migration.77eUGh/caddy python3 -m unittest discover -s deploy/tests -v
Ran 12 tests in 8.574s
OK
```

The final source refresh included a concurrent `js/course-pedagogy.js` change. Source pages, scripts other than the new builder, CI and the server-options document were not edited by this deployment work.

## Final Integrated Packages

After the content, reader, UI and MCTS repairs were integrated, the main agent rebuilt both packages into durable directories outside the repository. These supersede the intermediate temporary packages above. No Tencent deployment was performed.

| Package directory | Public bytes | Archive bytes | SHA-256 of site.tar.gz |
| --- | ---: | ---: | --- |
| `/Users/zhesun/Desktop/Fudan/phd/shapeofai-release-20260916` | 17,678,043 | 11,641,338 | `8e55b0cbcece466b36fc008340bc661516c5a24d9d3632b8063ff690acc81bc0` |
| `/Users/zhesun/Desktop/Fudan/phd/shapeofai-github-release-20260916` | 17,683,814 | 11,642,142 | `b327efaea8a1162e1d01b8107c727ab6afa2cbe9be90679823dbfe50b695982c` |

Each package contains 85 allowlisted source files and 3 generated files: 88 public files, 24 downloadable notebooks, 24 rendered notebooks, 38 HTML files and 34 sitemap URLs. Only MCTS differs from the original notebook baseline. The final deployment test rerun passed all 12 tests, with Caddy enabled, in 10.321 seconds.
