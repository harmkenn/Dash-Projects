import uuid
import zipfile
from pathlib import Path

from dash import Dash, html, page_container
from flask import jsonify, request


app = Dash(
    __name__,
    use_pages=True,
    title="Dash Projects",
    update_title="Working...",
)

UPLOAD_DIR = Path(__file__).resolve().parent / "generated" / ".uploads"


@app.server.post("/upload-takeout")
def upload_takeout():
    uploaded_file = request.files.get("file")
    if uploaded_file is None or not uploaded_file.filename:
        return jsonify(error="Choose a ZIP file to upload."), 400
    if Path(uploaded_file.filename).suffix.lower() != ".zip":
        return jsonify(error="Only ZIP files are supported."), 400

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    upload_id = uuid.uuid4().hex
    upload_path = UPLOAD_DIR / f"{upload_id}.zip"
    uploaded_file.save(upload_path)
    if not zipfile.is_zipfile(upload_path):
        upload_path.unlink(missing_ok=True)
        return jsonify(error="That file is not a valid ZIP archive."), 400

    return jsonify(id=upload_id, filename=Path(uploaded_file.filename).name)

app.layout = html.Div(
    [
        html.Header(
            [
                html.A(
                    [html.Span("DP", className="brand-mark"), html.Span("Dash Projects")],
                    href="/",
                    className="brand",
                ),
                html.Span("LOCAL WORKSPACE", className="topbar-note"),
            ],
            className="topbar",
        ),
        page_container,
        html.Footer("Private by default. Data stays on this machine.", className="site-footer"),
    ],
    className="app-shell",
)


if __name__ == "__main__":
    app.run(debug=True)