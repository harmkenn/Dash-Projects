import csv
import json
import uuid
import zipfile
from pathlib import Path

from dash import Input, Output, State, callback, ctx, dash_table, dcc, html, no_update, register_page

from google_photos.importer import scan_source


register_page(__name__, path="/apps/google-photos", name="Google Photos Metadata")

EXPORT_DIR = Path(__file__).resolve().parents[1] / "generated"

layout = html.Main(
    [
        html.A("<- All apps", href="/", className="back-link"),
        html.Div(
            [
                html.Div("DATA INTAKE / 01", className="eyebrow"),
                html.H1("Google Photos Metadata"),
                html.P("Turn a Takeout export into a portable, searchable dataset."),
            ],
            className="tool-heading",
        ),
        html.Section(
            [
                html.Label("Drop a Takeout ZIP", className="field-label"),
                html.Div(
                    [
                        html.Div("ZIP", className="dropzone-mark"),
                        html.Div("Drop ZIP here or click to browse", className="dropzone-title"),
                        html.Div("The archive uploads directly to this app and is removed after scanning.", className="dropzone-hint"),
                    ],
                    id="upload-dropzone",
                    className="upload-dropzone",
                    role="button",
                    tabIndex=0,
                    **{"aria-label": "Drop a Google Takeout ZIP or click to browse"},
                ),
                html.Div(id="upload-status", className="upload-status", role="status"),
                dcc.Store(id="uploaded-source"),
                html.Div("OR USE A FOLDER ALREADY ON THIS MACHINE", className="source-divider"),
                html.Label("Takeout folder or ZIP path", htmlFor="source-path", className="field-label"),
                dcc.Input(
                    id="source-path",
                    type="text",
                    placeholder=r"D:\Exports\takeout-20261003.zip",
                    className="path-input",
                    debounce=True,
                ),
                html.Div(
                    [
                        html.Button("Scan metadata", id="scan-button", n_clicks=0, className="primary-button"),
                        html.Span(
                            "For a complete existing library, import a Google Takeout export. The app reads JSON sidecars; media files are not copied.",
                            className="field-hint",
                        ),
                    ],
                    className="scan-controls",
                ),
            ],
            className="source-panel",
        ),
        html.Div(id="scan-status", className="status-line", role="status"),
        html.Section(
            [
                html.Div(
                    [
                        html.Div([html.Div("0", id="record-count", className="metric-value"), html.Div("records", className="metric-label")], className="metric"),
                        html.Div([html.Div("0", id="error-count", className="metric-value"), html.Div("sidecars skipped", className="metric-label")], className="metric"),
                    ],
                    className="metrics",
                ),
                html.Div(
                    [
                        html.H2("Dataset preview"),
                        html.Div(
                            [
                                html.Button("CSV", id="download-csv-button", n_clicks=0, className="export-button", disabled=True),
                                html.Button("JSON", id="download-json-button", n_clicks=0, className="export-button", disabled=True),
                            ],
                            className="export-actions",
                        ),
                    ],
                    className="preview-heading",
                ),
                dash_table.DataTable(
                    id="dataset-table",
                    data=[],
                    columns=[],
                    page_size=15,
                    sort_action="native",
                    filter_action="native",
                    fixed_rows={"headers": True},
                    style_table={"overflowX": "auto", "maxHeight": "560px", "overflowY": "auto"},
                    style_cell={
                        "fontFamily": "'IBM Plex Mono', monospace",
                        "fontSize": "12px",
                        "padding": "10px 12px",
                        "maxWidth": "280px",
                        "overflow": "hidden",
                        "textOverflow": "ellipsis",
                        "textAlign": "left",
                        "border": "none",
                        "borderBottom": "1px solid #e7e8e3",
                    },
                    style_header={
                        "fontFamily": "'DM Sans', sans-serif",
                        "fontWeight": "600",
                        "backgroundColor": "#f0f1eb",
                        "color": "#4b5149",
                        "border": "none",
                        "borderBottom": "1px solid #dfe2d9",
                    },
                    style_data={"backgroundColor": "#fff", "color": "#20251f"},
                ),
                html.Div(id="export-location", className="export-location"),
            ],
            className="results-section",
        ),
        dcc.Store(id="export-files"),
        dcc.Download(id="download-file"),
    ],
    className="tool-page page-width",
)


