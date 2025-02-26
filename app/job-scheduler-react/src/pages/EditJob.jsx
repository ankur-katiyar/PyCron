import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";
import Sidebar from "../components/Sidebar";
import { toast } from "react-hot-toast";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faTimes } from "@fortawesome/free-solid-svg-icons";

const EditJob = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: "",
    command: "",
    schedule: "",
    dependencies: [],
  });
  const [availableJobs, setAvailableJobs] = useState([]);
  const [error, setError] = useState("");
  const [dependencySearch, setDependencySearch] = useState("");
  const [filteredJobs, setFilteredJobs] = useState([]);
  const [selectedDependency, setSelectedDependency] = useState(null);

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
        setFormData({
          name: job.name,
          command: job.command,
          schedule: typeof job.schedule === "object" ? JSON.stringify(job.schedule) : job.schedule,
          dependencies: job.dependencies || [],
        });
      } catch (error) {
        console.error("Error fetching job:", error);
        setError("Failed to fetch job details.");
      }
    };

    const fetchJobs = async () => {
      try {
        const token = localStorage.getItem("token");
        const response = await axios.get("http://localhost:8000/jobs", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        // Filter out the current job from available dependencies
        setAvailableJobs(response.data.filter(job => job.id !== parseInt(id)));
      } catch (error) {
        console.error("Error fetching jobs:", error);
        setError("Failed to fetch available jobs for dependencies.");
      }
    };

    fetchJob();
    fetchJobs();
  }, [id]);

  // Filter jobs based on search input
  useEffect(() => {
    if (dependencySearch.trim() === "") {
      setFilteredJobs([]);
      return;
    }

    const searchLower = dependencySearch.toLowerCase();
    const filtered = availableJobs.filter(
      (job) => 
        job.name.toLowerCase().includes(searchLower) && 
        !formData.dependencies.includes(job.id)
    );
    setFilteredJobs(filtered);
  }, [dependencySearch, availableJobs, formData.dependencies]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleDependencySearchChange = (e) => {
    setDependencySearch(e.target.value);
    setSelectedDependency(null);
  };

  const handleSelectDependency = (job) => {
    setSelectedDependency(job);
    setDependencySearch(job.name);
    setFilteredJobs([]);
  };

  const handleAddDependency = () => {
    if (selectedDependency && !formData.dependencies.includes(selectedDependency.id)) {
      setFormData({
        ...formData,
        dependencies: [...formData.dependencies, selectedDependency.id],
      });
      setDependencySearch("");
      setSelectedDependency(null);
    }
  };

  const handleRemoveDependency = (id) => {
    setFormData({
      ...formData,
      dependencies: formData.dependencies.filter((depId) => depId !== id),
    });
  };

  const getDependencyName = (id) => {
    const job = availableJobs.find((job) => job.id === id);
    return job ? job.name : `Unknown Job (ID: ${id})`;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem("token");
      const response = await axios.put(
        `http://localhost:8000/jobs/${id}`,
        formData,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );
      toast.success("Job updated successfully!");
      navigate("/dashboard");
    } catch (error) {
      console.error("Error updating job:", error);
      setError("Failed to update job. Please check your inputs and try again.");
      toast.error("Failed to update job.");
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
            <label htmlFor="name">Job Name:</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
            />
          </div>
          <div>
            <label htmlFor="command">Command:</label>
            <input
              type="text"
              id="command"
              name="command"
              value={formData.command}
              onChange={handleChange}
              required
            />
          </div>
          <div>
            <label htmlFor="schedule">Schedule:</label>
            <input
              type="text"
              id="schedule"
              name="schedule"
              value={formData.schedule}
              onChange={handleChange}
              required
              placeholder="cron expression or JSON object"
            />
          </div>
          <div>
            <label htmlFor="dependency-search">Dependencies:</label>
            <div className="dependency-search-container">
              <input
                type="text"
                id="dependency-search"
                placeholder="Search for jobs by name"
                value={dependencySearch}
                onChange={handleDependencySearchChange}
              />
              <button 
                type="button" 
                className="add-dependency-button"
                onClick={handleAddDependency}
                disabled={!selectedDependency}
              >
                Add
              </button>
            </div>
            {filteredJobs.length > 0 && (
              <div className="dependency-dropdown">
                {filteredJobs.map((job) => (
                  <div 
                    key={job.id} 
                    className="dependency-option"
                    onClick={() => handleSelectDependency(job)}
                  >
                    {job.name} (ID: {job.id})
                  </div>
                ))}
              </div>
            )}
            <div className="selected-dependencies">
              {formData.dependencies.map((id) => (
                <div key={id} className="dependency-tag">
                  <span>{getDependencyName(id)}</span>
                  <button 
                    type="button"
                    className="remove-dependency-button"
                    onClick={() => handleRemoveDependency(id)}
                  >
                    <FontAwesomeIcon icon={faTimes} />
                  </button>
                </div>
              ))}
            </div>
          </div>
          <button type="submit">Update Job</button>
        </form>
      </div>
    </div>
  );
};

export default EditJob; 