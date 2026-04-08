# 1. Use an official, lightweight Python image
FROM python:3.11-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Install 'uv' (The lightning-fast package manager required by the hackathon's openenv)
RUN pip install uv

# 4. Copy all of your code and dependency files into the container
COPY . .

# 5. Install dependencies
# This clever line checks if the hackathon provided a pyproject.toml (using uv sync) 
# or if you are just using the requirements.txt we made earlier.
RUN if [ -f "pyproject.toml" ]; then uv sync; else uv pip install --system -r requirements.txt; fi

# 6. Expose Port 8000 (Mandatory, exactly as defined in your openenv.yaml)
EXPOSE 8000

# 7. The command to start the official hackathon REST API
CMD ["uv", "run", "uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "8000"]