from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import os

app = FastAPI(title="KemProMed API & Hub")

@app.get("/", response_class=HTMLResponse)
def read_root():
    # Lee el archivo index.html
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>KemProMed Backend Online</h1>"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)
