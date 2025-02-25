import React, { useState, useEffect } from "react";
import Sidebar from "../components/Sidebar";
import { toast } from "react-hot-toast";

const SettingsPage = () => {
  const [refreshInterval, setRefreshInterval] = useState(
    localStorage.getItem("refreshInterval") || 10
  );

  const handleSave = () => {
    localStorage.setItem("refreshInterval", refreshInterval);
    toast.success("Settings saved successfully.");
  };

  return (
    <div className="dashboard">
      <Sidebar />
      <div className="settings-container">
        <h1>Settings</h1>
        <div className="setting">
          <label>Dashboard Refresh Interval (seconds):</label>
          <input
            type="number"
            value={refreshInterval}
            onChange={(e) => setRefreshInterval(e.target.value)}
            min="1"
          />
        </div>
        <button className="save-button" onClick={handleSave}>
          Save
        </button>
      </div>
    </div>
  );
};

export default SettingsPage; 