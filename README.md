# Payment Example API

A minimal FastAPI project.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
fastapi dev app/main.py
```

Interactive docs: http://127.0.0.1:8000/docs

## Endpoints

| Method | Path              | Description           |
|--------|-------------------|-----------------------|
| GET    | `/health`         | Health check          |
| GET    | `/items`          | List all items        |
| GET    | `/items/{id}`     | Get one item          |
| POST   | `/items`          | Create an item        |
| POST   | `/example`        | Echo posted data      |

## Test

```bash
pytest
```
