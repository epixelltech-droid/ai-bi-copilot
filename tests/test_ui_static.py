import re
import shutil
import subprocess
import tempfile
from pathlib import Path

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
    assert 'id="tableFilterInput"' in html
    assert 'id="exportCsvBtn"' in html
    assert 'https://cdn.plot.ly/plotly-2.35.2.min.js' in html
    assert 'renderPlotlyVisualization(data.visualization, data.data)' in html
    assert 'id="promptInput"' in html
    assert 'id="userIdInput"' in html
    assert 'runBtn.addEventListener("click", executeQuery)' in html
    assert 'clearBtn.addEventListener("click", resetAll)' in html
    assert 'historyBtn.addEventListener("click", loadHistory)' in html
    assert 'refreshHistoryBtn.addEventListener("click", loadHistory)' in html
    assert 'copyCodeBtn.addEventListener("click", async () => {' in html
    assert 'tableFilterInput.addEventListener("input", () => {' in html
    assert 'exportCsvBtn.addEventListener("click", () => {' in html
    assert 'document.querySelectorAll(".preset-chip").forEach' in html


def test_ui_disables_dax_route_in_local_mode():
    html = _home_page()

    assert '<option value="powerbi" disabled>DAX - bientot</option>' in html
    assert 'routeSelect.value = entry.route === "sql" || entry.route === "rag"' in html


