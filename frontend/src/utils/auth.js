// src/utils/auth.js

export function loginWithGoogle() {
    // Redirect to FastAPI backend for OAuth
    window.location.href = "http://localhost:8000/auth/login";
  }
  
  export function extractTokenFromUrl() {
    const params = new URLSearchParams(window.location.search);
    const token = params.get("token");
    if (token) {
      localStorage.setItem("access_token", token);
    }
    return token;
  }
  
  export function getAccessToken() {
    return localStorage.getItem("access_token");
  }
  