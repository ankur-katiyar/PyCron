import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import Sidebar from "../components/Sidebar";

const CreateJob = () => {
  const [jobName, setJobName] = useState("");
  const [schedule, setSchedule] = useState("");
  const [command, setCommand] = useState("");
  const [dependencies, setDependencies] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Convert dependencies from comma-separated string to array of integers
    const dependenciesArray = dependencies
      .split(",")
      .map((id) => parseInt(id.trim()))
      .filter((id) => !isNaN(id));

    try {
      const token = localStorage.getItem("token");
      const response = await axios.post(
        "http://localhost:8000/jobs",
        {
          name: jobName,
          schedule: schedule,
          command: command,
          dependencies: dependenciesArray,
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      console.log("Job created:", response.data);
      navigate("/"); // Redirect to the dashboard after successful creation
    } catch (error) {
      if (error.response) {
        console.log("Server response data:", error.response.data);
        setError("Failed to create job. Please try again.");
      } else {
        setError("Network error. Please check your connection.");
      }
      console.error("Create job error:", error);
    }
  };

  return (
    <div className="dashboard">
      <Sidebar />
      <div className="create-job-container">
        <h1>Create Job</h1>
        {error && <p className="error">{error}</p>}
        <form onSubmit={handleSubmit}>
          <div>
            <label>Job Name:</label>
            <input
              type="text"
              placeholder="Enter job name"
              value={jobName}
              onChange={(e) => setJobName(e.target.value)}
              required
            />
          </div>
          <div>
            <label>Schedule:</label>
            <input
              type="text"
              placeholder="Enter cron schedule"
              value={schedule}
              onChange={(e) => setSchedule(e.target.value)}
              required
            />
          </div>
          <div>
            <label>Command:</label>
            <input
              type="text"
              placeholder="Enter command"
              value={command}
              onChange={(e) => setCommand(e.target.value)}
              required
            />
          </div>
          <div>
            <label>Dependencies:</label>
            <input
              type="text"
              placeholder="Enter job IDs (comma-separated)"
              value={dependencies}
              onChange={(e) => setDependencies(e.target.value)}
            />
          </div>
          <button type="submit">Create Job</button>
        </form>
      </div>
    </div>
  );
};

export default CreateJob; 