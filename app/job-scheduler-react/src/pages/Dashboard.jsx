import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { fetchJobs, deleteJob } from "../api/jobService";
import Sidebar from "../components/Sidebar";
import JobCard from "../components/JobCard";
import JobDetailsModal from "../components/JobDetailsModal";

const Dashboard = () => {
  const [jobs, setJobs] = useState([]);
  const [selectedJob, setSelectedJob] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      navigate("/login"); // Redirect to login if no token is found
      return;
    }

    const loadJobs = async () => {
      try {
        const data = await fetchJobs();
        console.log("Jobs fetched:", data);
        setJobs(data);
      } catch (error) {
        console.error("Error loading jobs:", error);
        navigate("/login"); // Redirect to login if unauthorized
      }
    };
    loadJobs();
  }, [navigate]);

  const handleDeleteJob = (jobId) => {
    setJobs((prevJobs) => prevJobs.filter((job) => job.id !== jobId));
  };

  return (
    <div className="dashboard">
      <Sidebar />
      <div className="job-grid">
        {jobs.map((job) => (
          <JobCard
            key={job.id}
            job={job}
            onClick={() => setSelectedJob(job)}
            onDelete={handleDeleteJob}
          />
        ))}
      </div>
      {selectedJob && (
        <JobDetailsModal
          job={selectedJob}
          onClose={() => setSelectedJob(null)}
        />
      )}
    </div>
  );
};

export default Dashboard; 