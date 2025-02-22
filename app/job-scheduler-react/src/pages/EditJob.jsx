import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import axios from "axios";
import Sidebar from "../components/Sidebar";

const EditJob = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [jobName, setJobName] = useState("");
  const [schedule, setSchedule] = useState("");
  const [command, setCommand] = useState("");
  const [dependencies, setDependencies] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchJob = async () => {
      try {
        const token = localStorage.getItem("token");
        const response = await axios.get(`http://localhost:8000/jobs/${id}`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        const job = response.data;
        setJobName(job.name);
        setSchedule(job.schedule);
        setCommand(job.command);

        // Handle dependencies (convert JSON string to array if necessary)
        const dependenciesArray = typeof job.dependencies === "string" 
          ? JSON.parse(job.dependencies) 
          : job.dependencies;
        setDependencies(dependenciesArray.join(","));
      } catch (error) {
        console.error("Error fetching job:", error);
        setError("Failed to fetch job details.");
      }
    };
    fetchJob();
  }, [id]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Convert dependencies from comma-separated string to array of integers
    const dependenciesArray = dependencies
      .split(",")
      .map((id) => parseInt(id.trim()))
      .filter((id) => !isNaN(id));

    try {
      const token = localStorage.getItem("token");
      const response = await axios.put(
        `http://localhost:8000/jobs/${id}`,
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

      console.log("Job updated:", response.data);
      navigate("/"); // Redirect to the dashboard after successful update
    } catch (error) {
      if (error.response) {
        console.log("Server response data:", error.response.data);
        setError("Failed to update job. Please try again.");
      } else {
        setError("Network error. Please check your connection.");
      }
      console.error("Update job error:", error);
    }
  };

  return (
    <div className="dashboard">
      <Sidebar />
      <div className="create-job-container">
        <h1>Edit Job</h1>
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
          <button type="submit">Update Job</button>
        </form>
      </div>
    </div>
  );
};

export default EditJob; 