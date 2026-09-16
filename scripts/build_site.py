#!/usr/bin/env python3
"""Build a reviewed, allowlisted static release using only the standard library."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import html
from html.parser import HTMLParser
import io
import ipaddress
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import tarfile
import tempfile
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OLD_ORIGIN = "https://zhesun-0209.github.io"
OLD_PATH = "/ai-thinking-labs/"
REDIRECTS = {"index.html": "hub.html", "notebooks/index.html": "hub.html"}
UTILITY_PAGES = {*REDIRECTS, "notebooks/view.html"}
URL_META = {"og:url", "twitter:url", "og:image", "og:image:url",
            "og:image:secure_url", "twitter:image", "twitter:image:src"}
EXTENSIONS = {".html", ".css", ".js", ".svg", ".ipynb", ".png", ".jpg",
              ".jpeg", ".webp", ".gif", ".ico", ".woff", ".woff2", ".ttf"}


def normalize_site_url(value):
    parts = urlsplit(value)
    if (parts.scheme != "https" or not parts.hostname or parts.username
            or parts.password or parts.port or parts.query or parts.fragment
            or not re.fullmatch(r"[A-Za-z0-9.-]+", parts.netloc)
            or any(not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?", label)
                   for label in parts.hostname.split("."))):
        raise ValueError("--site-url must be an HTTPS DNS URL without credentials, port, query or fragment")
    try:
        ipaddress.ip_address(parts.hostname)
    except ValueError:
        pass
    else:
        raise ValueError("--site-url must use a DNS name, not an IP address")
    path = parts.path.strip("/")
    if path and any(not re.fullmatch(r"[A-Za-z0-9_-]+", part) for part in path.split("/")):
        raise ValueError("unsafe site URL path")
    return f"https://{parts.hostname}/" + (path + "/" if path else "")


def validate_remote_root(value):
    if (not re.fullmatch(r"/[A-Za-z0-9_/-]+", value)
            or str(PurePosixPath(value)) != value or len(PurePosixPath(value).parts) < 3):
        raise ValueError("remote root must be a dedicated absolute directory, e.g. /srv/ai-thinking-labs")
    return value


def load_allowlist(source):
    names = json.loads((source / "deploy/public-files.json").read_text())
    if not isinstance(names, list) or not all(isinstance(name, str) for name in names):
        raise ValueError("allowlist must be an array of exact relative file paths")
    if len(names) != len(set(names)):
        raise ValueError("duplicate allowlist entry")
    for name in names:
        path = PurePosixPath(name)
        if (path.is_absolute() or str(path) != name or ".." in path.parts
                or any(part.startswith(".") for part in path.parts)
                or path.suffix not in EXTENSIONS
                or (len(path.parts) > 1 and path.parts[0] not in {"js", "notebooks", "assets"})):
            raise ValueError(f"unsafe allowlist entry: {name}")
        candidate = source
        for part in path.parts:
            candidate /= part
            if candidate.is_symlink():
                raise ValueError(f"symlinks are not publishable: {name}")
        if not candidate.is_file():
            raise ValueError(f"missing public file: {name}")
    notebooks = {name for name in names if name.endswith(".ipynb")}
    rendered = {name for name in names if name.startswith("notebooks/rendered/")}
    expected = {f"notebooks/rendered/{PurePosixPath(name).stem}.html" for name in notebooks}
    if len(notebooks) != 24 or rendered != expected:
        raise ValueError("require exactly 24 notebooks and their 24 rendered HTML counterparts")
    return sorted(names)


def rewrite_url(value, site_url):
    for prefix in (OLD_ORIGIN + OLD_PATH, "//zhesun-0209.github.io" + OLD_PATH):
        if value.startswith(prefix):
            return site_url + value[len(prefix):]
        if value == prefix.rstrip("/"):
            return site_url
    if value.startswith(OLD_PATH):
        return urlsplit(site_url).path + value[len(OLD_PATH):]
    if value == OLD_PATH.rstrip("/"):
        return urlsplit(site_url).path
    return value


def rewrite_literals(text, site_url):
    # Only rewrite complete known URL prefixes, not repository links or arbitrary paths.
    text = re.sub(r"(?<![\w:])(?:https:)?//zhesun-0209\.github\.io/ai-thinking-labs/",
                  lambda match: site_url, text)
    return re.sub(r'''(?<=["'(=\s])/ai-thinking-labs/''', urlsplit(site_url).path, text)


class PageRewriter(HTMLParser):
    def __init__(self, text, name, site_url):
        super().__init__(convert_charrefs=False)
        self.text, self.name, self.site_url = text, name, site_url
        self.offsets, offset = [], 0
        for line in text.splitlines(keepends=True):
            self.offsets.append(offset)
            offset += len(line)
        self.edits = []
        self.head = False
        self.head_count = 0

    def position(self):
        line, column = self.getpos()
        return self.offsets[line - 1] + column

    def handle_starttag(self, tag, attrs):
        if tag == "head":
            self.head = True
        values = dict(attrs)
        remove = self.head and (
            (tag == "link" and "canonical" in values.get("rel", "").lower().split())
            or (tag == "meta" and (values.get("property") or values.get("name") or "").lower() in URL_META))
        raw = self.get_starttag_text()
        if remove:
            self.edits.append((self.position(), len(raw), ""))
            return
        updated = [(key, rewrite_url(value, self.site_url) if value is not None else None)
                   for key, value in attrs]
        if updated != attrs:
            body = "".join(f' {key}="{html.escape(value, quote=True)}"' if value is not None
                           else f" {key}" for key, value in updated)
            replacement = f"<{tag}{body}" + (" />" if raw.endswith("/>") else ">")
            self.edits.append((self.position(), len(raw), replacement))

    handle_startendtag = handle_starttag

    def handle_endtag(self, tag):
        if tag != "head":
            return
        self.head = False
        self.head_count += 1
        canonical = html.escape(self.site_url + REDIRECTS.get(self.name, self.name), quote=True)
        social = html.escape(self.site_url + "og-image.svg", quote=True)
        metadata = (f'\n<link rel="canonical" href="{canonical}" />\n'
                    f'<meta property="og:url" content="{canonical}" />\n'
                    f'<meta name="twitter:url" content="{canonical}" />\n'
                    f'<meta property="og:image" content="{social}" />\n'
                    f'<meta name="twitter:image" content="{social}" />\n')
        if self.name == "notebooks/view.html":
            metadata += '<meta name="robots" content="noindex,follow" />\n'
        self.edits.append((self.position(), 0, metadata))

    def result(self):
        self.feed(self.text)
        self.close()
        if self.head_count != 1:
            raise ValueError(f"expected one HTML head: {self.name}")
        result = self.text
        for start, length, replacement in sorted(self.edits, reverse=True):
            result = result[:start] + replacement + result[start + length:]
        return rewrite_literals(result, self.site_url)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def build(source, output, site_url, remote_root="/srv/ai-thinking-labs"):
    source, output = source.resolve(), output.absolute()
    resolved = output.resolve()
    if output.exists() or output.is_symlink():
        raise ValueError("output already exists; use a new directory")
    if resolved == source or source in resolved.parents or resolved in source.parents:
        raise ValueError("output must be outside the source repository")
    site_url = normalize_site_url(site_url)
    remote_root = validate_remote_root(remote_root)
    names = load_allowlist(source)
    output.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=".site-build-", dir=output.parent))
    try:
        public = stage / "public"
        public.mkdir()
        source_hashes = {}
        for name in names:
            data = (source / name).read_bytes()
            source_hashes[name] = sha256(data)
            if name.endswith(".html"):
                data = PageRewriter(data.decode("utf-8"), name, site_url).result().encode("utf-8")
            elif name.endswith((".css", ".js")):
                data = rewrite_literals(data.decode("utf-8"), site_url).encode("utf-8")
            dest = public / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
        sitemap = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
        for name in names:
            if name.endswith(".html") and name not in UTILITY_PAGES:
                ET.SubElement(ET.SubElement(sitemap, "url"), "loc").text = site_url + name
        ET.ElementTree(sitemap).write(public / "sitemap.xml", encoding="utf-8", xml_declaration=True)
        (public / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {site_url}sitemap.xml\n")
        error_page = (source / "deploy/404.html").read_text(encoding="utf-8")
        error_page = error_page.replace("@@BASE_PATH@@", html.escape(urlsplit(site_url).path, quote=True))
        (public / "404.html").write_text(error_page, encoding="utf-8")
        files = {}
        # Build from the explicit list plus three generated files, never a repository walk.
        with (stage / "site.tar.gz").open("wb") as archive:
            with gzip.GzipFile(filename="", fileobj=archive, mode="wb", mtime=0) as compressed:
                with tarfile.open(fileobj=compressed, mode="w") as tar:
                    for name in sorted(names + ["404.html", "robots.txt", "sitemap.xml"]):
                        data = (public / name).read_bytes()
                        files[name] = {"bytes": len(data), "sha256": sha256(data)}
                        info = tarfile.TarInfo(name)
                        info.size, info.mode, info.mtime = len(data), 0o644, 0
                        tar.addfile(info, io.BytesIO(data))
        ready = urlsplit(site_url).path == "/"
        if ready:
            config = (source / "deploy/Caddyfile").read_text()
            config = config.replace("@@SITE_DOMAIN@@", urlsplit(site_url).hostname)
            config = config.replace("@@SITE_ROOT@@", remote_root + "/current")
            (stage / "Caddyfile").write_text(config)
        report = {
            "format": 1, "site_url": site_url, "remote_root": remote_root,
            "deployment_ready": ready, "source_sha256": source_hashes, "files": files,
            "counts": {"source_files": len(names), "public_files": len(files),
                       "notebooks": 24, "rendered_notebooks": 24,
                       "html": sum(name.endswith(".html") for name in files),
                       "sitemap_urls": len(sitemap)},
            "public_bytes": sum(item["bytes"] for item in files.values()),
            "archive_bytes": (stage / "site.tar.gz").stat().st_size,
            "archive_sha256": sha256((stage / "site.tar.gz").read_bytes()),
        }
        (stage / "build-report.json").write_text(json.dumps(report, indent=2) + "\n")
        stage.rename(output)
        return report
    finally:
        if stage.exists():
            shutil.rmtree(stage)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site-url", required=True, help="Actual HTTPS URL, including any base path")
    parser.add_argument("--output", required=True, type=Path, help="New release-package directory outside repo")
    parser.add_argument("--remote-root", default="/srv/ai-thinking-labs")
    args = parser.parse_args()
    try:
        report = build(ROOT, args.output, args.site_url, args.remote_root)
    except (ValueError, OSError) as exc:
        parser.exit(1, f"build failed: {exc}\n")
    print(json.dumps({key: report[key] for key in ("site_url", "counts", "public_bytes", "archive_bytes", "archive_sha256")}, indent=2))


if __name__ == "__main__":
    main()
