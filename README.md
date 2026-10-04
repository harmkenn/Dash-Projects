# Dash Projects

A local directory for focused data and workflow apps, built with Plotly Dash.

## Run

```powershell
python -m pip install -r requirements.txt
python app.py
```

Open the local URL printed by Dash. The first sub-app, **Google Photos Metadata**, reads a Google Takeout export (drop a ZIP into the app, browse to it, or enter an extracted folder path) and creates CSV and JSON datasets from its metadata sidecars.

## Deploy to Render

Create a Render **Web Service** for this repository, use `pip install -r requirements.txt` as the build command, and set the start command to:

```sh
gunicorn app:server --bind 0.0.0.0:$PORT
```

Gunicorn is included for non-Windows deployments. The `server` WSGI entry point is exposed by `app.py`.

**World Route** lets you choose from an expanded list of major cities and 2–20 total route legs. It selects cities at roughly even longitude intervals, plots the closed route, and lists each stop. The final leg returns to the starting city; estimated distance is calculated from great-circle distances between stops. Click **Print / Save PDF** above the map, then choose **Save as PDF** in your browser's print dialog to save a US Letter portrait PDF with a 6-inch-wide map above a numbered city list in 24-point text.

Google's current Photos APIs do not offer unrestricted bulk listing of an existing library. To build a dataset for an existing collection, request a Google Photos export through [Google Takeout](https://takeout.google.com/), then point the app at an extracted export folder or a Takeout ZIP. The importer reads JSON metadata sidecars and retains each complete sidecar in the output as `raw_metadata_json`.

Exports are written to `generated/` in this project, as well as offered for download in the app. The app runs locally; the source path must be accessible to the Python process.
