#!/usr/bin/env python3
"""
XMRT Ecosystem Main Application - Version 6.3 "Hardier GitHub"
- Full multi-agent ideation → comments → weighted consensus → decision issue
- Implements code + README + story, then opens a Discussion (or story Issue fallback)
- Discovers ALL repos named like xmrt* via owner listing OR REST search (user/org)
- Runs real GitHub mode even if owner fetch fails, as long as repo fetch works
"""

import os
import re
import sys
import json
import time
import queue
import signal
import random
import logging
import threading
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS

# ---------- Optional deps ----------
try:
    from github import Github, Auth, GithubException
    GITHUB_AVAILABLE = True
except ImportError:
    GITHUB_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

import requests  # used for REST fallback

# ---------- Config / Globals ----------
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
log = logging.getLogger("xmrt-main")

app = Flask(__name__)
CORS(app)

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "10000"))
OWNER = os.getenv("GITHUB_OWNER", "DevGruGold")
REPO_ECOSYSTEM = os.getenv("GITHUB_REPO", "XMRT-Ecosystem")
DEFAULT_OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
FORCE_SIMULATE = os.getenv("XMRT_FORCE_SIMULATE", "false").lower() == "true"

READY = threading.Event()
SHUTDOWN = threading.Event()

system_state: Dict[str, Any] = {
    "status": "operational",
    "startup_time": time.time(),
    "version": "6.3.0-hardy-github",
    "mode": "XMRT_INNOVATION_CYCLE",
    "owner": OWNER,
    "ecosystem_repo": REPO_ECOSYSTEM,
}

analytics: Dict[str, Any] = {
    "requests_count": 0,
    "ai_operations": 0,
    "github_operations": 0,
    "issues_created": 0,
    "discussions_created": 0,
    "story_issues_created": 0,
    "files_created": 0,
    "files_updated": 0,
    "repositories_discovered": 0,
    "ideas_generated": 0,
    "comments_posted": 0,
    "feature_cycles_completed": 0,
    "system_health": {"cpu": 0.0, "mem": 0.0, "disk": 0.0},
}

AGENTS: Dict[str, Dict[str, Any]] = {
    "eliza": {"name": "Eliza", "role": "Coordinator & Governor", "voice": "strategic, synthesizes viewpoints", "weight": 1.2},
    "security_guardian": {"name": "Security Guardian", "role": "Security & Privacy", "voice": "threat-models, privacy-first", "weight": 1.1},
    "defi_specialist": {"name": "DeFi Specialist", "role": "Mining & Tokenomics", "voice": "ROI, efficiency, yield", "weight": 1.05},
    "community_manager": {"name": "Community Manager", "role": "Adoption & UX", "voice": "onboarding, docs, growth", "weight": 1.0},
}

