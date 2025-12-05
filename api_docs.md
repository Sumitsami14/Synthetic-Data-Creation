# API Documentation

Base URL: `http://localhost:5000`

## Endpoints

### 1. Trigger Generation
**POST** `/api/generate`

Triggers a background job to generate synthetic data.

**Request Body** (JSON):
```json
{
    "customers": 100,
    "format": "csv"
}
```
- `customers`: (int) Number of customers to generate.
- `format`: (str) "csv" or "json".

**Response** (202 Accepted):
```json
{
    "message": "Generation started",
    "job_id": 1
}
```

### 2. Get Request History
**GET** `/api/history`

Returns a list of all generation requests and their status.

**Response** (200 OK):
```json
[
    {
        "id": 1,
        "timestamp": "2023-10-27T10:00:00.000000",
        "customers_count": 100,
        "status": "Completed",
        "file_path": "data/exports/..."
    },
    ...
]
```

### 3. Download Data
**GET** `/api/download/<job_id>`

Downloads the generated zip file for a specific job.

**Response**:
-   `200 OK`: File stream (application/zip).
-   `404 Not Found`: If file is not ready or doesn't exist.
