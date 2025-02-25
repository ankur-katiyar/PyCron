import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { fetchJobs, deleteJob } from "../api/jobService";
import Sidebar from "../components/Sidebar";
import JobCard from "../components/JobCard";
import JobDetailsModal from "../components/JobDetailsModal";
import { toast } from "react-hot-toast";

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

  const fetchJobsData = async () => {
    try {
      const jobs = await fetchJobs();
      setJobs(jobs);
    } catch (error) {
      console.error("Error fetching jobs:", error);
      toast.error("Failed to fetch jobs.");
    }
  };

  useEffect(() => {
    fetchJobsData(); // Initial fetch

    const interval = setInterval(() => {
      fetchJobsData(); // Periodic fetch
    }, localStorage.getItem("refreshInterval") * 1000 || 10000); // Default to 10 seconds

    return () => clearInterval(interval); // Cleanup on unmount
  }, []);

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