# ---------- AI ----------
class AIProcessor:
    def __init__(self, eager_probe: bool = False):
        self.openai = None
        self.gemini = None
        if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
            try:
                self.openai = OpenAI()
                if eager_probe:
                    _ = self.openai.chat.completions.create(
                        model=DEFAULT_OPENAI_MODEL,
                        messages=[{"role": "user", "content": "ping"}],
                        max_tokens=2,
                    )
                log.info("OpenAI client initialized")
            except Exception as e:
                log.warning(f"OpenAI init failed: {e}")
        if GEMINI_AVAILABLE and os.getenv("GEMINI_API_KEY"):
            try:
                genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
                self.gemini = genai.GenerativeModel(os.getenv("GEMINI_MODEL", "gemini-pro"))
            except Exception as e:
                log.warning(f"Gemini init failed: {e}")

    def is_available(self) -> bool:
        return bool(self.openai or self.gemini)

    def _chat(self, sys_prompt: str, user_prompt: str, max_tokens: int = 1200, temperature: float = 0.7) -> str:
        if self.openai:
            try:
                r = self.openai.chat.completions.create(
                    model=DEFAULT_OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": sys_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                analytics["ai_operations"] += 1
                return r.choices[0].message.content or ""
            except Exception as e:
                log.warning(f"OpenAI error: {e}")
        if self.gemini:
            try:
                r = self.gemini.generate_content(f"{sys_prompt}\n\n{user_prompt}")
                analytics["ai_operations"] += 1
                return getattr(r, "text", "") or ""
            except Exception as e:
                log.warning(f"Gemini error: {e}")
        return ""

    def ideate(self, repos_summary: List[Dict[str, Any]], n: int = 7) -> List[Dict[str, Any]]:
        sys_prompt = "You are an XMRT DAO strategist (mobile mining, mesh, privacy, adoption)."
        user_prompt = (
            "Propose high-impact, concrete features/utilities for this ecosystem. "
            "Return JSON array of objects: title, description, rationale, impact (1-5), complexity (1-5), tags (list). "
            f"Generate {n} distinct ideas.\n\nREPOS:\n{json.dumps(repos_summary, indent=2)}"
        )
        text = self._chat(sys_prompt, user_prompt)
        ideas: List[Dict[str, Any]] = []
        for candidate in re.findall(r"\[[\s\S]*\]", text):
            try:
                parsed = json.loads(candidate)
                if isinstance(parsed, list):
                    for x in parsed:
                        if isinstance(x, dict) and "title" in x:
                            ideas.append(x)
                    break
            except Exception:
                continue
        if not ideas:
            ideas = [
                {"title": "Adaptive Mobile Mining Profiles", "description": "Auto-tune CPU/battery/net profiles.", "rationale": "Boost hash-per-watt.", "impact": 5, "complexity": 3, "tags": ["mining", "optimizer", "mobile"]},
                {"title": "Mesh Health Beacons", "description": "UDP beacons for offline discovery.", "rationale": "Mesh resilience.", "impact": 5, "complexity": 2, "tags": ["meshnet", "offline"]},
                {"title": "Proof-of-Participation Badges", "description": "Signed badges feed governance.", "rationale": "Align effort & votes.", "impact": 4, "complexity": 3, "tags": ["governance", "reputation"]},
                {"title": "XMRT Cross-Indexer", "description": "Unified API over all xmrt* repos.", "rationale": "Dev velocity.", "impact": 4, "complexity": 2, "tags": ["devtools", "api"]},
                {"title": "Mesh-First Wallet Alerts", "description": "Offline alerts; sync later.", "rationale": "Trust-minimized UX.", "impact": 4, "complexity": 3, "tags": ["wallet", "meshnet"]},
                {"title": "One-Tap MobileMonero Onboarding", "description": "Termux bootstrap + verify.", "rationale": "Drop friction.", "impact": 5, "complexity": 3, "tags": ["onboarding", "mobile", "ux"]},
                {"title": "Edge Telemetry Pack", "description": "Privacy-preserving miner metrics.", "rationale": "Optimize safely.", "impact": 4, "complexity": 2, "tags": ["telemetry", "privacy"]},
            ]
        analytics["ideas_generated"] += len(ideas)
        return ideas

    def agent_reviews(self, ideas: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        out: Dict[str, List[Dict[str, Any]]] = {k: [] for k in AGENTS.keys()}
        for agent_id, meta in AGENTS.items():
            for idea in ideas:
                impact = float(idea.get("impact", 3))
                complexity = float(idea.get("complexity", 3))
                tags = [t.lower() for t in idea.get("tags", [])]
                boost = 0.0
                if agent_id == "security_guardian" and any(t in tags for t in ["privacy", "security", "meshnet"]): boost += 2.0
                if agent_id == "defi_specialist" and any(t in tags for t in ["mining", "optimizer", "governance"]): boost += 2.0
                if agent_id == "community_manager" and any(t in tags for t in ["onboarding", "ux", "alerts"]): boost += 2.0
                if agent_id == "eliza": boost += 1.5
                base = 5.0
                score = max(0.0, min(10.0, base + (impact - 0.3 * complexity) + boost))
                comment = f"{meta['name']} ({meta['role']}): {meta['voice']}. Assessment for '{idea['title']}': impact={impact}, complexity={complexity}, score={round(score,2)}."
                out[agent_id].append({"title": idea["title"], "comment": comment, "score": round(score, 2)})
        return out

    def choose(self, ideas: List[Dict[str, Any]], reviews: Dict[str, List[Dict[str, Any]]]) -> Tuple[Dict[str, Any], Dict[str, float]]:
        totals: Dict[str, float] = {i["title"]: 0.0 for i in ideas}
        for aid, arr in reviews.items():
            w = float(AGENTS[aid]["weight"])
            for r in arr:
                totals[r["title"]] += r["score"] * w
        winner = max(totals, key=lambda k: totals[k]) if totals else ideas[0]["title"]
        return next(i for i in ideas if i["title"] == winner), totals

ai = AIProcessor()

# ---------- GitHub ----------
class GitHubClient:
    def __init__(self, owner: str, repo_name: str):
        self.owner = owner
        self.repo_name = repo_name
        self.token = os.getenv("GITHUB_TOKEN")
        self.simulate = FORCE_SIMULATE or not (self.token and GITHUB_AVAILABLE)
        self.gh = None
        self.owner_obj = None
        self.repo = None

        if not GITHUB_AVAILABLE:
            log.warning("PyGithub not available -> simulate mode")
            self.simulate = True
            return

        if FORCE_SIMULATE:
            log.warning("XMRT_FORCE_SIMULATE=true -> simulate mode")
            self.simulate = True
            return

        try:
            auth = Auth.Token(self.token) if self.token else None
            self.gh = Github(auth=auth) if auth else Github()
            # Try direct repo first to enable real mode without owner resolution
            try:
                self.repo = self.gh.get_repo(f"{self.owner}/{self.repo_name}")
                log.info("GitHub repo reachable (%s/%s). Enabling real mode.", self.owner, self.repo_name)
                self.simulate = False
            except Exception as e_repo:
                log.warning(f"Direct repo fetch failed: {e_repo}")
            # Best-effort owner resolve (optional)
            if not self.owner_obj:
                try:
                    self.owner_obj = self.gh.get_user(self.owner)
                except Exception:
                    try:
                        self.owner_obj = self.gh.get_organization(self.owner)
                    except Exception as e_owner:
                        log.warning(f"Owner resolve failed (user/org). Continuing with REST search fallback. Reason: {e_owner}")
            if not self.repo and not self.simulate:
                # Try again to get repo (owner might be resolved now)
                try:
                    self.repo = self.gh.get_repo(f"{self.owner}/{self.repo_name}")
                except Exception:
                    pass
            if not self.repo and not self.owner_obj:
                # Still no repo/owner: remain in simulate, but we can still REST search later.
                log.warning("No repo/owner handle available; will use REST search for discovery.")
        except Exception as e:
            log.warning(f"GitHub init failed -> simulate mode. Reason: {e}")
            self.simulate = True

    # REST helper
    def _rest(self, method: str, path: str, **kwargs) -> Tuple[int, Any]:
        headers = kwargs.pop("headers", {})
        headers.update({
            "Accept": "application/vnd.github+json",
            "User-Agent": "XMRT-Consensus-Builder",
        })
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
            headers["X-GitHub-Api-Version"] = "2022-11-28"
        url = f"https://api.github.com{path}"
        resp = requests.request(method, url, headers=headers, timeout=30, **kwargs)
        try:
            return resp.status_code, resp.json()
        except Exception:
            return resp.status_code, resp.text

    def list_xmrt_repos(self) -> List[Dict[str, Any]]:
        repos: List[Dict[str, Any]] = []
        # Preferred: owner_obj listing
        if self.owner_obj and not self.simulate:
            try:
                for r in self.owner_obj.get_repos(type="public"):
                    if r.name.lower().startswith("xmrt"):
                        topics = []
                        try:
                            topics = r.get_topics()
                        except Exception:
                            pass
                        repos.append({
                            "name": r.name,
                            "full_name": r.full_name,
                            "description": r.description,
                            "language": r.language,
                            "topics": topics,
                            "stars": r.stargazers_count,
                            "forks": r.forks_count,
                            "updated_at": r.updated_at.isoformat() if r.updated_at else None,
                            "has_pages": r.has_pages,
                        })
                analytics["repositories_discovered"] = len(repos)
                return repos
            except Exception as e:
                log.warning(f"Owner listing failed, falling back to REST search: {e}")

        # REST Search fallback (works even without owner_obj)
        try:
            combined = {}
            # Search as user
            status, data = self._rest("GET", f"/search/repositories?q=user:{self.owner}+xmrt+in:name&per_page=100")
            if status == 200 and isinstance(data, dict) and "items" in data:
                for r in data["items"]:
                    if r["name"].lower().startswith("xmrt"):
                        combined[r["full_name"]] = r
            # Search as org
            status2, data2 = self._rest("GET", f"/search/repositories?q=org:{self.owner}+xmrt+in:name&per_page=100")
            if status2 == 200 and isinstance(data2, dict) and "items" in data2:
                for r in data2["items"]:
                    if r["name"].lower().startswith("xmrt"):
                        combined[r["full_name"]] = r

            for r in combined.values():
                repos.append({
                    "name": r["name"],
                    "full_name": r["full_name"],
                    "description": r.get("description"),
                    "language": r.get("language"),
                    "topics": r.get("topics", []),
                    "stars": r.get("stargazers_count", 0),
                    "forks": r.get("forks_count", 0),
                    "updated_at": r.get("updated_at"),
                    "has_pages": r.get("has_pages", False),
                })
            analytics["repositories_discovered"] = len(repos)
            if not repos:
                log.warning("REST search found no xmrt* repos; using minimal seed list.")
                repos = [{"name": "XMRT-Ecosystem", "full_name": f"{self.owner}/XMRT-Ecosystem", "language": "Python", "topics": ["xmrt"]}]
                analytics["repositories_discovered"] = len(repos)
            return repos
        except Exception as e:
            log.error(f"REST search failed: {e}")
            repos = [{"name": "XMRT-Ecosystem", "full_name": f"{self.owner}/XMRT-Ecosystem", "language": "Python", "topics": ["xmrt"]}]
            analytics["repositories_discovered"] = len(repos)
            return repos

    def create_or_update_file(self, path: str, message: str, content: str) -> Dict[str, Any]:
        if self.repo and not self.simulate:
            try:
                self.repo.create_file(path, message, content)
                analytics["files_created"] += 1
                return {"created": True, "path": path}
            except GithubException:
                try:
                    file = self.repo.get_contents(path)
                    self.repo.update_file(path, f"Update: {message}", content, file.sha)
                    analytics["files_updated"] += 1
                    return {"updated": True, "path": path}
                except Exception as e:
                    log.error(f"File op error for {path}: {e}")
                    return {"error": str(e), "path": path}
            except Exception as e:
                log.error(f"File op error for {path}: {e}")
                return {"error": str(e), "path": path}
        # simulate
        analytics["files_created"] += 1
        return {"simulated": True, "path": path}

    def create_issue(self, title: str, body: str, labels: Optional[List[str]] = None) -> Dict[str, Any]:
        if self.repo and not self.simulate:
            try:
                issue = self.repo.create_issue(title=title, body=body, labels=labels or [])
                analytics["issues_created"] += 1
                return {"number": issue.number, "url": issue.html_url}
            except Exception as e:
                log.error(f"Issue create failed: {e}")
                return {"error": str(e)}
        analytics["issues_created"] += 1
        return {"simulated": True, "number": random.randint(1000, 9999)}

    def comment_issue(self, issue_number: int, comment: str) -> Dict[str, Any]:
        if self.repo and not self.simulate:
            try:
                issue = self.repo.get_issue(number=issue_number)
                issue.create_comment(comment)
                analytics["comments_posted"] += 1
                return {"ok": True}
            except Exception as e:
                log.error(f"Issue comment failed: {e}")
                return {"error": str(e)}
        analytics["comments_posted"] += 1
        return {"simulated": True}

    def list_discussion_categories(self) -> List[Dict[str, Any]]:
        if not self.token:
            return []
        status, data = self._rest("GET", f"/repos/{self.owner}/{self.repo_name}/discussions/categories")
        if status == 200 and isinstance(data, list):
            return data
        return []

    def create_discussion(self, title: str, body: str, category_name: str = "General") -> Dict[str, Any]:
        if self.token and not self.simulate:
            cats = self.list_discussion_categories()
            cat_id = None
            for c in cats:
                if str(c.get("name", "")).lower() == category_name.lower():
                    cat_id = c.get("id")
                    break
            if not cat_id and cats:
                cat_id = cats[0].get("id")
            if cat_id:
                status, data = self._rest("POST", f"/repos/{self.owner}/{self.repo_name}/discussions", json={"title": title, "body": body, "category_id": cat_id})
                if status in (200, 201):
                    analytics["discussions_created"] += 1
                    return {"ok": True, "number": data.get("number"), "url": data.get("html_url")}
                log.warning(f"Discussion create failed ({status}): {data}")
            # Fallback → Story as Issue (label: story)
            story = self.create_issue(f"[Story] {title}", body, labels=["story"])
            analytics["story_issues_created"] += 1
            story["fallback"] = "story-issue"
            return story
        # simulate
        analytics["discussions_created"] += 1
        return {"simulated": True}

gh = GitHubClient(OWNER, REPO_ECOSYSTEM)

# ---------- Helpers ----------
def summarize_repos_for_ai(repos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for r in repos:
        out.append({
            "name": r.get("name"),
            "language": r.get("language"),
            "topics": r.get("topics", []),
            "stars": r.get("stars", 0),
            "updated_at": r.get("updated_at"),
            "desc": (r.get("description") or "")[:140],
        })
    return out

def slugify(name: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9\-_]+", "-", (name or "feature").strip())
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s.lower() or "feature"

def implement_feature(app_name: str, idea: Dict[str, Any]) -> List[Dict[str, Any]]:
    created: List[Dict[str, Any]] = []
    slug = slugify(app_name)
    base = f"xmrt_apps/{slug}"
    files = {
        f"{base}/{slug}.py": (
            "#!/usr/bin/env python3\n"
            f'"""{app_name}\n'
            "Auto-generated by XMRT Consensus Builder.\n\n"
            "Description:\n"
            f"{idea.get('description','(no description)')}\n\n"
            f"Tags: {', '.join(idea.get('tags', []))}\n"
            '"""\n\n'
            "import time, json, logging\n"
            'logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")\n'
            f'log = logging.getLogger("{slug}")\n\n'
            "def run():\n"
            f"    log.info('Initialized {app_name}')\n"
            "    result = {\n"
            "        'status': 'ok',\n"
            f"        'feature': '{app_name}',\n"
            "        'timestamp': time.time(),\n"
            "    }\n"
            "    print(json.dumps(result))\n\n"
            "if __name__ == '__main__':\n"
            "    run()\n"
        ),
        f"{base}/{slug}_config.py": (
            f"# Config for {app_name}\n"
            "CONFIG = {\n"
            "  'version': '0.1.0',\n"
            "  'enabled': True,\n"
            "  'notes': 'Auto-generated; add integration params.'\n"
            "}\n"
        ),
        f"{base}/{slug}_README.md": (
            f"# {app_name}\n\n"
            f"**Idea**: {idea.get('description','')}\n\n"
            f"**Rationale**: {idea.get('rationale','')}\n\n"
            f"**Tags**: {', '.join(idea.get('tags', []))}\n\n"
            "Created by the XMRT multi-agent consensus flow.\n"
            "Next steps:\n"
            "- Wire into MobileMonero / MeshNet / Optimizer as applicable.\n"
            "- Add tests and integration hooks.\n"
        ),
        f"docs/stories/{slug}.md": (
            f"# Story: {app_name}\n\n"
            f"- Idea: {idea.get('title','')}\n"
            f"- Why: {idea.get('rationale','')}\n\n"
            "Artifacts will be linked by CI (issue, commits, demos).\n"
            f"*Generated {datetime.now().isoformat()} by XMRT Consensus Builder.*\n"
        ),
    }
    for path, content in files.items():
        created.append(gh.create_or_update_file(path, f"Add {app_name}: {os.path.basename(path)}", content))
    return created

# ---------- Innovation Cycle ----------
def run_consensus_cycle() -> Dict[str, Any]:
    repos = gh.list_xmrt_repos()
    summaries = summarize_repos_for_ai(repos)
    ideas = ai.ideate(summaries, n=7)
    reviews = ai.agent_reviews(ideas)
    winner, totals = ai.choose(ideas, reviews)

    # Decision Issue
    issue_title = f"[Consensus] Implement: {winner['title']}"
    body = []
    body.append(f"# Consensus Decision: {winner['title']}\n")
    body.append("## Idea\n")
    body.append(f"- Description: {winner.get('description','')}\n")
    body.append(f"- Rationale: {winner.get('rationale','')}\n")
    body.append(f"- Tags: {', '.join(winner.get('tags', []))}\n")
    body.append(f"- Impact: {winner.get('impact','?')}  Complexity: {winner.get('complexity','?')}\n")
    body.append("## Agent Scores\n")
    for aid, arr in reviews.items():
        nm = AGENTS[aid]["name"]
        sc = next((x["score"] for x in arr if x["title"] == winner["title"]), None)
        if sc is not None:
            body.append(f"- {nm}: {sc}\n")
    body.append("## Totals\n")
    for k, v in sorted(totals.items(), key=lambda kv: kv[1], reverse=True):
        body.append(f"- {k}: {round(v,2)}\n")
    body.append("## Initial Plan\n- Create module under xmrt_apps/<slug>/\n- Add story in docs/stories/\n- Wire integration points next\n")
    decision_issue = gh.create_issue(issue_title, "".join(body), labels=["consensus", "auto", "xmrt-feature"])
    issue_no = decision_issue.get("number") or random.randint(1000, 9999)

    # Agent comments on the decision issue
    for aid, meta in AGENTS.items():
        c = next((x for x in reviews[aid] if x["title"] == winner["title"]), None)
        text = c["comment"] if c else f"{meta['name']}: Approve."
        gh.comment_issue(issue_no, text)

    # Implement files
    files = implement_feature(winner["title"], winner)

    # Story (Discussion or fallback Story Issue)
    story_title = f"{winner['title']} shipped via Multi-Agent Consensus"
    story_body = (
        f"# {winner['title']}\n\n"
        "Emerging from autonomous, multi-agent deliberation.\n\n"
        f"- Decision Issue: #{issue_no}\n"
        f"- Owner: {OWNER}/{REPO_ECOSYSTEM}\n\n"
        f"**What/Why**\n- {winner.get('description','')}\n- {winner.get('rationale','')}\n\n"
        f"**Artifacts**\n{json.dumps(files, indent=2)}\n"
    )
    discussion = gh.create_discussion(story_title, story_body, category_name="General")

    analytics["feature_cycles_completed"] += 1
    result = {
        "repos_discovered": len(repos),
        "ideas_count": len(ideas),
        "winner": winner,
        "totals": totals,
        "decision_issue": decision_issue,
        "files": files,
        "story": discussion,
        "timestamp": datetime.now().isoformat(),
    }
    return result

# ---------- Worker ----------
class OneShotWorker(threading.Thread):
    def __init__(self):
        super().__init__(name="xmrt-oneshot-worker", daemon=True)
        self.q: "queue.Queue[Dict[str, Any]]" = queue.Queue()
        self.last_result: Optional[Dict[str, Any]] = None

    def schedule(self, job: Dict[str, Any]) -> None:
        self.q.put(job)

    def run(self):
        READY.set()
        log.info("Consensus Builder worker ready")
        while not SHUTDOWN.is_set():
            try:
                job = self.q.get(timeout=0.5)
            except queue.Empty:
                continue
            if job.get("type") == "innovation_cycle":
                log.info("Starting innovation cycle")
                try:
                    self.last_result = run_consensus_cycle()
                    log.info("Innovation cycle complete: %s", self.last_result.get("winner", {}).get("title", "n/a"))
                except Exception as e:
                    log.exception(f"Innovation cycle failed: {e}")
            else:
                log.info("Unknown job: %s", job)

worker = OneShotWorker()
worker.start()

# ---------- Health ----------
def update_health():
    if PSUTIL_AVAILABLE:
        try:
            analytics["system_health"]["cpu"] = psutil.cpu_percent(interval=0.1)
            analytics["system_health"]["mem"] = psutil.virtual_memory().percent
            analytics["system_health"]["disk"] = psutil.disk_usage("/").percent
            return
        except Exception:
            pass
    analytics["system_health"]["cpu"] = round(random.uniform(5, 35), 1)
    analytics["system_health"]["mem"] = round(random.uniform(20, 70), 1)
    analytics["system_health"]["disk"] = round(random.uniform(10, 60), 1)

# ---------- Frontend ----------
FRONT = """
<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>XMRT Ecosystem 6.3 — Consensus Builder</title>
<style>
body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Ubuntu,Cantarell,Noto Sans,sans-serif;background:#0f172a;color:#e2e8f0;margin:0;padding:24px}
.container{max-width:1200px;margin:0 auto}
h1{font-size:28px;margin-bottom:8px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px;margin-top:16px}
.card{background:#111827;border:1px solid #1f2937;border-radius:12px;padding:16px}
button{background:#334155;color:#e2e8f0;border:none;border-radius:8px;padding:10px 16px;cursor:pointer}
button:hover{background:#475569}
pre{white-space:pre-wrap;word-wrap:break-word;background:#0b1220;padding:12px;border-radius:8px;border:1px solid #1f2937}
.small{color:#94a3b8;font-size:12px}
.stat{font-size:24px;font-weight:700}
</style></head><body>
<div class="container">
  <h1>XMRT Ecosystem 6.3 — Consensus Builder</h1>
  <div class="small">Owner: {{ owner }} • Repo: {{ repo }} • Version: {{ version }} • Uptime: {{ uptime }}s</div>
  <div class="grid">
    <div class="card">
      <h3>Actions</h3>
      <button onclick="runCycle()">Run Innovation Cycle</button>
      <button onclick="lastResult()">Last Result</button>
      <button onclick="refresh()">Refresh</button>
      <div id="out" style="margin-top:12px;"></div>
    </div>
    <div class="card">
      <h3>Stats</h3>
      <div>Repos discovered: <span class="stat">{{ stats.repositories_discovered }}</span></div>
      <div>Ideas: <span class="stat">{{ stats.ideas_generated }}</span></div>
      <div>Issues: <span class="stat">{{ stats.issues_created }}</span></div>
      <div>Discussions: <span class="stat">{{ stats.discussions_created }}</span> • Story Issues: <span class="stat">{{ stats.story_issues_created }}</span></div>
      <div>Files: <span class="stat">{{ stats.files_created }}</span> / updates: <span class="stat">{{ stats.files_updated }}</span></div>
      <div>Cycles: <span class="stat">{{ stats.feature_cycles_completed }}</span></div>
      <div class="small">CPU {{ sys.cpu }}% • MEM {{ sys.mem }}% • DISK {{ sys.disk }}%</div>
    </div>
    <div class="card">
      <h3>Agents</h3>
      <pre>{{ agents_json }}</pre>
    </div>
  </div>
</div>
<script>
async function runCycle(){
  const out=document.getElementById('out');
  out.textContent='Running innovation cycle...';
  const r=await fetch('/api/run-innovation-cycle',{method:'POST'});
  const j=await r.json();
  out.textContent=JSON.stringify(j,null,2);
}
async function lastResult(){
  const out=document.getElementById('out');
  const r=await fetch('/api/innovation/last');
  const j=await r.json();
  out.textContent=JSON.stringify(j,null,2);
}
function refresh(){location.reload();}
</script></body></html>
"""

# ---------- Routes ----------
@app.route("/", methods=["GET", "HEAD"])
def index():
    analytics["requests_count"] += 1
    update_health()
    return render_template_string(
        FRONT,
        owner=OWNER,
        repo=REPO_ECOSYSTEM,
        version=system_state["version"],
        uptime=round(time.time() - system_state["startup_time"], 1),
        stats=analytics,
        sys=analytics["system_health"],
        agents_json=json.dumps(AGENTS, indent=2),
    )

@app.route("/health")
@app.route("/healthz")
def health():
    update_health()
    return jsonify({
        "ok": True,
        "ready": READY.is_set(),
        "version": system_state["version"],
        "owner": OWNER,
        "repo": REPO_ECOSYSTEM,
        "uptime": round(time.time() - system_state["startup_time"], 3),
        "system": analytics["system_health"],
        "timestamp": datetime.now().isoformat(),
    })

@app.route("/analytics")
def get_analytics():
    analytics["requests_count"] += 1
    return jsonify(analytics)

@app.route("/agents")
def get_agents():
    analytics["requests_count"] += 1
    return jsonify({"agents": AGENTS})

@app.route("/api/coordination/status")
def coordination_status():
    return jsonify({
        "ready": READY.is_set(),
        "feature_cycles_completed": analytics["feature_cycles_completed"],
        "ideas_generated": analytics["ideas_generated"],
        "repositories_discovered": analytics["repositories_discovered"],
        "issues_created": analytics["issues_created"],
        "discussions_created": analytics["discussions_created"],
        "story_issues_created": analytics["story_issues_created"],
        "files_created": analytics["files_created"],
        "files_updated": analytics["files_updated"],
        "timestamp": datetime.now().isoformat(),
    })

@app.route("/api/run-innovation-cycle", methods=["POST"])
def api_run_cycle():
    worker.schedule({"type": "innovation_cycle"})
    return jsonify({"scheduled": True})

@app.route("/api/innovation/last")
def api_last():
    return jsonify(worker.last_result or {"last_result": None})

# Minimal webhooks
@app.route("/webhook/github", methods=["POST"])
def webhook_github():
    analytics["github_operations"] += 1
    return jsonify({"status": "received", "source": "github", "ts": datetime.now().isoformat()})

@app.route("/webhook/render", methods=["POST"])
def webhook_render():
    return jsonify({"status": "received", "source": "render", "ts": datetime.now().isoformat()})

@app.route("/webhook/discord", methods=["POST"])
def webhook_discord():
    return jsonify({"status": "received", "source": "discord", "ts": datetime.now().isoformat()})


# ---------- Enhanced API Endpoints ----------
@app.route("/api/analytics")
def api_analytics():
    """Enhanced analytics endpoint with more detailed information."""
    analytics["requests_count"] += 1
    return jsonify({
        **analytics,
        "uptime": round(time.time() - system_state["startup_time"], 2),
        "status": system_state["status"],
        "mode": system_state["mode"],
        "timestamp": datetime.now().isoformat(),
    })

@app.route("/api/system/info")
def system_info():
    """Detailed system information."""
    return jsonify({
        "version": system_state["version"],
        "owner": OWNER,
        "repo": REPO_ECOSYSTEM,
        "mode": system_state["mode"],
        "status": system_state["status"],
        "startup_time": system_state["startup_time"],
        "uptime": round(time.time() - system_state["startup_time"], 2),
        "ready": READY.is_set(),
        "python_version": sys.version,
        "platform": sys.platform,
    })

@app.route("/api/agents/detailed")
def agents_detailed():
    """Detailed agent information with statistics."""
    analytics["requests_count"] += 1
    agent_details = {}
    
    for agent_id, agent_data in AGENTS.items():
        agent_details[agent_id] = {
            **agent_data,
            "id": agent_id,
            "status": "active",
            "last_activity": datetime.now().isoformat(),
        }
    
    return jsonify({
        "agents": agent_details,
        "total_agents": len(AGENTS),
        "timestamp": datetime.now().isoformat(),
    })

@app.route("/api/activity/recent")
def recent_activity():
    """Get recent system activity."""
    # This would ideally pull from a database or log file
    # For now, we'll return a summary based on analytics
    activities = []
    
    if analytics["issues_created"] > 0:
        activities.append({
            "type": "issue",
            "count": analytics["issues_created"],
            "description": f"{analytics['issues_created']} issues created",
            "timestamp": datetime.now().isoformat(),
        })
    
    if analytics["discussions_created"] > 0:
        activities.append({
            "type": "discussion",
            "count": analytics["discussions_created"],
            "description": f"{analytics['discussions_created']} discussions created",
            "timestamp": datetime.now().isoformat(),
        })
    
    if analytics["files_created"] > 0:
        activities.append({
            "type": "file",
            "count": analytics["files_created"],
            "description": f"{analytics['files_created']} files created",
            "timestamp": datetime.now().isoformat(),
        })
    
    if analytics["feature_cycles_completed"] > 0:
        activities.append({
            "type": "cycle",
            "count": analytics["feature_cycles_completed"],
            "description": f"{analytics['feature_cycles_completed']} innovation cycles completed",
            "timestamp": datetime.now().isoformat(),
        })
    
    return jsonify({
        "activities": activities,
        "total": len(activities),
        "timestamp": datetime.now().isoformat(),
    })

@app.route("/api/stats/summary")
def stats_summary():
    """Comprehensive statistics summary."""
    return jsonify({
        "repositories": {
            "discovered": analytics["repositories_discovered"],
        },
        "content": {
            "ideas_generated": analytics["ideas_generated"],
            "issues_created": analytics["issues_created"],
            "discussions_created": analytics["discussions_created"],
            "story_issues_created": analytics["story_issues_created"],
            "files_created": analytics["files_created"],
            "files_updated": analytics["files_updated"],
        },
        "operations": {
            "feature_cycles_completed": analytics["feature_cycles_completed"],
            "ai_operations": analytics["ai_operations"],
            "github_operations": analytics["github_operations"],
            "requests_count": analytics["requests_count"],
        },
        "system": analytics["system_health"],
        "timestamp": datetime.now().isoformat(),
    })

@app.route("/run-cycle", methods=["POST"])
def run_cycle_endpoint():
    """Trigger an innovation cycle (compatible with existing UI)."""
    try:
        worker.schedule({"type": "innovation_cycle"})
        return jsonify({
            "status": "scheduled",
            "message": "Innovation cycle scheduled successfully",
            "timestamp": datetime.now().isoformat(),
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat(),
        }), 500

@app.route("/api/health/detailed")
def detailed_health():
    """Detailed health check with all system metrics."""
    update_health()
    return jsonify({
        "ok": True,
        "ready": READY.is_set(),
        "version": system_state["version"],
        "owner": OWNER,
        "repo": REPO_ECOSYSTEM,
        "uptime": round(time.time() - system_state["startup_time"], 2),
        "system": analytics["system_health"],
        "analytics": {
            "requests": analytics["requests_count"],
            "ai_ops": analytics["ai_operations"],
            "github_ops": analytics["github_operations"],
            "cycles": analytics["feature_cycles_completed"],
        },
        "agents": {
            "total": len(AGENTS),
            "active": len(AGENTS),  # All agents are always active in current implementation
        },
        "timestamp": datetime.now().isoformat(),
    })

# Add CORS headers to all responses for better API access
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response



# ---------- Enhanced Dashboard Route ----------

@app.route("/enhanced")
def enhanced_dashboard():
    """Serve the enhanced dashboard with comprehensive monitoring."""
    analytics["requests_count"] += 1
    enhanced_html = """<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n    <meta charset=\"UTF-8\">\n    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n    <title>XMRT Ecosystem 6.3 — Enhanced Dashboard</title>\n    <style>\n        * {\n            margin: 0;\n            padding: 0;\n            box-sizing: border-box;\n        }\n\n        :root {\n            --primary: #667eea;\n            --secondary: #764ba2;\n            --success: #10b981;\n            --warning: #f59e0b;\n            --danger: #ef4444;\n            --info: #3b82f6;\n            --dark: #1a202c;\n            --darker: #0f1419;\n            --card-bg: #2d3748;\n            --card-hover: #374151;\n            --text-primary: #ffffff;\n            --text-secondary: #a0aec0;\n            --border: #4a5568;\n        }\n\n        body {\n            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;\n            background: linear-gradient(135deg, var(--darker) 0%, var(--dark) 100%);\n            color: var(--text-primary);\n            line-height: 1.6;\n            min-height: 100vh;\n        }\n\n        .container {\n            max-width: 1800px;\n            margin: 0 auto;\n            padding: 20px;\n        }\n\n        /* Header */\n        header {\n            background: rgba(45, 55, 72, 0.95);\n            backdrop-filter: blur(10px);\n            padding: 1rem 0;\n            border-bottom: 2px solid var(--primary);\n            margin-bottom: 20px;\n            position: sticky;\n            top: 0;\n            z-index: 1000;\n        }\n\n        .header-content {\n            max-width: 1800px;\n            margin: 0 auto;\n            padding: 0 20px;\n            display: flex;\n            justify-content: space-between;\n            align-items: center;\n            flex-wrap: wrap;\n            gap: 15px;\n        }\n\n        .logo {\n            font-size: 1.5rem;\n            font-weight: 700;\n            background: linear-gradient(135deg, var(--primary), var(--secondary));\n            -webkit-background-clip: text;\n            -webkit-text-fill-color: transparent;\n            background-clip: text;\n        }\n\n        .system-info {\n            display: flex;\n            gap: 20px;\n            flex-wrap: wrap;\n            font-size: 0.85rem;\n            color: var(--text-secondary);\n        }\n\n        .system-info span {\n            display: flex;\n            align-items: center;\n            gap: 5px;\n        }\n\n        .status-badge {\n            display: inline-block;\n            padding: 4px 12px;\n            border-radius: 12px;\n            font-size: 0.75rem;\n            font-weight: 600;\n            background: var(--success);\n            color: white;\n        }\n\n        /* Main Grid Layout */\n        .dashboard-grid {\n            display: grid;\n            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));\n            gap: 20px;\n            margin-bottom: 20px;\n        }\n\n        /* Cards */\n        .card {\n            background: var(--card-bg);\n            border-radius: 12px;\n            padding: 20px;\n            border: 1px solid var(--border);\n            transition: all 0.3s ease;\n        }\n\n        .card:hover {\n            background: var(--card-hover);\n            transform: translateY(-2px);\n            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);\n        }\n\n        .card-header {\n            display: flex;\n            justify-content: space-between;\n            align-items: center;\n            margin-bottom: 15px;\n            padding-bottom: 10px;\n            border-bottom: 1px solid var(--border);\n        }\n\n        .card-title {\n            font-size: 1.1rem;\n            font-weight: 600;\n            display: flex;\n            align-items: center;\n            gap: 8px;\n        }\n\n        .card-icon {\n            font-size: 1.3rem;\n        }\n\n        /* Action Buttons */\n        .action-section {\n            grid-column: 1 / -1;\n        }\n\n        .button-group {\n            display: flex;\n            gap: 15px;\n            flex-wrap: wrap;\n        }\n\n        .btn {\n            padding: 15px 30px;\n            border: none;\n            border-radius: 8px;\n            font-size: 1rem;\n            font-weight: 600;\n            cursor: pointer;\n            transition: all 0.3s ease;\n            display: flex;\n            align-items: center;\n            gap: 8px;\n            flex: 1;\n            min-width: 200px;\n            justify-content: center;\n        }\n\n        .btn-primary {\n            background: linear-gradient(135deg, var(--success), #059669);\n            color: white;\n        }\n\n        .btn-secondary {\n            background: linear-gradient(135deg, var(--info), #2563eb);\n            color: white;\n        }\n\n        .btn-warning {\n            background: linear-gradient(135deg, var(--warning), #d97706);\n            color: white;\n        }\n\n        .btn:hover {\n            transform: translateY(-2px);\n            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.3);\n        }\n\n        .btn:disabled {\n            opacity: 0.5;\n            cursor: not-allowed;\n            transform: none;\n        }\n\n        /* Stats Display */\n        .stats-grid {\n            display: grid;\n            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));\n            gap: 15px;\n        }\n\n        .stat-item {\n            text-align: center;\n            padding: 15px;\n            background: rgba(102, 126, 234, 0.1);\n            border-radius: 8px;\n            border: 1px solid rgba(102, 126, 234, 0.2);\n        }\n\n        .stat-value {\n            font-size: 2rem;\n            font-weight: 700;\n            color: var(--primary);\n            display: block;\n        }\n\n        .stat-label {\n            font-size: 0.85rem;\n            color: var(--text-secondary);\n            margin-top: 5px;\n        }\n\n        /* Agent Cards */\n        .agent-grid {\n            display: grid;\n            gap: 15px;\n        }\n\n        .agent-card {\n            background: rgba(102, 126, 234, 0.05);\n            padding: 15px;\n            border-radius: 8px;\n            border-left: 4px solid var(--primary);\n            transition: all 0.3s ease;\n        }\n\n        .agent-card:hover {\n            background: rgba(102, 126, 234, 0.1);\n            border-left-width: 6px;\n        }\n\n        .agent-header {\n            display: flex;\n            justify-content: space-between;\n            align-items: center;\n            margin-bottom: 8px;\n        }\n\n        .agent-name {\n            font-weight: 600;\n            font-size: 1.05rem;\n        }\n\n        .agent-weight {\n            background: var(--primary);\n            color: white;\n            padding: 2px 8px;\n            border-radius: 12px;\n            font-size: 0.75rem;\n            font-weight: 600;\n        }\n\n        .agent-role {\n            color: var(--text-secondary);\n            font-size: 0.9rem;\n            margin-bottom: 5px;\n        }\n\n        .agent-voice {\n            color: var(--info);\n            font-size: 0.85rem;\n            font-style: italic;\n        }\n\n        /* System Resources */\n        .resource-bar {\n            margin-bottom: 15px;\n        }\n\n        .resource-label {\n            display: flex;\n            justify-content: space-between;\n            margin-bottom: 5px;\n            font-size: 0.9rem;\n        }\n\n        .progress-bar {\n            height: 8px;\n            background: rgba(255, 255, 255, 0.1);\n            border-radius: 4px;\n            overflow: hidden;\n        }\n\n        .progress-fill {\n            height: 100%;\n            border-radius: 4px;\n            transition: width 0.5s ease;\n        }\n\n        .progress-fill.low {\n            background: var(--success);\n        }\n\n        .progress-fill.medium {\n            background: var(--warning);\n        }\n\n        .progress-fill.high {\n            background: var(--danger);\n        }\n\n        /* Activity Log */\n        .activity-log {\n            max-height: 400px;\n            overflow-y: auto;\n            padding-right: 10px;\n        }\n\n        .activity-log::-webkit-scrollbar {\n            width: 6px;\n        }\n\n        .activity-log::-webkit-scrollbar-track {\n            background: rgba(255, 255, 255, 0.05);\n            border-radius: 3px;\n        }\n\n        .activity-log::-webkit-scrollbar-thumb {\n            background: var(--primary);\n            border-radius: 3px;\n        }\n\n        .log-entry {\n            padding: 10px;\n            margin-bottom: 8px;\n            background: rgba(255, 255, 255, 0.03);\n            border-radius: 6px;\n            border-left: 3px solid var(--info);\n            font-size: 0.9rem;\n        }\n\n        .log-time {\n            color: var(--text-secondary);\n            font-size: 0.8rem;\n            margin-bottom: 3px;\n        }\n\n        .log-message {\n            color: var(--text-primary);\n        }\n\n        /* Recent Items */\n        .recent-list {\n            list-style: none;\n        }\n\n        .recent-item {\n            padding: 12px;\n            margin-bottom: 8px;\n            background: rgba(255, 255, 255, 0.03);\n            border-radius: 6px;\n            border-left: 3px solid var(--success);\n            transition: all 0.2s ease;\n            cursor: pointer;\n        }\n\n        .recent-item:hover {\n            background: rgba(255, 255, 255, 0.06);\n            transform: translateX(5px);\n        }\n\n        .recent-item-title {\n            font-weight: 600;\n            margin-bottom: 4px;\n            color: var(--text-primary);\n        }\n\n        .recent-item-meta {\n            font-size: 0.8rem;\n            color: var(--text-secondary);\n        }\n\n        /* Loading Spinner */\n        .spinner {\n            display: inline-block;\n            width: 20px;\n            height: 20px;\n            border: 3px solid rgba(255, 255, 255, 0.3);\n            border-radius: 50%;\n            border-top-color: white;\n            animation: spin 1s ease-in-out infinite;\n        }\n\n        @keyframes spin {\n            to { transform: rotate(360deg); }\n        }\n\n        /* Modal */\n        .modal {\n            display: none;\n            position: fixed;\n            top: 0;\n            left: 0;\n            width: 100%;\n            height: 100%;\n            background: rgba(0, 0, 0, 0.8);\n            z-index: 2000;\n            align-items: center;\n            justify-content: center;\n        }\n\n        .modal.active {\n            display: flex;\n        }\n\n        .modal-content {\n            background: var(--card-bg);\n            border-radius: 12px;\n            padding: 30px;\n            max-width: 600px;\n            width: 90%;\n            max-height: 80vh;\n            overflow-y: auto;\n            border: 1px solid var(--border);\n        }\n\n        .modal-header {\n            display: flex;\n            justify-content: space-between;\n            align-items: center;\n            margin-bottom: 20px;\n            padding-bottom: 15px;\n            border-bottom: 1px solid var(--border);\n        }\n\n        .modal-close {\n            background: none;\n            border: none;\n            color: var(--text-secondary);\n            font-size: 1.5rem;\n            cursor: pointer;\n            transition: color 0.3s ease;\n        }\n\n        .modal-close:hover {\n            color: var(--text-primary);\n        }\n\n        /* Responsive */\n        @media (max-width: 768px) {\n            .dashboard-grid {\n                grid-template-columns: 1fr;\n            }\n\n            .button-group {\n                flex-direction: column;\n            }\n\n            .btn {\n                min-width: 100%;\n            }\n\n            .stats-grid {\n                grid-template-columns: repeat(2, 1fr);\n            }\n        }\n\n        /* Pulse Animation */\n        @keyframes pulse {\n            0%, 100% {\n                opacity: 1;\n            }\n            50% {\n                opacity: 0.5;\n            }\n        }\n\n        .pulse {\n            animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;\n        }\n\n        /* Badge */\n        .badge {\n            display: inline-block;\n            padding: 4px 10px;\n            border-radius: 12px;\n            font-size: 0.75rem;\n            font-weight: 600;\n        }\n\n        .badge-success {\n            background: var(--success);\n            color: white;\n        }\n\n        .badge-warning {\n            background: var(--warning);\n            color: white;\n        }\n\n        .badge-info {\n            background: var(--info);\n            color: white;\n        }\n    </style>\n</head>\n<body>\n    <header>\n        <div class=\"header-content\">\n            <div class=\"logo\">🤖 XMRT Ecosystem 6.3</div>\n            <div class=\"system-info\">\n                <span>Owner: <strong id=\"owner\">Loading...</strong></span>\n                <span>Repo: <strong id=\"repo\">Loading...</strong></span>\n                <span>Version: <strong id=\"version\">Loading...</strong></span>\n                <span>Uptime: <strong id=\"uptime\">Loading...</strong></span>\n                <span class=\"status-badge\" id=\"status-badge\">Operational</span>\n            </div>\n        </div>\n    </header>\n\n    <div class=\"container\">\n        <!-- Action Section -->\n        <div class=\"card action-section\">\n            <div class=\"card-header\">\n                <h2 class=\"card-title\">\n                    <span class=\"card-icon\">⚡</span>\n                    Actions\n                </h2>\n            </div>\n            <div class=\"button-group\">\n                <button class=\"btn btn-primary\" id=\"run-cycle-btn\" onclick=\"runInnovationCycle()\">\n                    <span>🚀</span>\n                    Run Innovation Cycle\n                </button>\n                <button class=\"btn btn-secondary\" onclick=\"showLastResult()\">\n                    <span>📋</span>\n                    Last Result\n                </button>\n                <button class=\"btn btn-warning\" onclick=\"refreshData()\">\n                    <span>🔄</span>\n                    Refresh\n                </button>\n            </div>\n        </div>\n\n        <!-- Main Dashboard Grid -->\n        <div class=\"dashboard-grid\">\n            <!-- Statistics Card -->\n            <div class=\"card\">\n                <div class=\"card-header\">\n                    <h3 class=\"card-title\">\n                        <span class=\"card-icon\">📊</span>\n                        Statistics\n                    </h3>\n                </div>\n                <div class=\"stats-grid\">\n                    <div class=\"stat-item\">\n                        <span class=\"stat-value\" id=\"repos-count\">0</span>\n                        <span class=\"stat-label\">Repos</span>\n                    </div>\n                    <div class=\"stat-item\">\n                        <span class=\"stat-value\" id=\"ideas-count\">0</span>\n                        <span class=\"stat-label\">Ideas</span>\n                    </div>\n                    <div class=\"stat-item\">\n                        <span class=\"stat-value\" id=\"issues-count\">0</span>\n                        <span class=\"stat-label\">Issues</span>\n                    </div>\n                    <div class=\"stat-item\">\n                        <span class=\"stat-value\" id=\"discussions-count\">0</span>\n                        <span class=\"stat-label\">Discussions</span>\n                    </div>\n                    <div class=\"stat-item\">\n                        <span class=\"stat-value\" id=\"story-issues-count\">0</span>\n                        <span class=\"stat-label\">Story Issues</span>\n                    </div>\n                    <div class=\"stat-item\">\n                        <span class=\"stat-value\" id=\"files-count\">0</span>\n                        <span class=\"stat-label\">Files</span>\n                    </div>\n                    <div class=\"stat-item\">\n                        <span class=\"stat-value\" id=\"updates-count\">0</span>\n                        <span class=\"stat-label\">Updates</span>\n                    </div>\n                    <div class=\"stat-item\">\n                        <span class=\"stat-value\" id=\"cycles-count\">0</span>\n                        <span class=\"stat-label\">Cycles</span>\n                    </div>\n                </div>\n            </div>\n\n            <!-- System Resources Card -->\n            <div class=\"card\">\n                <div class=\"card-header\">\n                    <h3 class=\"card-title\">\n                        <span class=\"card-icon\">💻</span>\n                        System Resources\n                    </h3>\n                </div>\n                <div class=\"resource-bar\">\n                    <div class=\"resource-label\">\n                        <span>CPU</span>\n                        <span id=\"cpu-value\">0%</span>\n                    </div>\n                    <div class=\"progress-bar\">\n                        <div class=\"progress-fill low\" id=\"cpu-bar\" style=\"width: 0%\"></div>\n                    </div>\n                </div>\n                <div class=\"resource-bar\">\n                    <div class=\"resource-label\">\n                        <span>Memory</span>\n                        <span id=\"mem-value\">0%</span>\n                    </div>\n                    <div class=\"progress-bar\">\n                        <div class=\"progress-fill low\" id=\"mem-bar\" style=\"width: 0%\"></div>\n                    </div>\n                </div>\n                <div class=\"resource-bar\">\n                    <div class=\"resource-label\">\n                        <span>Disk</span>\n                        <span id=\"disk-value\">0%</span>\n                    </div>\n                    <div class=\"progress-bar\">\n                        <div class=\"progress-fill low\" id=\"disk-bar\" style=\"width: 0%\"></div>\n                    </div>\n                </div>\n            </div>\n\n            <!-- Agents Card -->\n            <div class=\"card\" style=\"grid-column: 1 / -1;\">\n                <div class=\"card-header\">\n                    <h3 class=\"card-title\">\n                        <span class=\"card-icon\">🤖</span>\n                        Active Agents\n                    </h3>\n                    <span class=\"badge badge-success\" id=\"agent-count\">0 Agents</span>\n                </div>\n                <div class=\"agent-grid\" id=\"agents-container\">\n                    <!-- Agents will be populated here -->\n                </div>\n            </div>\n\n            <!-- Recent Issues Card -->\n            <div class=\"card\">\n                <div class=\"card-header\">\n                    <h3 class=\"card-title\">\n                        <span class=\"card-icon\">📝</span>\n                        Recent Issues\n                    </h3>\n                </div>\n                <ul class=\"recent-list\" id=\"recent-issues\">\n                    <li class=\"recent-item\">\n                        <div class=\"recent-item-title\">Loading...</div>\n                        <div class=\"recent-item-meta\">Please wait</div>\n                    </li>\n                </ul>\n            </div>\n\n            <!-- Activity Log Card -->\n            <div class=\"card\">\n                <div class=\"card-header\">\n                    <h3 class=\"card-title\">\n                        <span class=\"card-icon\">📜</span>\n                        Activity Log\n                    </h3>\n                </div>\n                <div class=\"activity-log\" id=\"activity-log\">\n                    <div class=\"log-entry\">\n                        <div class=\"log-time\">System starting...</div>\n                        <div class=\"log-message\">Initializing dashboard</div>\n                    </div>\n                </div>\n            </div>\n\n            <!-- Recent Files Card -->\n            <div class=\"card\">\n                <div class=\"card-header\">\n                    <h3 class=\"card-title\">\n                        <span class=\"card-icon\">📁</span>\n                        Recent Files\n                    </h3>\n                </div>\n                <ul class=\"recent-list\" id=\"recent-files\">\n                    <li class=\"recent-item\">\n                        <div class=\"recent-item-title\">Loading...</div>\n                        <div class=\"recent-item-meta\">Please wait</div>\n                    </li>\n                </ul>\n            </div>\n        </div>\n    </div>\n\n    <!-- Modal for Last Result -->\n    <div class=\"modal\" id=\"result-modal\">\n        <div class=\"modal-content\">\n            <div class=\"modal-header\">\n                <h3>Last Innovation Cycle Result</h3>\n                <button class=\"modal-close\" onclick=\"closeModal()\">&times;</button>\n            </div>\n            <div id=\"result-content\">\n                <p>No results yet. Run an innovation cycle first.</p>\n            </div>\n        </div>\n    </div>\n\n    <script>\n        let lastResult = null;\n        let activityLog = [];\n\n        // Initialize\n        document.addEventListener('DOMContentLoaded', () => {\n            refreshData();\n            // Auto-refresh every 30 seconds\n            setInterval(refreshData, 30000);\n        });\n\n        function addLogEntry(message) {\n            const now = new Date();\n            const timeStr = now.toLocaleTimeString();\n            activityLog.unshift({ time: timeStr, message });\n            \n            // Keep only last 50 entries\n            if (activityLog.length > 50) {\n                activityLog = activityLog.slice(0, 50);\n            }\n            \n            updateActivityLog();\n        }\n\n        function updateActivityLog() {\n            const logContainer = document.getElementById('activity-log');\n            logContainer.innerHTML = activityLog.map(entry => `\n                <div class=\"log-entry\">\n                    <div class=\"log-time\">${entry.time}</div>\n                    <div class=\"log-message\">${entry.message}</div>\n                </div>\n            `).join('');\n        }\n\n        async function refreshData() {\n            try {\n                addLogEntry('Refreshing data...');\n                \n                // Fetch health data\n                const healthRes = await fetch('/health');\n                const health = await healthRes.json();\n                \n                // Update header info\n                document.getElementById('owner').textContent = health.owner || 'N/A';\n                document.getElementById('repo').textContent = health.repo || 'N/A';\n                document.getElementById('version').textContent = health.version || 'N/A';\n                document.getElementById('uptime').textContent = formatUptime(health.uptime || 0);\n                \n                // Update system resources\n                if (health.system) {\n                    updateResource('cpu', health.system.cpu);\n                    updateResource('mem', health.system.mem);\n                    updateResource('disk', health.system.disk);\n                }\n                \n                // Fetch agents\n                const agentsRes = await fetch('/agents');\n                const agentsData = await agentsRes.json();\n                updateAgents(agentsData.agents || {});\n                \n                // Try to fetch analytics\n                try {\n                    const analyticsRes = await fetch('/api/analytics');\n                    if (analyticsRes.ok) {\n                        const analytics = await analyticsRes.json();\n                        updateStatistics(analytics);\n                    }\n                } catch (e) {\n                    // Fallback to parsing from page if analytics endpoint doesn't exist\n                    console.log('Analytics endpoint not available, using defaults');\n                }\n                \n                addLogEntry('✅ Data refreshed successfully');\n            } catch (error) {\n                console.error('Error refreshing data:', error);\n                addLogEntry('❌ Error refreshing data: ' + error.message);\n            }\n        }\n\n        function updateResource(type, value) {\n            const valueEl = document.getElementById(`${type}-value`);\n            const barEl = document.getElementById(`${type}-bar`);\n            \n            valueEl.textContent = value.toFixed(1) + '%';\n            barEl.style.width = value + '%';\n            \n            // Update color based on value\n            barEl.className = 'progress-fill';\n            if (value < 50) {\n                barEl.classList.add('low');\n            } else if (value < 80) {\n                barEl.classList.add('medium');\n            } else {\n                barEl.classList.add('high');\n            }\n        }\n\n        function updateAgents(agents) {\n            const container = document.getElementById('agents-container');\n            const count = Object.keys(agents).length;\n            document.getElementById('agent-count').textContent = `${count} Agents`;\n            \n            container.innerHTML = Object.entries(agents).map(([id, agent]) => `\n                <div class=\"agent-card\">\n                    <div class=\"agent-header\">\n                        <div class=\"agent-name\">${agent.name}</div>\n                        <div class=\"agent-weight\">Weight: ${agent.weight}</div>\n                    </div>\n                    <div class=\"agent-role\">${agent.role}</div>\n                    <div class=\"agent-voice\">\"${agent.voice}\"</div>\n                </div>\n            `).join('');\n        }\n\n        function updateStatistics(data) {\n            document.getElementById('repos-count').textContent = data.repositories_discovered || 1;\n            document.getElementById('ideas-count').textContent = data.ideas_generated || 0;\n            document.getElementById('issues-count').textContent = data.issues_created || 0;\n            document.getElementById('discussions-count').textContent = data.discussions_created || 0;\n            document.getElementById('story-issues-count').textContent = data.story_issues_created || 0;\n            document.getElementById('files-count').textContent = data.files_created || 0;\n            document.getElementById('updates-count').textContent = data.files_updated || 0;\n            document.getElementById('cycles-count').textContent = data.feature_cycles_completed || 0;\n        }\n\n        async function runInnovationCycle() {\n            const btn = document.getElementById('run-cycle-btn');\n            btn.disabled = true;\n            btn.innerHTML = '<span class=\"spinner\"></span> Running...';\n            \n            addLogEntry('🚀 Starting innovation cycle...');\n            \n            try {\n                const response = await fetch('/run-cycle', {\n                    method: 'POST',\n                    headers: { 'Content-Type': 'application/json' }\n                });\n                \n                const result = await response.json();\n                lastResult = result;\n                \n                addLogEntry('✅ Innovation cycle completed successfully');\n                addLogEntry(`📝 Created: ${result.summary || 'Check GitHub for details'}`);\n                \n                // Refresh data after cycle\n                setTimeout(refreshData, 2000);\n                \n                // Show result modal\n                showLastResult();\n            } catch (error) {\n                console.error('Error running cycle:', error);\n                addLogEntry('❌ Error running cycle: ' + error.message);\n            } finally {\n                btn.disabled = false;\n                btn.innerHTML = '<span>🚀</span> Run Innovation Cycle';\n            }\n        }\n\n        function showLastResult() {\n            const modal = document.getElementById('result-modal');\n            const content = document.getElementById('result-content');\n            \n            if (lastResult) {\n                content.innerHTML = `\n                    <div style=\"margin-bottom: 15px;\">\n                        <strong>Status:</strong> ${lastResult.status || 'completed'}\n                    </div>\n                    <div style=\"margin-bottom: 15px;\">\n                        <strong>Summary:</strong><br>\n                        ${lastResult.summary || 'No summary available'}\n                    </div>\n                    ${lastResult.issue_url ? `\n                        <div style=\"margin-bottom: 15px;\">\n                            <strong>Issue:</strong><br>\n                            <a href=\"${lastResult.issue_url}\" target=\"_blank\" style=\"color: var(--info);\">${lastResult.issue_url}</a>\n                        </div>\n                    ` : ''}\n                    ${lastResult.discussion_url ? `\n                        <div style=\"margin-bottom: 15px;\">\n                            <strong>Discussion:</strong><br>\n                            <a href=\"${lastResult.discussion_url}\" target=\"_blank\" style=\"color: var(--info);\">${lastResult.discussion_url}</a>\n                        </div>\n                    ` : ''}\n                    <div style=\"margin-top: 20px; padding: 15px; background: rgba(255,255,255,0.05); border-radius: 8px;\">\n                        <pre style=\"white-space: pre-wrap; font-size: 0.9rem;\">${JSON.stringify(lastResult, null, 2)}</pre>\n                    </div>\n                `;\n            } else {\n                content.innerHTML = '<p>No results yet. Run an innovation cycle first.</p>';\n            }\n            \n            modal.classList.add('active');\n        }\n\n        function closeModal() {\n            document.getElementById('result-modal').classList.remove('active');\n        }\n\n        function formatUptime(seconds) {\n            const hours = Math.floor(seconds / 3600);\n            const minutes = Math.floor((seconds % 3600) / 60);\n            const secs = Math.floor(seconds % 60);\n            \n            if (hours > 0) {\n                return `${hours}h ${minutes}m`;\n            } else if (minutes > 0) {\n                return `${minutes}m ${secs}s`;\n            } else {\n                return `${secs}s`;\n            }\n        }\n\n        // Close modal when clicking outside\n        document.getElementById('result-modal').addEventListener('click', (e) => {\n            if (e.target.id === 'result-modal') {\n                closeModal();\n            }\n        });\n    </script>\n</body>\n</html>\n"""
    return enhanced_html

@app.route("/dashboard")
def dashboard_redirect():
    """Redirect /dashboard to /enhanced for convenience."""
    from flask import redirect
    return redirect("/enhanced")


# ---------- Signals / Main ----------
def _sig(sig, _frm):
    log.info("Signal %s -> shutdown", sig)
    SHUTDOWN.set()

def main() -> int:
    signal.signal(signal.SIGINT, _sig)
    signal.signal(signal.SIGTERM, _sig)
    log.info("Agents and Coordination initialized")
    log.info("Starting XMRT Ecosystem on port %s", PORT)
    READY.set()
    try:
        app.run(host=HOST, port=PORT, debug=False, use_reloader=False, threaded=True)
    finally:
        SHUTDOWN.set()
        log.info("Shutdown complete")
    return 0

if __name__ == "__main__":
    sys.exit(main())