@callback(
    Output("scan-status", "children"),
    Output("scan-status", "className"),
    Output("record-count", "children"),
    Output("error-count", "children"),
    Output("dataset-table", "data"),
    Output("dataset-table", "columns"),
    Output("export-files", "data"),
    Output("download-csv-button", "disabled"),
    Output("download-json-button", "disabled"),
    Output("export-location", "children"),
    Input("scan-button", "n_clicks"),
    Input("uploaded-source", "data"),
    State("source-path", "value"),
    prevent_initial_call=True,
)
def scan_takeout(n_clicks, uploaded_source, source):
    uploaded_path = None
    if ctx.triggered_id == "uploaded-source":
        upload_id = uploaded_source.get("id") if isinstance(uploaded_source, dict) else None
        if not isinstance(upload_id, str):
            return "The ZIP upload could not be found. Please drop it again.", "status-line status-error", "0", "0", [], [], None, True, True, ""
        try:
            parsed_id = uuid.UUID(hex=upload_id)
        except ValueError:
            return "The ZIP upload could not be found. Please drop it again.", "status-line status-error", "0", "0", [], [], None, True, True, ""
        if parsed_id.hex != upload_id:
            return "The ZIP upload could not be found. Please drop it again.", "status-line status-error", "0", "0", [], [], None, True, True, ""
        uploaded_path = Path(__file__).resolve().parents[1] / "generated" / ".uploads" / f"{upload_id}.zip"
        if not uploaded_path.is_file():
            return "The ZIP upload expired. Please drop it again.", "status-line status-error", "0", "0", [], [], None, True, True, ""
        source_path = uploaded_path
    else:
        if not source or not source.strip():
            return "Enter a folder or ZIP path, or drop a ZIP file above.", "status-line status-error", "0", "0", [], [], None, True, True, ""
        source_path = source.strip()

    try:
        result = scan_source(str(source_path))
    except (OSError, ValueError, json.JSONDecodeError, zipfile.BadZipFile) as error:
        return f"Could not scan that source: {error}", "status-line status-error", "0", "0", [], [], None, True, True, ""
    finally:
        if uploaded_path is not None:
            uploaded_path.unlink(missing_ok=True)

    if not result:
        return "Enter a folder or ZIP path to scan.", "status-line status-error", "0", "0", [], [], None, True, True, ""

    records = result["records"]
    if not records:
        message = "No Google Photos metadata sidecars were found. Check that this is a Takeout export folder or ZIP."
        if result["errors"]:
            message += f" {len(result['errors'])} sidecar(s) could not be read."
        return message, "status-line status-error", "0", str(len(result["errors"])), [], [], None, True, True, ""

    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    export_id = uuid.uuid4().hex
    csv_path = EXPORT_DIR / f"google_photos_{export_id}.csv"
    json_path = EXPORT_DIR / f"google_photos_{export_id}.json"
    columns = list(records[0])
    with csv_path.open("w", newline="", encoding="utf-8-sig") as output:
        writer = csv.DictWriter(output, fieldnames=columns)
        writer.writeheader()
        writer.writerows(records)
    json_path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")

    skipped = len(result["errors"])
    message = f"Scanned {len(records):,} metadata sidecar(s)."
    if skipped:
        message += f" {skipped:,} sidecar(s) could not be read; see the skipped count."
    return (
        message,
        "status-line status-success",
        f"{len(records):,}",
        f"{skipped:,}",
        [
            {key: value for key, value in record.items() if key != "raw_metadata_json"}
            for record in records[:100]
        ],
        [{"name": column, "id": column} for column in columns if column != "raw_metadata_json"],
        {"id": export_id},
        False,
        False,
        f"Full datasets also saved under {EXPORT_DIR}",
    )


@callback(
    Output("download-file", "data"),
    Input("download-csv-button", "n_clicks"),
    Input("download-json-button", "n_clicks"),
    State("export-files", "data"),
    prevent_initial_call=True,
)
def download_dataset(csv_clicks, json_clicks, files):
    from dash import ctx, dcc

    if not files:
        return no_update
    export_id = files.get("id", "")
    if not isinstance(export_id, str):
        return no_update
    try:
        parsed_id = uuid.UUID(hex=export_id)
    except (ValueError, AttributeError):
        return no_update
    if parsed_id.hex != export_id:
        return no_update
    kind = "csv" if ctx.triggered_id == "download-csv-button" else "json"
    path = EXPORT_DIR / f"google_photos_{export_id}.{kind}"
    if not path.is_file():
        return no_update
    return dcc.send_file(str(path))