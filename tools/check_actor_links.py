# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6", "requests>=2.31", "tldextract>=5"]
# ///
"""Check the links in the actorpack: logos, websites, references and domains.

For every actor it checks
- the logo (first entry of context.images): it must have an image file
  extension (the dashboard draws it with <object>, which crops images whose
  URL has none) and load as an image;
- the website (uri) and the references (context.refs): they must load;
- the website's domain, when the website does not load cleanly: it must
  still be registered (RDAP).

Each finding is one of
- broken:  certainly wrong (404/410, no DNS record, connection refused,
           domain not registered or being deleted, logo not an image or
           without file extension);
- unknown: could not tell (403/429/5xx, timeouts, TLS errors: often bot
           protection, so never reported as broken);
- moved:   the URL redirects to another domain (rebrand, sale, parking);
           worth a look, not an error.

Usage:
    uv run tools/check_actor_links.py                       # all actors
    uv run tools/check_actor_links.py --actors binance okex  # some actors
    uv run tools/check_actor_links.py --changed-from origin/master  # new or
        changed URLs only (pull requests)
    ... --report report.md --csv results.csv --fail-on-broken

The script never edits the actorpack.
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import csv
import re
import socket
import subprocess
import sys
import threading
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlsplit

import requests
import tldextract
import yaml

ACTORPACK = Path("actors/graphsense.actorpack.yaml")
IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".svg", ".webp", ".gif", ".ico", ".avif")
# Sites that block automated requests whatever the state of the page; their
# links are not checked.
SKIP_DOMAINS = {
    "twitter.com", "x.com", "linkedin.com", "facebook.com", "instagram.com",
    "t.me", "telegram.me", "reddit.com", "medium.com", "youtube.com",
    "discord.gg", "discord.com", "tiktok.com", "crunchbase.com",
}  # fmt: skip
# Data APIs listed as references: rate-limited and not a statement about the
# actor's own site.
SKIP_HOSTS = {"api.coingecko.com", "api.llama.fi", "api.cryptowisser.com"}
UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/130.0 Safari/537.36 graphsense-tagpacks-link-check"
)
TIMEOUT = 20
PER_HOST = 2  # requests in flight per host
RDAP_BOOTSTRAP = "https://data.iana.org/rdap/dns.json"
# RDAP statuses of a domain that is going away.
DYING = {"pending delete", "redemption period", "pendingdelete", "redemptionperiod"}

_extract = tldextract.TLDExtract(suffix_list_urls=())  # bundled list, no download


@dataclass
class Finding:
    actor: str
    kind: str  # logo | uri | ref | domain
    url: str
    status: str  # ok | broken | unknown | moved | skipped
    detail: str = ""


@dataclass
class Target:
    actor: str
    kind: str
    url: str


@dataclass
class Session:
    http: requests.Session = field(default_factory=requests.Session)
    host_locks: dict[str, threading.Semaphore] = field(
        default_factory=lambda: defaultdict(lambda: threading.Semaphore(PER_HOST))
    )
    rdap_servers: dict[str, str] = field(default_factory=dict)
    rdap_blocked: set[str] = field(default_factory=set)  # servers that sent 429
    lock: threading.Lock = field(default_factory=threading.Lock)


def full_url(url: str) -> str:
    """Actorpack URLs are often stored without scheme."""
    url = str(url).strip()
    # "://" may also appear later, e.g. in web.archive.org/web/<ts>/https://...
    return url if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", url) else "https://" + url


def registered_domain(url: str) -> str:
    host = urlsplit(full_url(url)).hostname or ""
    ext = _extract(host)
    return f"{ext.domain}.{ext.suffix}" if ext.domain and ext.suffix else host


def has_image_extension(url: str) -> bool:
    return urlsplit(full_url(url)).path.lower().endswith(IMAGE_EXTENSIONS)


def skipped(url: str) -> bool:
    host = (urlsplit(full_url(url)).hostname or "").lower()
    return (
        registered_domain(url) in SKIP_DOMAINS
        or host in SKIP_HOSTS
        or host.endswith(".dummy")  # placeholder for actors without a website
    )


def load_actors(text: str) -> dict[str, dict]:
    return {a["id"]: a for a in (yaml.safe_load(text) or {}).get("actors", [])}


def actor_targets(actor: dict) -> list[Target]:
    """The URLs of one actor: logo, website, references."""
    ctx = actor.get("context") or {}
    out = []
    images = ctx.get("images") or []
    if images:
        out.append(Target(actor["id"], "logo", str(images[0])))
    if actor.get("uri"):
        out.append(Target(actor["id"], "uri", str(actor["uri"])))
    for ref in ctx.get("refs") or []:
        out.append(Target(actor["id"], "ref", str(ref)))
    return out


def changed_targets(base: dict[str, dict], head: dict[str, dict]) -> list[Target]:
    """Targets of the head actorpack that the base does not have (new
    actors, new or changed logos, websites and references)."""
    out = []
    for aid, actor in head.items():
        old = {(t.kind, t.url) for t in actor_targets(base.get(aid, {"id": aid}))}
        out += [t for t in actor_targets(actor) if (t.kind, t.url) not in old]
    return out


def fetch(s: Session, url: str) -> tuple[str, str, str]:
    """(status, detail, final url) of a GET, following redirects."""
    url = full_url(url)
    host = urlsplit(url).hostname or ""
    try:
        socket.getaddrinfo(host, 443)
    except socket.gaierror:
        return "broken", "no DNS record", url
    with s.host_locks[host]:
        for attempt in range(2):
            try:
                r = s.http.get(
                    url, timeout=TIMEOUT, stream=True, allow_redirects=True,
                    headers={"User-Agent": UA, "Accept": "*/*"},
                )  # fmt: skip
                r.close()
            except requests.exceptions.SSLError:
                return "unknown", "TLS error", url
            except requests.exceptions.ConnectionError as e:
                if "refused" in str(e).lower():
                    return "broken", "connection refused", url
                if attempt == 0:
                    time.sleep(2)
                    continue
                return "unknown", "connection error", url
            except requests.exceptions.RequestException as e:
                if attempt == 0:
                    time.sleep(2)
                    continue
                return "unknown", type(e).__name__, url
            code = r.status_code
            ctype = r.headers.get("content-type", "").split(";")[0].strip()
            if code in (404, 410):
                return "broken", f"HTTP {code}", r.url
            if code >= 400:
                return "unknown", f"HTTP {code}", r.url
            return "ok", ctype, r.url
    return "unknown", "no answer", url


def check_link(s: Session, t: Target) -> Finding:
    if t.kind != "logo" and skipped(t.url):
        return Finding(t.actor, t.kind, t.url, "skipped")
    if t.kind == "logo" and not has_image_extension(t.url):
        return Finding(t.actor, t.kind, t.url, "broken", "no image file extension")
    status, detail, final = fetch(s, t.url)
    if status != "ok":
        return Finding(t.actor, t.kind, t.url, status, detail)
    if t.kind == "logo" and not detail.startswith("image/"):
        return Finding(
            t.actor, t.kind, t.url, "broken", f"not an image ({detail or '?'})"
        )
    if registered_domain(final) != registered_domain(t.url):
        return Finding(t.actor, t.kind, t.url, "moved", f"redirects to {final}")
    return Finding(t.actor, t.kind, t.url, "ok")


def rdap_server(s: Session, domain: str) -> str | None:
    with s.lock:
        if not s.rdap_servers:
            for tlds, urls in s.http.get(RDAP_BOOTSTRAP, timeout=60).json()["services"]:
                for tld in tlds:
                    s.rdap_servers[tld.lower()] = urls[0].rstrip("/")
    return s.rdap_servers.get(domain.rsplit(".", 1)[-1].lower())


def check_domain(s: Session, actor: str, domain: str) -> Finding:
    server = rdap_server(s, domain)
    if not server:
        return Finding(actor, "domain", domain, "skipped", "no RDAP server for TLD")
    host = urlsplit(server).hostname or server
    detail = "no answer"
    with s.host_locks["rdap:" + host]:
        for attempt in range(3):
            if host in s.rdap_blocked:
                return Finding(
                    actor, "domain", domain, "unknown", "RDAP server rate limit"
                )
            try:
                r = s.http.get(
                    f"{server}/domain/{domain}", timeout=TIMEOUT,
                    headers={"Accept": "application/rdap+json"},
                )  # fmt: skip
            except requests.exceptions.RequestException as e:
                detail = type(e).__name__
                time.sleep(2 * (attempt + 1))
                continue
            if r.status_code == 404:
                return Finding(actor, "domain", domain, "broken", "not registered")
            if r.status_code == 429:
                # some registries block for hours (Retry-After: 76918);
                # wait only for short limits, else skip the server
                wait = r.headers.get("retry-after", "")
                if not wait.isdigit() or int(wait) > 60:
                    s.rdap_blocked.add(host)
                    continue
                time.sleep(int(wait) + 1)
                continue
            if r.status_code != 200:
                return Finding(
                    actor, "domain", domain, "unknown", f"HTTP {r.status_code}"
                )
            data = r.json()
            statuses = {str(x).lower() for x in data.get("status") or []}
            if statuses & DYING:
                return Finding(
                    actor,
                    "domain",
                    domain,
                    "broken",
                    ", ".join(sorted(statuses & DYING)),
                )
            for event in data.get("events") or []:
                if event.get("eventAction") == "expiration" and event.get("eventDate"):
                    try:
                        when = datetime.fromisoformat(event["eventDate"])
                    except ValueError:
                        break
                    if when < datetime.now(UTC):
                        return Finding(
                            actor, "domain", domain, "broken", f"expired {when.date()}"
                        )
            return Finding(actor, "domain", domain, "ok")
    return Finding(actor, "domain", domain, "unknown", detail)


def look_up_domains(s: Session, lookups: dict[str, str]) -> list[Finding]:
    """RDAP lookups of {domain: actor}: each RDAP server gets its own
    PER_HOST threads that work through its domains one by one, so a slow
    or rate-limiting server delays only its own domains."""
    by_server: dict[str, list[str]] = defaultdict(list)
    for d in lookups:
        by_server[rdap_server(s, d) or ""].append(d)
    chunks = [ds[i::PER_HOST] for ds in by_server.values() for i in range(PER_HOST)]
    chunks = [c for c in chunks if c]
    out: list[Finding] = []
    if not chunks:
        return out
    with cf.ThreadPoolExecutor(len(chunks)) as pool:
        jobs = [
            pool.submit(lambda c: [check_domain(s, lookups[d], d) for d in c], c)
            for c in chunks
        ]
        for job in cf.as_completed(jobs):
            out += job.result()
            print(
                f"{len(out)}/{len(lookups)} domains looked up",
                file=sys.stderr,
                flush=True,
            )
    return out


def run(targets: list[Target], workers: int, domains: bool) -> list[Finding]:
    """Check the links, then look up the registration of the website domains
    that have no DNS record (a host that resolves belongs to a registered
    domain; RDAP servers are slow and rate-limited, so the others are
    skipped)."""
    s = Session()
    findings: list[Finding] = []
    with cf.ThreadPoolExecutor(workers) as pool:
        jobs = [pool.submit(check_link, s, t) for t in targets]
        for i, job in enumerate(cf.as_completed(jobs), 1):
            findings.append(job.result())
            if i % 500 == 0:
                print(f"{i}/{len(jobs)} links checked", file=sys.stderr, flush=True)
        lookups: dict[str, str] = {}
        if domains:
            for f in findings:
                if f.kind == "uri" and f.detail == "no DNS record":
                    lookups.setdefault(registered_domain(f.url), f.actor)
        print(f"{len(lookups)} domains to look up", file=sys.stderr, flush=True)
    findings += look_up_domains(s, lookups)
    return sorted(findings, key=lambda f: (f.actor, f.kind, f.url))


def report(findings: list[Finding], title: str) -> str:
    counts = Counter((f.kind, f.status) for f in findings)
    kinds = ("logo", "uri", "ref", "domain")
    lines = [f"# {title}", "", f"Checked {datetime.now(UTC):%Y-%m-%d %H:%M} UTC.", ""]
    lines += [
        "| | ok | broken | unknown | moved | skipped |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for k in kinds:
        lines.append(
            f"| {k} | " + " | ".join(str(counts[(k, st)]) for st in
                                     ("ok", "broken", "unknown", "moved", "skipped")) + " |"
        )  # fmt: skip
    sections = [
        ("Broken logos", "logo", "broken"),
        ("Domains not registered or expiring", "domain", "broken"),
        ("Broken websites", "uri", "broken"),
        ("Broken references", "ref", "broken"),
        ("Websites that moved to another domain", "uri", "moved"),
    ]
    for heading, kind, status in sections:
        rows = [f for f in findings if f.kind == kind and f.status == status]
        if not rows:
            continue
        lines += [
            "",
            f"## {heading} ({len(rows)})",
            "",
            "| actor | url | detail |",
            "|---|---|---|",
        ]
        lines += [f"| `{f.actor}` | {f.url} | {f.detail} |" for f in rows]
    unknown = [f for f in findings if f.status == "unknown"]
    if unknown:
        lines += ["", (f"<details><summary>Could not tell ({len(unknown)}): bot protection, "
                   "timeouts, rate limits</summary>"), "", "| actor | kind | url | detail |",
                  "|---|---|---|---|"]  # fmt: skip
        lines += [f"| `{f.actor}` | {f.kind} | {f.url} | {f.detail} |" for f in unknown]
        lines += ["", "</details>"]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--actorpack", type=Path, default=ACTORPACK)
    p.add_argument("--actors", nargs="*", help="only these actor ids")
    p.add_argument("--changed-from", metavar="GIT_REF",
                   help="only URLs that are new or changed since this git ref")  # fmt: skip
    p.add_argument("--no-domains", action="store_true", help="skip the RDAP lookups")
    p.add_argument("--workers", type=int, default=16)
    p.add_argument("--report", type=Path, help="write a Markdown report")
    p.add_argument("--csv", type=Path, help="write all findings as CSV")
    p.add_argument("--fail-on-broken", action="store_true",
                   help="exit 1 if anything is broken")  # fmt: skip
    args = p.parse_args(argv)

    head = load_actors(args.actorpack.read_text(encoding="utf-8"))
    if args.changed_from:
        base_text = subprocess.run(
            ["git", "show", f"{args.changed_from}:{args.actorpack.as_posix()}"],
            capture_output=True, text=True, check=True,
        ).stdout  # fmt: skip
        targets = changed_targets(load_actors(base_text), head)
        title = f"Actor link check: new or changed links since {args.changed_from}"
    else:
        if missing := [a for a in args.actors or [] if a not in head]:
            sys.exit(f"unknown actor ids: {', '.join(missing)}")
        actors = {a: head[a] for a in args.actors} if args.actors else head
        targets = [t for actor in actors.values() for t in actor_targets(actor)]
        title = "Actor link check"
    print(f"{len(targets)} links", file=sys.stderr)
    findings = run(targets, args.workers, domains=not args.no_domains)
    text = report(findings, title)
    if args.report:
        args.report.write_text(text, encoding="utf-8")
    else:
        print(text)
    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["actor", "kind", "url", "status", "detail"])
            w.writerows([f.actor, f.kind, f.url, f.status, f.detail] for f in findings)
    broken = sum(f.status == "broken" for f in findings)
    print(f"{broken} broken", file=sys.stderr)
    return 1 if args.fail_on_broken and broken else 0


if __name__ == "__main__":
    sys.exit(main())
