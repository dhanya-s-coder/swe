# Factory Adjuster Simulation

Corrected discrete-event simulation: running machines fail with a positive Gaussian pseudo-random interval around the selected MTTF, failed machines wait for compatible adjusters, and repaired machines receive a new failure clock. The timeline is virtual simulation time; it is separate from wall-clock execution time, so a day or month of simulated time can normally run in seconds. Backend is FastAPI, persistence is MongoDB, and the UI is Streamlit.

## Features

- Gaussian machine failure times around each category MTTF
- Fixed repair time per machine category
- Skill-based FIFO dispatching with least-skilled compatible adjuster selection
- Add/remove machine groups and adjusters from the Streamlit UI
- Batch creation of machines, for example 200 lathe machines at once
- Per-category and per-machine efficiency metrics
- MongoDB persistence through the FastAPI backend

## Requirements

- Python 3.11 or newer
- A MongoDB database (local MongoDB or MongoDB Atlas)

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and set:

```text
MONGODB_URI=your-mongodb-connection-string
MONGODB_DATABASE=factory_simulation
API_URL=http://localhost:8000
```

Start the backend in one terminal:

```powershell
uvicorn app.api:app --reload --host 127.0.0.1 --port 8000
```

Start the dashboard in a second terminal:

```powershell
streamlit run streamlit_app.py
```

Open the Streamlit URL shown in the terminal, usually `http://localhost:8501`.

## How to use

1. Add one or more machine groups. Each group has a category, count, MTTF in seconds, and fixed repair time in seconds.
2. Add adjusters and select one or more skills for each adjuster.
3. Set the virtual simulation timeline. This is simulated factory time, not a delay; the program should finish quickly.
4. Click **Run simulation**.
5. Review overall utilization, category results, machine efficiency, failures, and waiting machines.

The simulator uses a positive Gaussian failure interval around each MTTF. Waiting and repair count as machine downtime. When several idle adjusters can repair a failed category, the compatible adjuster with the fewest skills is selected first.

## API smoke test

With the backend running:

```powershell
Invoke-RestMethod http://localhost:8000/health
```

The expected response is:

```json
{"status":"ok"}
```

## Security

Keep MongoDB credentials in `.env` or another secret manager. Do not commit `.env`, `atlas-credentials.env`, passwords, or connection strings.
streamlit run streamlit_app.py
```
Set `MONGODB_URI` and `MONGODB_DATABASE` in `.env`. Never commit credentials.
