# FastAPI CSV to JSON Converter

This is a simple FastAPI app that reads data from a CSV file and converts it to JSON format.

## How to Run the App

git clone https://github.com/xdignya776/fastapi-csv-json-converter.git
cd fastapi-csv-json-converter

### Using Docker

1. Build the Docker image:
   ```sh
   docker build -t fastapi-csv-json-converter .
   ```
2. Run the Docker container:
   ```sh
   docker run -p 8000:8000 fastapi-csv-json-converter
   ```
3. Access the API at [http://localhost:8000/](http://localhost:8000/)

### Running Locally (without Docker)

1. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
2. Start the FastAPI app:
   ```sh
   uvicorn app.main:app --reload
   ```
3. Access the API at [http://localhost:8000/](http://localhost:8000/)
