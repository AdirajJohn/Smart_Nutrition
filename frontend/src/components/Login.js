// src/components/Login.js

import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { loginWithGoogle, extractTokenFromUrl } from "../utils/auth";

const Login = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const token = extractTokenFromUrl();
    if (token) {
      console.log("Logged in with token:", token);
      navigate("/app");
    }
  }, [navigate]);

  return (
    <div style={{ padding: "2rem" }}>
      <h2>Welcome to Smart Nutrition</h2>
      <button onClick={loginWithGoogle}>Login with Google</button>
    </div>
  );
};

export default Login;
