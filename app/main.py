from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from app.converter import csv_to_json
import pandas as pd
import os
import io
import json

app = FastAPI()
TEMP_JSON_PATH = "output.json"

@app.get("/", response_class=HTMLResponse)
def root_page():
    return """
    <html>
        <head>
            <title>CSV to JSON Converter</title>
            <script>
                let uploadedFile = null;

                async function previewCSV(event) {
                    event.preventDefault();
                    const fileInput = document.getElementById("file");
                    const file = fileInput.files[0];
                    if (!file || !file.name.endsWith(".csv")) {
                        alert("Please upload a valid CSV file.");
                        return;
                    }

                    const formData = new FormData();
                    formData.append("file", file);
                    uploadedFile = file;

                    const res = await fetch("/upload-preview", {
                        method: "POST",
                        body: formData
                    });

                    const data = await res.json();
                    if (res.ok) {
                        renderTablePreview(data.preview);
                        document.getElementById("convert-button").style.display = "inline-block";
                    } else {
                        alert(data.error || "Preview failed.");
                    }
                }

                function renderTablePreview(data) {
                    const tableDiv = document.getElementById("preview");
                    if (!data || data.length === 0) {
                        tableDiv.innerHTML = "<p>No data in file.</p>";
                        return;
                    }

                    let table = "<table border='1' style='border-collapse: collapse'><thead><tr>";
                    for (const col of Object.keys(data[0])) {
                        table += `<th>${col}</th>`;
                    }
                    table += "</tr></thead><tbody>";
                    for (const row of data) {
                        table += "<tr>";
                        for (const col of Object.values(row)) {
                            table += `<td>${col}</td>`;
                        }
                        table += "</tr>";
                    }
                    table += "</tbody></table>";
                    tableDiv.innerHTML = table;
                }

                async function convertDefaultCSV() {
                    const logBox = document.getElementById('log');
                    logBox.textContent = "Converting default CSV...";
                    try {
                        const res = await fetch('/convert');
                        const data = await res.json();
                        if (res.ok) {
                            logBox.textContent = JSON.stringify(data.converted_data, null, 2);
                        } else {
                            logBox.textContent = "Error: " + (data.error || "Unknown error");
                        }
                    } catch (e) {
                        logBox.textContent = "Request failed: " + e;
                    }
                }

                async function convertUploadedCSV() {
                    const logBox = document.getElementById('log');
                    logBox.textContent = "Converting uploaded CSV...";
                    const fileInput = document.getElementById("file");
                    const file = fileInput.files[0];
                    if (!file) {
                        logBox.textContent = "No uploaded file.";
                        return;
                    }

                    const formData = new FormData();
                    formData.append("file", file);

                    const res = await fetch("/upload", {
                        method: "POST",
                        body: formData
                    });

                    const data = await res.json();
                    if (res.ok) {
                        logBox.textContent = JSON.stringify(data.rows, null, 2);
                    } else {
                        logBox.textContent = "Error: " + (data.error || "Unknown error");
                    }
                }
            </script>
        </head>
        <body>
            <h2>CSV to JSON Converter</h2>

            <!-- Upload + preview -->
            <form onsubmit="previewCSV(event)">
                <input id="file" name="file" type="file" accept=".csv" required>
                <button type="submit">Preview CSV</button>
            </form>

            <br>

            <!-- Table preview -->
            <div id="preview" style="margin-bottom: 20px;"></div>

            <!-- Convert uploaded file -->
            <button id="convert-button" onclick="convertUploadedCSV()" style="display:none;">Convert Uploaded CSV to JSON</button>

            <br><br>

            <!-- Convert default -->
            <button onclick="convertDefaultCSV()">Convert Default CSV (app/data.csv)</button>

            <br><br>

            <!-- Download -->
            <a href="/download" target="_blank">
                <button>Download Last JSON</button>
            </a>

            <hr>

            <!-- JSON log -->
            <h3>Output JSON</h3>
            <pre id="log" style="background:#f0f0f0; padding:10px; border-radius:5px;"></pre>
        </body>
    </html>
    """

@app.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        return JSONResponse(content={"error": "Only CSV files are allowed"}, status_code=400)

    contents = await file.read()
    df = pd.read_csv(io.StringIO(contents.decode("utf-8")))

    df.to_json(TEMP_JSON_PATH, orient="records", indent=2)
    return JSONResponse(content={"message": "CSV converted to JSON!", "rows": df.to_dict(orient="records")})

@app.post("/upload-preview")
async def preview_csv(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        return JSONResponse(content={"error": "Only CSV files allowed"}, status_code=400)

    contents = await file.read()
    df = pd.read_csv(io.StringIO(contents.decode("utf-8")))
    preview = df.head(10).to_dict(orient="records")  # Show top 10 rows only
    return JSONResponse(content={"preview": preview})

@app.get("/convert")
def convert_csv_to_json():
    try:
        json_data = csv_to_json("app/data.csv")
        with open(TEMP_JSON_PATH, "w") as f:
            json.dump(json_data, f, indent=2)
        return JSONResponse(content={"message": "Converted", "converted_data": json_data})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/download")
def download_json():
    if os.path.exists(TEMP_JSON_PATH):
        return FileResponse(TEMP_JSON_PATH, media_type='application/json', filename="converted.json")
    else:
        return JSONResponse(content={"error": "No JSON file found. Upload a CSV first."}, status_code=404)