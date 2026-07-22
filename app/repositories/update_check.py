import json
import urllib.error
import urllib.request
from dataclasses import dataclass

from app.version import GITHUB_REPO, __version__

_TIMEOUT_SECONDS = 6


@dataclass(frozen=True)
class UpdateCheckResult:
    current_version: str
    latest_version: str | None
    update_available: bool
    release_url: str | None
    error: str | None = None


def _version_tuple(version: str) -> tuple[int, ...]:
    cleaned = version.lstrip("vV")
    parts = []
    for chunk in cleaned.split("."):
        digits = "".join(c for c in chunk if c.isdigit())
        parts.append(int(digits) if digits else 0)
    return tuple(parts)


def check_for_update() -> UpdateCheckResult:
    url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    request = urllib.request.Request(
        url, headers={"Accept": "application/vnd.github+json"}
    )
    try:
        with urllib.request.urlopen(request, timeout=_TIMEOUT_SECONDS) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, ValueError) as error:
        return UpdateCheckResult(__version__, None, False, None, error=str(error))

    latest_version = payload.get("tag_name", "")
    release_url = payload.get("html_url")
    update_available = _version_tuple(latest_version) > _version_tuple(__version__)
    return UpdateCheckResult(__version__, latest_version, update_available, release_url)