def test_ui_button_flows_work_in_node_harness():
    if shutil.which("node") is None:
        raise AssertionError("Node.js is required to validate UI interactions.")

    html = _home_page()
    script = r"""
const fs = require("fs");

class FakeElement {
  constructor(id = "") {
    this.id = id;
    this.value = "";
    this.textContent = "";
    this.innerHTML = "";
    this.className = "";
    this.disabled = false;
    this.style = {};
    this.dataset = {};
    this.listeners = {};
    this._queryCache = {};
    this.classList = {
      add: (...names) => {
        const existing = new Set(this.className.split(" ").filter(Boolean));
        names.forEach((name) => existing.add(name));
        this.className = Array.from(existing).join(" ");
      },
    };
  }

  addEventListener(name, handler) {
    this.listeners[name] = handler;
  }

  async click() {
    if (this.listeners.click) {
      await this.listeners.click({ target: this, preventDefault() {} });
    }
  }

  async dispatch(name) {
    if (this.listeners[name]) {
      await this.listeners[name]({ target: this, preventDefault() {} });
    }
  }

  focus() {
    this.focused = true;
  }

  querySelectorAll(selector) {
    if (selector === "th[data-column]") {
      if (this._queryCache.html !== this.innerHTML) {
        this._queryCache.html = this.innerHTML;
        this._queryCache.headers = Array.from(this.innerHTML.matchAll(/data-column="([^"]+)"/g)).map((match) => {
          const element = new FakeElement("header-" + match[1]);
          element.dataset.column = match[1];
          return element;
        });
      }
      return this._queryCache.headers || [];
    }
    return [];
  }
}

const html = fs.readFileSync(0, "utf8");
const match = html.match(/<script>([\s\S]*)<\/script>/);
if (!match) {
  throw new Error("UI script not found");
}

const ids = [
  "promptInput",
  "userIdInput",
  "routeSelect",
  "runBtn",
  "clearBtn",
  "historyBtn",
  "refreshHistoryBtn",
  "answerText",
  "routeBadge",
  "auditBadge",
  "artifactBadge",
  "rowCountBadge",
  "sourcesRow",
  "sourcesContainer",
  "codeBlock",
  "tableContainer",
  "tableFilterInput",
  "exportCsvBtn",
  "copyCodeBtn",
  "historyList",
  "resolvedQuestionValue",
  "routeMetaValue",
  "dataMetaValue",
  "statMetric",
  "statMetricNote",
  "statLeader",
  "statLeaderNote",
  "statReading",
  "statReadingNote",
  "vizContainer",
];

const elements = Object.fromEntries(ids.map((id) => [id, new FakeElement(id)]));
elements.routeSelect.value = "auto";
elements.userIdInput.value = "portfolio-user";
elements.sourcesRow.style.display = "none";

const presetChips = [
  new FakeElement("preset-0"),
  new FakeElement("preset-1"),
];
presetChips[0].dataset.q = "Quel est le chiffre d'affaires par pays ?";
presetChips[1].dataset.q = "Comment calcule-t-on l'ASP ?";

let historyRequests = 0;
let chatRequests = 0;
let clipboardValue = "";
let anchorClicks = 0;
let exportedHref = "";
let plotlyRenderCount = 0;

global.document = {
  getElementById(id) {
    return elements[id];
  },
  querySelectorAll(selector) {
    if (selector === ".preset-chip") {
      return presetChips;
    }
    return [];
  },
  createElement(tag) {
    const element = new FakeElement(tag);
    if (tag === "a") {
      element.click = () => {
        anchorClicks += 1;
        exportedHref = element.href || "";
      };
    }
    return element;
  },
};

global.window = global;
global.Plotly = {
  newPlot(target, data, layout, config) {
    if (target !== "plotlyChart") {
      throw new Error("Plotly target mismatch");
    }
    if (!Array.isArray(data) || data[0].type !== "bar") {
      throw new Error("Plotly received an invalid trace");
    }
    plotlyRenderCount += 1;
    return Promise.resolve({ layout, config });
  },
};
global.navigator = {
  clipboard: {
    async writeText(value) {
      clipboardValue = value;
    },
  },
};
global.URL = {
  createObjectURL() {
    return "blob:demo";
  },
  revokeObjectURL() {},
};
global.Blob = function(parts, options) {
  this.parts = parts;
  this.options = options;
};
global.setTimeout = (fn) => {
  fn();
  return 1;
};
global.clearTimeout = () => {};

global.fetch = async (url, options = {}) => {
  if (String(url).startsWith("/api/history/")) {
    historyRequests += 1;
    return {
      ok: true,
      async json() {
        return [
          {
            timestamp_epoch: 1,
            audit_id: "audit-1",
            user_id: "portfolio-user",
            question: "Quel est le chiffre d'affaires par pays ?",
            resolved_question: "Quel est le chiffre d'affaires par pays ?",
            route: "sql",
            query_language: "SQL",
            status: "success",
            latency_ms: 25,
            row_count: 2,
            source_count: 0,
            used_memory: false,
            answer_preview: "Maroc en tete",
          },
        ];
      },
    };
  }

  if (url === "/api/chat") {
    chatRequests += 1;
    const payload = JSON.parse(options.body);
    const isRag = payload.question.includes("ASP");
    return {
      ok: true,
      async json() {
        if (isRag) {
          return {
            route: "rag",
            answer: "ASP = Revenue / Quantity",
            artifact: { language: "NONE", query: null },
            data: [],
            sources: ["kpi_dictionary.md"],
            audit_id: "audit-rag",
          };
        }
        return {
          route: "sql",
          answer: "Le Maroc est en tete.",
          artifact: { language: "SQL", query: "SELECT country, revenue FROM demo" },
          data: [
            { country: "France", revenue: 100 },
            { country: "Maroc", revenue: 200 },
          ],
          sources: [],
          visualization: {
            enabled: true,
            kind: "bar",
            title: "Revenue by Country",
            figure: {
              data: [{ type: "bar", x: ["Maroc", "France"], y: [200, 100] }],
              layout: { title: { text: "Revenue by Country" } },
              config: { displaylogo: false, responsive: true },
            },
          },
          audit_id: "audit-sql",
        };
      },
    };
  }

  throw new Error("Unexpected fetch call: " + url);
};

async function flush() {
  await Promise.resolve();
  await Promise.resolve();
}

(async () => {
  new Function(match[1])();
  await flush();

  if (historyRequests < 1) {
    throw new Error("Initial history load did not run");
  }

  elements.promptInput.value = "";
  await elements.runBtn.click();
  if (!elements.answerText.textContent.includes("Saisis une question")) {
    throw new Error("Empty-question message not shown");
  }

  elements.promptInput.value = "Quel est le chiffre d'affaires par pays ?";
  await elements.runBtn.click();
  await flush();
  if (elements.routeBadge.textContent !== "Moteur SQL") {
    throw new Error("SQL route badge not updated");
  }
  if (!elements.tableContainer.innerHTML.includes("France") || !elements.tableContainer.innerHTML.includes("Maroc")) {
    throw new Error("SQL rows not rendered");
  }
  if (plotlyRenderCount !== 1 || !elements.vizContainer.innerHTML.includes("plotlyChart")) {
    throw new Error("Plotly chart was not rendered");
  }

      elements.tableFilterInput.value = "Maroc";
      await elements.tableFilterInput.dispatch("input");
      if (elements.rowCountBadge.textContent !== "1 ligne") {
        throw new Error("Filter did not reduce visible rows");
      }

      elements.tableFilterInput.value = "";
      await elements.tableFilterInput.dispatch("input");
      const headers = elements.tableContainer.querySelectorAll("th[data-column]");
      const revenueHeader = headers.find((header) => header.dataset.column === "revenue");
      if (!revenueHeader) {
        throw new Error("Sortable revenue header not found");
      }
  await revenueHeader.click();
  await flush();
  const refreshedHeaders = elements.tableContainer.querySelectorAll("th[data-column]");
  const refreshedRevenueHeader = refreshedHeaders.find((header) => header.dataset.column === "revenue");
  await refreshedRevenueHeader.click();
  await flush();
      if (elements.tableContainer.innerHTML.indexOf("Maroc") > elements.tableContainer.innerHTML.indexOf("France")) {
        throw new Error("Descending sort did not place the top value first");
      }

      await elements.exportCsvBtn.click();
      if (anchorClicks !== 1 || exportedHref !== "blob:demo") {
        throw new Error("CSV export did not trigger");
      }

      if (!elements.codeBlock.textContent.includes("SELECT country")) {
        throw new Error("SQL artifact not displayed before copy");
      }
      await elements.copyCodeBtn.click();
      if (clipboardValue && !clipboardValue.includes("SELECT country")) {
        throw new Error("Copy action used the wrong query text");
      }
      if (elements.copyCodeBtn.textContent === "Indisponible") {
        throw new Error("Copy action fell back to the unavailable state");
      }

  const beforeHistoryRequests = historyRequests;
  await elements.historyBtn.click();
  await flush();
  if (historyRequests <= beforeHistoryRequests) {
    throw new Error("History button did not reload history");
  }

  await presetChips[1].click();
  await flush();
  if (elements.promptInput.value !== "Comment calcule-t-on l'ASP ?") {
    throw new Error("Preset button did not update the prompt");
  }
  if (elements.routeBadge.textContent !== "RAG local") {
    throw new Error("Preset-driven RAG flow not rendered");
  }

  await elements.clearBtn.click();
  if (elements.promptInput.value !== "" || elements.rowCountBadge.textContent !== "0 ligne") {
    throw new Error("Clear button did not reset the UI");
  }

  console.log("ok");
})().catch((error) => {
  console.error(error.stack || String(error));
  process.exit(1);
});
"""

    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as handle:
        handle.write(script)
        script_path = Path(handle.name)

    try:
        result = subprocess.run(
            ["node", str(script_path)],
            input=html,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
            timeout=30,
        )
    finally:
        script_path.unlink(missing_ok=True)

    assert result.returncode == 0, result.stderr
    assert "ok" in result.stdout
