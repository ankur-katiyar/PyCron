import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { fetchJobs, deleteJob } from "../api/jobService";
import Sidebar from "../components/Sidebar";
import JobCard from "../components/JobCard";
import JobDetailsModal from "../components/JobDetailsModal";
import { toast } from "react-hot-toast";

const Dashboard = () => {
  const [jobs, setJobs] = useState([]);
  const [filteredJobs, setFilteredJobs] = useState([]);
  const [selectedJob, setSelectedJob] = useState(null);
  const [filters, setFilters] = useState({
    status: "",
    name: "",
    dependency: "",
  });
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
        setFilteredJobs(data); // Initialize filtered jobs
      } catch (error) {
        console.error("Error loading jobs:", error);
        navigate("/login"); // Redirect to login if unauthorized
      }
    };
    loadJobs();
  }, [navigate]);

  const handleDeleteJob = (jobId) => {
    setJobs((prevJobs) => prevJobs.filter((job) => job.id !== jobId));
    setFilteredJobs((prevJobs) => prevJobs.filter((job) => job.id !== jobId));
  };

  const fetchJobsData = async () => {
    try {
      const jobs = await fetchJobs();
      setJobs(jobs); // Only update the jobs state
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

  // Apply filters whenever filters change
  useEffect(() => {
    const filtered = jobs.filter((job) => {
      const matchesStatus = filters.status ? job.status === filters.status : true;
      const matchesName = filters.name
        ? job.name.toLowerCase().includes(filters.name.toLowerCase())
        : true;
      const matchesDependency = filters.dependency
        ? job.dependencies.includes(parseInt(filters.dependency))
        : true;
      return matchesStatus && matchesName && matchesDependency;
    });
    setFilteredJobs(filtered);
  }, [filters, jobs]); // Reapply filters when filters or jobs change

  return (
    <div className="dashboard">
      <Sidebar />
      <div className="job-grid-container">
        <div className="filter-bar">
          <input
            type="text"
            placeholder="Search by job name"
            value={filters.name}
            onChange={(e) => setFilters({ ...filters, name: e.target.value })}
          />
          <select
            value={filters.status}
            onChange={(e) => setFilters({ ...filters, status: e.target.value })}
          >
            <option value="">All Statuses</option>
            <option value="scheduled">Scheduled</option>
            <option value="inactive">Inactive</option>
            <option value="complete">Complete</option>
            <option value="failed">Failed</option>
            <option value="running">Running</option>
          </select>
          <input
            type="text"
            placeholder="Filter by dependency ID"
            value={filters.dependency}
            onChange={(e) => setFilters({ ...filters, dependency: e.target.value })}
          />
        </div>
        <div className="job-grid">
          {filteredJobs.map((job) => (
            <JobCard
              key={job.id}
              job={job}
              onClick={() => setSelectedJob(job)}
              onDelete={handleDeleteJob}
              onStatusUpdate={fetchJobsData}
            />
          ))}
        </div>
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