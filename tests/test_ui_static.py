import re
import shutil
import subprocess

from fastapi.testclient import TestClient

from app.main import app


def _home_page() -> str:
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    return response.text


def test_ui_script_is_valid_javascript():
    if shutil.which("node") is None:
        raise AssertionError("Node.js is required to validate the UI script syntax.")

    html = _home_page()
    match = re.search(r"<script>([\s\S]*)</script>", html)
    assert match is not None

    result = subprocess.run(
        ["node", "-e", "new Function(process.argv[1]); console.log('ok');", match.group(1)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "ok" in result.stdout


def test_ui_exposes_main_controls_and_bindings():
    html = _home_page()

    assert 'id="runBtn"' in html
    assert 'id="clearBtn"' in html
    assert 'id="historyBtn"' in html
    assert 'id="refreshHistoryBtn"' in html
    assert 'id="copyCodeBtn"' in html
    assert 'id="promptInput"' in html
    assert 'id="userIdInput"' in html
    assert 'runBtn.addEventListener("click", executeQuery)' in html
    assert 'clearBtn.addEventListener("click", resetAll)' in html
    assert 'historyBtn.addEventListener("click", loadHistory)' in html
    assert 'refreshHistoryBtn.addEventListener("click", loadHistory)' in html
    assert 'copyCodeBtn.addEventListener("click", async () => {' in html
    assert 'document.querySelectorAll(".preset-chip").forEach' in html


def test_ui_disables_dax_route_in_local_mode():
    html = _home_page()

    assert '<option value="powerbi" disabled>DAX - bientot</option>' in html
    assert 'routeSelect.value = entry.route === "sql" || entry.route === "rag"' in html
