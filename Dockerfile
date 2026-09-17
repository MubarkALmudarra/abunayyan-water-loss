# On-premise deployment image.
# Build once, run as an internal service on the company's own server —
# no outbound internet access is required at runtime.
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Regenerate/refresh the demo dataset at build time.
# In production, replace generate_data.py's output with a real export
# from the company's meter data historian (CSV/DB) — analysis.py and
# dashboard.py do not need to change.
RUN python generate_data.py

EXPOSE 8501
CMD ["streamlit", "run", "dashboard.py", "--server.address=0.0.0.0", "--server.port=8501"]
