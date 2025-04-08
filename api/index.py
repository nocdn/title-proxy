# filepath: api/index.py
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
import re
import os

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for simplicity, restrict in production
    allow_credentials=True,
    allow_methods=["*"], # Allow all methods
    allow_headers=["*"], # Allow all headers
)

# Define a User-Agent
USER_AGENT = "Mozilla/5.0 (compatible; BookmarkAppBot/1.0)"

@app.get("/api/fetch-title") # Vercel routes requests starting with /api to this file
async def fetch_title(url: str = Query(..., description="The URL to fetch the title from")):
    if not url:
        raise HTTPException(status_code=400, detail="URL parameter is required")

    # Ensure URL has a scheme
    if not url.startswith("http://") and not url.startswith("https://"):
        url = f"https://{url}"

    try:
        async with httpx.AsyncClient(headers={"User-Agent": USER_AGENT}, follow_redirects=True, timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # Extract title using regex (case-insensitive)
        # Handles potential attributes within the title tag
        title_match = re.search(r'<title[^>]*>(.*?)</title>', response.text, re.IGNORECASE | re.DOTALL)
        title = title_match.group(1).strip() if title_match else ""

        return JSONResponse(content={"title": title})

    except httpx.RequestError as exc:
        print(f"An error occurred while requesting {exc.request.url!r}: {exc}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch URL: Network error - {type(exc).__name__}")
    except httpx.HTTPStatusError as exc:
        print(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}.")
        raise HTTPException(status_code=500, detail=f"Failed to fetch URL: Received status {exc.response.status_code}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {type(e).__name__}")

# Optional: Add a root endpoint for testing deployment
@app.get("/api")
async def read_root():
    return {"message": "Title fetcher API is running"}
