import uvicorn
from bug_triage_env.server.app import app

def start():
    uvicorn.run("server.app:app", host="0.0.0.0", port=8000)

if __name__ == "__main__":
    start()
