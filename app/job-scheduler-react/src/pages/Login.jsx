import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

const Login = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();

    // Basic validation
    if (!username.trim() || !password.trim()) {
      setError("Please enter both username and password");
      return;
    }

    const params = new URLSearchParams();
    params.append('username', username.trim());
    params.append('password', password.trim());

    try {
      const response = await axios.post("http://localhost:8000/api/login", params, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });

      // Store the token in local storage
      localStorage.setItem("token", response.data.access_token);
      console.log("Token stored:", response.data.access_token);
      navigate("/"); // Redirect to the dashboard after successful login
    } catch (error) {
      if (error.response) {
        console.log("Server response data:", error.response.data);
        setError("Login failed. Please try again.");
      } else {
        setError("Network error. Please check your connection.");
      }
      console.error("Login error:", error);
    }
  };

  return (
    <div className="login-container">
      <h2>Login</h2>
      {error && <p className="error">{error}</p>}
      <form onSubmit={handleLogin}>
        <div>
          <label>Username:</label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>
        <div>
          <label>Password:</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <button type="submit">Login</button>
      </form>
    </div>
  );
};

export default Login; 