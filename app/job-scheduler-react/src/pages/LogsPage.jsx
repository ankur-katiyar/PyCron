import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";
import Sidebar from "../components/Sidebar";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faTrash, faArrowLeft, faSync } from "@fortawesome/free-solid-svg-icons";
import { toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

const LogsPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [logs, setLogs] = useState([]);
  const [error, setError] = useState("");
  const [jobName, setJobName] = useState("");

  useEffect(() => {
    fetchLogs();
    fetchJobDetails();
  }, [id]);

  const fetchLogs = async () => {
    try {
      const token = localStorage.getItem("token");
      const response = await axios.get(`http://localhost:8000/jobs/${id}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      setLogs(response.data.logs || []);
    } catch (error) {
      console.error("Error fetching logs:", error);
      setError("Failed to fetch logs.");
    }
  };

  const fetchJobDetails = async () => {
    try {
      const token = localStorage.getItem("token");
      const response = await axios.get(`http://localhost:8000/jobs/${id}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      setJobName(response.data.name);
    } catch (error) {
      console.error("Error fetching job details:", error);
      setError("Failed to fetch job details.");
    }
  };

  const handlePurgeLogs = async () => {
    try {
      const token = localStorage.getItem("token");
      const response = await axios.post(
        `http://localhost:8000/jobs/${id}/purge_logs`,
        {},
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      toast.success(response.data.message);
      fetchLogs();
    } catch (error) {
      console.error("Error purging logs:", error);
      toast.error(error.response?.data?.message || "Failed to purge logs.");
    }
  };

  return (
    <div className="dashboard">
      <Sidebar />
      <div className="logs-container">
        <div className="logs-header">
          <button className="back-button" onClick={() => navigate(-1)}>
            <FontAwesomeIcon icon={faArrowLeft} /> Back
          </button>
          <h1>Job Logs {jobName}(id={id})</h1>
          <div className="logs-actions">
            <button className="refresh-button" onClick={fetchLogs}>
              <FontAwesomeIcon icon={faSync} /> Refresh
            </button>
            <button className="purge-button" onClick={handlePurgeLogs}>
              <FontAwesomeIcon icon={faTrash} /> Purge Logs
            </button>
          </div>
        </div>
        {error && <p className="error">{error}</p>}
        <div className="terminal">
          {logs.map((log, index) => (
            <div key={index} className="log-entry">
              <div className="log-timestamp">
                {log.timestamp && new Date(log.timestamp).toLocaleString()}
              </div>
              <div className="log-stdout">
                <pre>{log.stdout}</pre>
              </div>
              <div className="log-stderr">
                <pre>{log.stderr}</pre>
              </div>
              <div className="log-execution-time">
                Execution Time: {log.execution_time} seconds
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default LogsPage; 