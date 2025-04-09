from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from colorthief import ColorThief
import httpx
import re
import os
from urllib.parse import urlparse  # for parsing url

app = FastAPI()

# configure cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins for simplicity, restrict in production
    allow_credentials=True,
    allow_methods=["*"],  # allow all methods
    allow_headers=["*"],  # allow all headers
)

# define a user-agent
USER_AGENT = "Mozilla/5.0 (compatible; BookmarkAppBot/1.0)"

@app.get("/api/fetch-title")
async def fetch_title(url: str = Query(..., description="the url to fetch the title from")):
    if not url:
        raise HTTPException(status_code=400, detail="url parameter is required")

    if not url.startswith("http://") and not url.startswith("https://"):
        url = f"https://{url}"

    try:
        async with httpx.AsyncClient(headers={"User-Agent": USER_AGENT}, follow_redirects=True, timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()  # raise exception for bad status codes

            # extract title using regex (case-insensitive)
            title_match = re.search(r'<title[^>]*>(.*?)</title>', response.text, re.IGNORECASE | re.DOTALL)
            title = title_match.group(1).strip() if title_match else ""

            # fetch favicon from scheme://netloc/favicon.ico
            parsed_url = urlparse(url)
            favicon_url = f"{parsed_url.scheme}://{parsed_url.netloc}/favicon.ico"
            try:
                favicon_response = await client.get(favicon_url)
                if favicon_response.status_code == 200:
                    favicon_img = favicon_response.content
                    if favicon_img is not None:
                      with open("favicon.ico", "wb") as f:
                        f.write(favicon_img)
                    ct = ColorThief("favicon.ico")
                    dominant_color = ct.get_color(quality=1)
                    os.remove("favicon.ico")
                else:
                    favicon_img = None
                    dominant_color = None
            except Exception as favicon_error:
                favicon_img = None
                dominant_color = None


        return JSONResponse(content={"title": title, "faviconColor": dominant_color})
    except httpx.RequestError as exc:
        print(f"an error occurred while requesting {exc.request.url!r}: {exc}")
        raise HTTPException(status_code=500, detail=f"failed to fetch url: network error - {type(exc).__name__}")
    except httpx.HTTPStatusError as exc:
        print(f"error response {exc.response.status_code} while requesting {exc.request.url!r}.")
        raise HTTPException(status_code=500, detail=f"failed to fetch url: received status {exc.response.status_code}")
    except Exception as e:
        print(f"an unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"an internal server error occurred: {type(e).__name__}")

# root endpoint for testing deployment
@app.get("/api")
async def read_root():
    return {"message": "title fetcher api is running"}
