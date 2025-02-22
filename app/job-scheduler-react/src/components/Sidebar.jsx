import React from "react";
import { useNavigate } from "react-router-dom";

const Sidebar = () => {
  const navigate = useNavigate();

  return (
    <div className="sidebar">
      <h2>Job Scheduler</h2>
      <ul>
        <li onClick={() => { console.log("Navigating to /"); navigate("/"); }}>Dashboard</li>
        <li onClick={() => { console.log("Navigating to /create-job"); navigate("/create-job"); }}>Create Job</li>
        <li onClick={() => { console.log("Navigating to /settings"); navigate("/settings"); }}>Settings</li>
      </ul>
    </div>
  );
};

export default Sidebar; 