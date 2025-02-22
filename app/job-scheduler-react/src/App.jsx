import React, { useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Login from "./pages/Login";
import CreateJob from "./pages/CreateJob";
import EditJob from "./pages/EditJob";
import Settings from "./pages/Settings";
import "./styles/global.css";
import "./styles/theme.css";

function App() {
  const isAuthenticated = () => {
    const token = localStorage.getItem("token");
    return !!token; // Return true if token exists, false otherwise
  };

  return (
    <Router>
      <Routes>
        <Route
          path="/"
          element={isAuthenticated() ? <Dashboard /> : <Navigate to="/login" />}
        />
        <Route path="/login" element={<Login />} />
        <Route
          path="/create-job"
          element={isAuthenticated() ? <CreateJob /> : <Navigate to="/login" />}
        />
        <Route
          path="/edit-job/:id"
          element={isAuthenticated() ? <EditJob /> : <Navigate to="/login" />}
        />
        <Route
          path="/settings"
          element={isAuthenticated() ? <Settings /> : <Navigate to="/login" />}
        />
      </Routes>
    </Router>
  );
}

export default App; 