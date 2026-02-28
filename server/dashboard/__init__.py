"""Minimal HTML dashboard for testing and debugging."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from server.config import AppConfig
from server.dependencies import get_config

router = APIRouter()

_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>AI Model Server</title>
<style>
  body {{ font-family: sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; }}
  h1 {{ color: #2563eb; }}
  .status {{ color: #16a34a; font-weight: bold; }}
  table {{ border-collapse: collapse; width: 100%; margin-top: 1em; }}
  th, td {{ border: 1px solid #d1d5db; padding: 8px 12px; text-align: left; }}
  th {{ background: #f3f4f6; }}
  textarea {{ width: 100%; box-sizing: border-box; font-size: 14px; }}
  button {{ background: #2563eb; color: white; border: none; padding: 8px 18px;
            border-radius: 4px; cursor: pointer; margin-top: 6px; }}
  button:hover {{ background: #1d4ed8; }}
  pre {{ background: #f3f4f6; padding: 12px; border-radius: 4px; overflow-x: auto; white-space: pre-wrap; }}
  .section {{ margin-top: 2em; }}
</style>
</head>
<body>
<h1>🤖 AI Model Server</h1>
<p>Status: <span class="status">Running ✔</span></p>

<div class="section">
  <h2>Available Models</h2>
  <table>
    <thead><tr><th>Alias</th><th>Provider</th><th>Backend Model</th></tr></thead>
    <tbody>
      {model_rows}
    </tbody>
  </table>
</div>

<div class="section">
  <h2>Chat Tester</h2>
  <label>Model alias:<br/>
    <input id="modelInput" type="text" value="{first_model}" style="width:100%;box-sizing:border-box;padding:6px;font-size:14px;" />
  </label><br/><br/>
  <label>User message:<br/>
    <textarea id="msgInput" rows="4" placeholder="Type your message here..."></textarea>
  </label><br/>
  <button onclick="sendChat()">Send</button>
  <h3>Response</h3>
  <pre id="responseBox">—</pre>
</div>

<script>
async function sendChat() {{
  const model = document.getElementById('modelInput').value.trim();
  const msg   = document.getElementById('msgInput').value.trim();
  if (!model || !msg) {{ alert('Fill in both fields.'); return; }}
  document.getElementById('responseBox').textContent = 'Loading…';
  try {{
    const resp = await fetch('/v1/chat/completions', {{
      method: 'POST',
      headers: {{'Content-Type': 'application/json'}},
      body: JSON.stringify({{
        model: model,
        messages: [{{role: 'user', content: msg}}]
      }})
    }});
    const data = await resp.json();
    document.getElementById('responseBox').textContent = JSON.stringify(data, null, 2);
  }} catch(e) {{
    document.getElementById('responseBox').textContent = 'Error: ' + e;
  }}
}}
</script>
</body>
</html>
"""


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
@router.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
async def dashboard(config: AppConfig = Depends(get_config)) -> HTMLResponse:
    rows = "\n".join(
        f"<tr><td>{alias}</td><td>{cfg.provider}</td><td>{cfg.model}</td></tr>"
        for alias, cfg in config.models.items()
    )
    first_model = next(iter(config.models), "")
    html = _HTML_TEMPLATE.format(model_rows=rows or "<tr><td colspan=3><em>No models configured</em></td></tr>", first_model=first_model)
    return HTMLResponse(content=html)
