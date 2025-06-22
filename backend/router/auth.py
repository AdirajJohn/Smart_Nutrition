from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, RedirectResponse
import httpx, os
from urllib.parse import urlencode
from dotenv import load_dotenv
load_dotenv()
router = APIRouter(prefix="/auth", tags=["auth"])

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
FRONTEND_URL = 'http://localhost:3000/app'

@router.get("/login")
async def login():
    params = {
        'client_id':GOOGLE_CLIENT_ID,
        'redirect_uri':REDIRECT_URI,
        'response_type': 'code',
        'scope': "openid email profile",
        'access_type':'offline',
        'prompt':'consent'
    }
    url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    return RedirectResponse(url)

# Step 2: Handle callback
@router.get("/callback")
async def callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        return JSONResponse(content={"error": "Missing code"}, status_code=400)
    
    #Exchange code for token
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    async with httpx.AsyncClient() as client:
        token_res = await client.post(token_url,data = token_data,headers=headers,timeout=20)
        token_json = token_res.json()

    access_token = token_json.get('access_token')
    if not access_token:
        return JSONResponse(content={"error": "Token exchange failed", "details": token_json}, status_code=400)
    

    #Fetch userinfo
    async with httpx.AsyncClient() as client:
        userinfo_res = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        userinfo = userinfo_res.json()
    return RedirectResponse(FRONTEND_URL)