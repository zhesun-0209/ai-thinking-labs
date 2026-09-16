"""Offline deployment tests; optional CADDY_BIN enables loopback HTTP checks."""

import gzip
import hashlib
from html.parser import HTMLParser
import http.client
import json
import os
from pathlib import Path
import runpy
import shutil
import socket
import subprocess
import sys
import tarfile
import tempfile
import time
import unittest
from urllib.parse import urljoin, urlsplit, unquote
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
BUILDER = runpy.run_path(str(ROOT / "scripts/build_site.py"))
URL = "https://shapeofai.cn/"


class Tags(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.tags = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


class BuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="deployment-tests-")
        cls.work = Path(cls.temp.name)
        cls.source = cls.work / "source"
        cls.source.mkdir()
        names = json.loads((ROOT / "deploy/public-files.json").read_text())
        for name in names + ["deploy/public-files.json", "deploy/Caddyfile", "deploy/404.html"]:
            dest = cls.source / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, dest)
        for name in [".git/config", ".env", "docs/private.html", "scripts/private.js",
                     "private.html", "js/private.js", "assets/private.png", "labs/secret.json",
                     "notebooks/private.ipynb", "notebooks/rendered/private.html", "id_ed25519"]:
            dest = cls.source / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text("PRIVATE_SENTINEL_NOT_FOR_PUBLICATION")
        cls.output = cls.work / "root-package"
        cls.report = BUILDER["build"](cls.source, cls.output, URL)
        cls.public = cls.output / "public"

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_exact_allowlist_and_notebook_bytes(self):
        names = json.loads((self.source / "deploy/public-files.json").read_text())
        actual = {p.relative_to(self.public).as_posix() for p in self.public.rglob("*") if p.is_file()}
        self.assertEqual(actual, set(names) | {"robots.txt", "sitemap.xml", "404.html"})
        self.assertEqual(len(list(self.public.rglob("*.ipynb"))), 24)
        self.assertEqual(len(list((self.public / "notebooks/rendered").glob("*.html"))), 24)
        for name in names:
            data = (self.public / name).read_bytes()
            self.assertNotIn(b"PRIVATE_SENTINEL", data)
            if name.endswith(".ipynb"):
                self.assertEqual(data, (self.source / name).read_bytes())
        for name in ["js/reading.js", "hub.css", "commercial.css", "course.css"]:
            self.assertIn(name, actual)

    def test_archive_manifest_and_reproducibility(self):
        with tarfile.open(self.output / "site.tar.gz") as archive:
            self.assertEqual(set(archive.getnames()), set(self.report["files"]))
            for item in archive.getmembers():
                self.assertTrue(item.isfile())
                self.assertEqual(item.mode, 0o644)
                self.assertEqual(hashlib.sha256(archive.extractfile(item).read()).hexdigest(),
                                 self.report["files"][item.name]["sha256"])
        second = BUILDER["build"](self.source, self.work / "reproducible", URL)
        self.assertEqual(second["archive_sha256"], self.report["archive_sha256"])

    def test_all_metadata_and_source_untouched(self):
        for name, digest in self.report["source_sha256"].items():
            self.assertEqual(hashlib.sha256((self.source / name).read_bytes()).hexdigest(), digest)
            if not name.endswith(".html"):
                continue
            text = (self.public / name).read_text()
            self.assertNotIn(BUILDER["OLD_ORIGIN"] + BUILDER["OLD_PATH"], text)
            tags = Tags(text).tags
            canonical = [attrs["href"] for tag, attrs in tags
                         if tag == "link" and attrs.get("rel") == "canonical"]
            expected = URL + BUILDER["REDIRECTS"].get(name, name)
            self.assertEqual(canonical, [expected], name)
            for key in ["og:url", "twitter:url", "og:image", "twitter:image"]:
                values = [attrs["content"] for tag, attrs in tags
                          if tag == "meta" and (attrs.get("property") or attrs.get("name")) == key]
                self.assertEqual(values, [URL + "og-image.svg" if "image" in key else expected])

    def test_local_links_exist(self):
        for page in self.public.rglob("*.html"):
            name = page.relative_to(self.public).as_posix()
            for tag, attrs in Tags(page.read_text()).tags:
                for key in ("href", "src"):
                    value = attrs.get(key)
                    if not value or "${" in value or value.startswith(("#", "data:", "javascript:", "mailto:")):
                        continue
                    target = urlsplit(urljoin(URL + name, value))
                    if target.netloc != "shapeofai.cn":
                        continue
                    path = self.public / unquote(target.path.lstrip("/"))
                    self.assertTrue(path.exists(), f"{name}: missing {value}")

    def test_subpath_and_original_pages_base(self):
        for base, directory in [(URL + "ai-thinking-labs/", "prefix-package"),
                                (BUILDER["OLD_ORIGIN"] + BUILDER["OLD_PATH"], "github-package")]:
            output = self.work / directory
            report = BUILDER["build"](self.source, output, base)
            self.assertFalse(report["deployment_ready"])
            self.assertFalse((output / "Caddyfile").exists())
            self.assertIn(base + "hub.html", (output / "public/hub.html").read_text())
            self.assertNotIn("https:https:", (output / "public/hub.html").read_text())
            self.assertIn(base + "sitemap.xml", (output / "public/robots.txt").read_text())
            error = (output / "public/404.html").read_text()
            self.assertIn('href="/ai-thinking-labs/hub.css"', error)
            self.assertIn('href="/ai-thinking-labs/hub.html"', error)
            self.assertNotIn('@@BASE_PATH@@', error)
            for page in (output / "public").rglob("*.html"):
                for tag, attrs in Tags(page.read_text()).tags:
                    if tag == "link" and attrs.get("rel") == "canonical":
                        self.assertTrue(attrs["href"].startswith(base), str(page))
                    if tag == "meta" and (attrs.get("property") or attrs.get("name")) in BUILDER["URL_META"]:
                        self.assertTrue(attrs["content"].startswith(base), str(page))

    def test_rewrite_url_attributes_and_literals(self):
        old = BUILDER["OLD_ORIGIN"] + BUILDER["OLD_PATH"]
        content = ('<html><head><link rel="canonical" href="hub.html">'
                   f'<link rel="canonical" href="{old}index.html"></head><body>'
                   '<a href="/ai-thinking-labs/ch5.html?q=1&amp;x=2#part">A</a>'
                   f'<img src="{old}favicon.svg"><a href="https://other.example/ai-thinking-labs/">B</a>'
                   '<script>const p="/ai-thinking-labs/js/reading.js";</script></body></html>')
        text = BUILDER["PageRewriter"](content, "index.html", URL).result()
        self.assertIn('href="/ch5.html?q=1&amp;x=2#part"', text)
        self.assertIn(f'src="{URL}favicon.svg"', text)
        self.assertIn('"/js/reading.js"', text)
        self.assertIn('https://other.example/ai-thinking-labs/', text)
        self.assertEqual(text.count('rel="canonical"'), 1)
        css = 'body{background:url(/ai-thinking-labs/assets/a.png)}'
        self.assertEqual(BUILDER["rewrite_literals"](css, URL), 'body{background:url(/assets/a.png)}')

    def test_sitemap_robots_404(self):
        urls = [element.text for element in ET.parse(self.public / "sitemap.xml").iter()
                if element.tag.endswith("}loc")]
        self.assertEqual(len(urls), 34)
        self.assertTrue(all(url.startswith(URL) for url in urls))
        self.assertNotIn(URL + "404.html", urls)
        self.assertNotIn(URL + "index.html", urls)
        self.assertIn("Sitemap: " + URL + "sitemap.xml", (self.public / "robots.txt").read_text())
        error = (self.public / "404.html").read_text()
        self.assertIn('content="noindex,follow"', error)
        self.assertIn('lang="zh-CN"', error)
        self.assertIn('\u9875\u9762\u672a\u627e\u5230', error)
        self.assertIn('href="/hub.css"', error)
        self.assertIn('href="/hub.html"', error)
        self.assertNotIn('Page not found', error)

    def test_reject_unsafe_urls_and_output(self):
        for url in ["http://shapeofai.cn", "https://u:p@shapeofai.cn", "https://shapeofai.cn?x=1",
                    "https://shapeofai.cn/#fragment", "https://shapeofai.cn/../private",
                    "https://shapeofai.cn/{bad}", "https://127.0.0.1", "https://shapeofai.cn:443"]:
            with self.subTest(url=url), self.assertRaises(ValueError):
                BUILDER["normalize_site_url"](url)
        for output in [self.output, self.source / "out", self.source]:
            with self.subTest(output=output), self.assertRaises(ValueError):
                BUILDER["build"](self.source, output, URL)

    def test_reject_missing_symlinks_and_allowlist_traversal(self):
        name = self.source / "js/reading.js"
        backup = name.read_bytes()
        try:
            name.unlink()
            with self.assertRaisesRegex(ValueError, "missing public file"):
                BUILDER["load_allowlist"](self.source)
            name.symlink_to(self.source / "js/private.js")
            with self.assertRaisesRegex(ValueError, "symlinks"):
                BUILDER["load_allowlist"](self.source)
        finally:
            if name.is_symlink():
                name.unlink()
            name.write_bytes(backup)
        manifest = self.source / "deploy/public-files.json"
        saved = manifest.read_text()
        try:
            for entry in ["../private.html", "docs/private.html", ".git/config", "scripts/private.js"]:
                manifest.write_text(json.dumps(json.loads(saved) + [entry]))
                with self.subTest(entry=entry), self.assertRaises(ValueError):
                    BUILDER["load_allowlist"](self.source)
        finally:
            manifest.write_text(saved)

    def test_deploy_dry_run_and_ssh_guards(self):
        known = self.work / "known_hosts"
        known.write_text("TEST_FIXTURE_ONLY_NOT_A_REAL_HOST_KEY\n")
        command = ["bash", str(ROOT / "deploy/deploy.sh"), "deploy", "--package", str(self.output),
                   "--host", "server.example.invalid", "--user", "site-deploy", "--known-hosts", str(known)]
        result = subprocess.run(command, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("no SSH/SCP was run", result.stdout)
        self.assertIn(URL, result.stdout)
        command[command.index("site-deploy")] = "root"
        self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)
        script = (ROOT / "deploy/deploy.sh").read_text()
        self.assertIn("StrictHostKeyChecking=yes", script)
        self.assertNotIn("StrictHostKeyChecking=no", script)
        self.assertIn("ForwardAgent=no", script)

    def test_release_activation_rollback_and_failed_health_locally(self):
        # Execute the real remote payload in a temp directory. Only OS command
        # compatibility and HTTPS transport are simulated; no SSH is invoked.
        remote = (ROOT / "deploy/deploy.sh").read_text().split("<<'REMOTE'\n", 1)[1].rsplit("\nREMOTE", 1)[0]
        root = self.work / "remote-simulation"
        (root / "releases").mkdir(parents=True)
        (root / "incoming").mkdir()
        mocks = self.work / "mock-bin"
        mocks.mkdir()
        commands = {
            "mv": "import os,sys\na=[x for x in sys.argv[1:] if x not in ('-Tf','--')]\nos.replace(*a)\n",
            "flock": "import fcntl,sys\nfcntl.flock(int(sys.argv[-1]), fcntl.LOCK_EX | fcntl.LOCK_NB)\n",
            "curl": ("import os,pathlib,shutil,sys,urllib.parse\n"
                     "if os.environ.get('MOCK_HEALTH_FAIL'): sys.exit(22)\n"
                     "args=sys.argv[1:]; url=next(x for x in args if x.startswith('https://'))\n"
                     "src=pathlib.Path(os.environ['MOCK_ROOT'])/'current'/urllib.parse.urlsplit(url).path.lstrip('/')\n"
                     "shutil.copyfile(src, args[args.index('-o')+1])\n"),
        }
        for name, body in commands.items():
            path = mocks / name
            path.write_text(f"#!{sys.executable}\n" + body)
            path.chmod(0o755)
        environment = dict(os.environ, PATH=str(mocks) + os.pathsep + os.environ["PATH"], MOCK_ROOT=str(root),
                           PYTHONOPTIMIZE="1")
        def activate(action, release, fail=False):
            if action == "deploy":
                incoming = root / "incoming" / release
                incoming.mkdir()
                for name in ["site.tar.gz", "build-report.json"]:
                    shutil.copyfile(self.output / name, incoming / name)
            env = dict(environment)
            if fail:
                env["MOCK_HEALTH_FAIL"] = "1"
            return subprocess.run(["bash", "-c", remote, "--", action, str(root), release, URL,
                                   self.report["archive_sha256"]], env=env, text=True, capture_output=True)
        first, failed, second = [f"20260916T000000Z-{number:08x}" for number in [1, 2, 3]]
        result = activate("deploy", first)
        self.assertEqual(result.returncode, 0, result.stderr)
        first_target = f"releases/{first}/public"
        self.assertEqual(os.readlink(root / "current"), first_target)
        result = activate("deploy", failed, fail=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(os.readlink(root / "current"), first_target)
        self.assertFalse((root / "previous").exists())
        result = activate("deploy", second)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(os.readlink(root / "previous"), first_target)
        result = activate("rollback", first)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(os.readlink(root / "current"), first_target)
        self.assertEqual(os.readlink(root / "previous"), f"releases/{second}/public")
        (root / "releases" / second / "public/hub.html").write_text("tampered")
        result = activate("rollback", second)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(os.readlink(root / "current"), first_target)

    @unittest.skipUnless(os.environ.get("CADDY_BIN"), "set CADDY_BIN for local Caddy HTTP integration")
    def test_caddy_loopback_http(self):
        binary = os.environ["CADDY_BIN"]
        config = (self.output / "Caddyfile").read_text()
        adapted = subprocess.run([binary, "adapt", "--config", str(self.output / "Caddyfile"),
                                  "--adapter", "caddyfile"], capture_output=True, text=True)
        self.assertEqual(adapted.returncode, 0, adapted.stderr)
        self.assertIn("shapeofai.cn", adapted.stdout)
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        config = config.replace("shapeofai.cn {", f"http://127.0.0.1:{port} {{", 1)
        config = config.replace("/srv/ai-thinking-labs/current", str(self.public))
        config = "{\n admin off\n auto_https off\n persist_config off\n}\n" + config
        local = self.work / "Caddyfile.local"
        local.write_text(config)
        environment = dict(os.environ, XDG_DATA_HOME=str(self.work / "caddy-data"),
                           XDG_CONFIG_HOME=str(self.work / "caddy-config"))
        with (self.work / "caddy.log").open("w+") as log:
            process = subprocess.Popen([binary, "run", "--config", str(local), "--adapter", "caddyfile"],
                                       stdout=log, stderr=log, env=environment)
            try:
                for attempt in range(100):
                    try:
                        with socket.create_connection(("127.0.0.1", port), timeout=0.1):
                            break
                    except OSError:
                        if process.poll() is not None:
                            log.seek(0)
                            self.fail(log.read())
                        time.sleep(0.05)
                def request(path, headers=None):
                    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
                    try:
                        connection.request("GET", path, headers=headers or {})
                        response = connection.getresponse()
                        return response.status, dict(response.getheaders()), response.read()
                    finally:
                        connection.close()
                for path in ["/", "/hub.html", "/notebooks/", "/sitemap.xml", "/robots.txt"]:
                    status, headers, body = request(path)
                    self.assertEqual(status, 200, path)
                    self.assertEqual(headers["Cache-Control"], "no-cache, max-age=0, must-revalidate")
                status, headers, body = request("/hub.html", {"Accept-Encoding": "gzip"})
                self.assertEqual(headers["Content-Encoding"], "gzip")
                self.assertEqual(gzip.decompress(body), (self.public / "hub.html").read_bytes())
                status, headers, body = request("/hub.html")
                self.assertEqual(request("/hub.html", {"If-None-Match": headers["Etag"]})[0], 304)
                for name in self.report["files"]:
                    if name.endswith((".ipynb", ".html", ".css", ".js")) and name != "404.html":
                        status, headers, body = request("/" + name)
                        self.assertEqual(status, 200, name)
                        self.assertEqual(body, (self.public / name).read_bytes())
                        if not name.endswith(".html"):
                            self.assertEqual(headers["Cache-Control"], "public, max-age=3600, must-revalidate")
                for path in ["/missing", "/missing.js", "/404.html", "/docs/private.html", "/.git/config", "/notebooks/rendered/", "/nested/missing/page.html"]:
                    status, headers, body = request(path)
                    self.assertEqual(status, 404, path)
                    self.assertEqual(headers["Cache-Control"], "no-store", path)
                    self.assertEqual(body, (self.public / "404.html").read_bytes(), path)
                    self.assertIn(b'href="/hub.css"', body)
                for path, expected in [("/ai-thinking-labs/?ch=5", "/?ch=5"),
                                       ("/ai-thinking-labs/ch5.html?x=1", "/ch5.html?x=1")]:
                    status, headers, body = request(path)
                    self.assertEqual(status, 308)
                    self.assertEqual(headers["Location"], expected)
            finally:
                process.terminate()
                process.wait(timeout=10)


if __name__ == "__main__":
    unittest.main(verbosity=2)
