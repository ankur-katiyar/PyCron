import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { deleteJob, getJobs, runJobAdhoc, updateJobStatus } from "../api/jobService";
import { useNavigate } from "react-router-dom";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faEdit, faTrash, faArrowRight, faPlay, faFileAlt } from "@fortawesome/free-solid-svg-icons";
import { toast } from "react-hot-toast";
import ConfirmationModal from "./ConfirmationModal";

const JobCard = ({ job, onClick, onDelete }) => {
  const navigate = useNavigate();
  const [dependencyNames, setDependencyNames] = useState([]);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [selectedStatus, setSelectedStatus] = useState(job.status);

  // Convert schedule to a string if it's an object
  const schedule = typeof job.schedule === "object" ? JSON.stringify(job.schedule) : job.schedule;

  // Sync selectedStatus with job.status
  useEffect(() => {
    setSelectedStatus(job.status);
  }, [job.status]);

  // Fetch job names for dependencies
  useEffect(() => {
    const fetchDependencyNames = async () => {
      if (job.dependencies && job.dependencies.length > 0) {
        try {
          const token = localStorage.getItem("token");
          const response = await getJobs(token);
          const jobs = response.data;

          // Map dependency IDs to job names
          const names = job.dependencies.map((id) => {
            const dependentJob = jobs.find((j) => j.id === id);
            return dependentJob ? dependentJob.name : `Unknown Job (ID: ${id})`;
          });

          setDependencyNames(names);
        } catch (error) {
          console.error("Error fetching dependency names:", error);
        }
      }
    };

    fetchDependencyNames();
  }, [job.dependencies]);

  const handleDelete = async () => {
    try {
      await deleteJob(job.id);
      onDelete(job.id); // Notify the parent component to remove the job from the list
      toast.success("Job deleted successfully.");
    } catch (error) {
      console.error("Error deleting job:", error);
      toast.error("Failed to delete job.");
    } finally {
      setShowDeleteModal(false); // Close the modal
    }
  };

  const handleEdit = (e) => {
    e.stopPropagation(); // Prevent the card's onClick from firing
    navigate(`/edit-job/${job.id}`); // Navigate to the edit job page
  };

  const handleRunAdhoc = async (e) => {
    e.stopPropagation(); // Prevent the card's onClick from firing
    try {
      const token = localStorage.getItem("token");
      const response = await runJobAdhoc(job.id, token);
      toast.success(response.message); // Display the API response message
    } catch (error) {
      console.error("Error running job ad-hoc:", error);
      toast.error(error.response?.data?.message || "Failed to start job."); // Display the error message
    }
  };

  const handleStatusChange = async (e) => {
    e.stopPropagation(); // Prevent the card's onClick from firing
    const newStatus = e.target.value;
    try {
      const token = localStorage.getItem("token");
      const response = await updateJobStatus(job.id, newStatus, token);
      toast.success(response.message); // Display the API response message
      setSelectedStatus(newStatus); // Update the selected status
    } catch (error) {
      console.error("Error updating job status:", error);
      toast.error(error.response?.data?.message || "Failed to update job status."); // Display the error message
    }
  };

  const handleViewLogs = (e) => {
    e.stopPropagation(); // Prevent the card's onClick from firing
    navigate(`/logs/${job.id}`); // Navigate to the logs page
  };

  // Get the color for the job card based on the status
  const getJobCardColor = (status) => {
    switch (status) {
      case "running":
        return "#2e7d32"; // Darker green for running
      default:
        return "#2d2d2d"; // Default color for other statuses
    }
  };

  // Get the color for the status dropdown
  const getStatusColor = (status) => {
    switch (status) {
      case "scheduled":
        return "#ff9800"; // Amber for scheduled
      case "inactive":
        return "#b0b0b0"; // Grey for inactive
      case "complete":
        return "#2196f3"; // Blue for complete
      default:
        return "#ffffff"; // White for other statuses
    }
  };

  return (
    <motion.div
      className="job-card"
      style={{ backgroundColor: getJobCardColor(job.status) }} // Apply job card color
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
    >
      <div className="job-header">
        <h3>
          {job.name} (id={job.id})
        </h3>
        <div className="job-actions">
          <button className="icon-button" onClick={handleRunAdhoc}>
            <FontAwesomeIcon icon={faPlay} />
          </button>
          <button className="icon-button" onClick={handleEdit}>
            <FontAwesomeIcon icon={faEdit} />
          </button>
          <button className="icon-button" onClick={handleViewLogs}>
            <FontAwesomeIcon icon={faFileAlt} />
          </button>
          <button
            className="icon-button"
            onClick={(e) => {
              e.stopPropagation();
              setShowDeleteModal(true); // Show the delete confirmation modal
            }}
          >
            <FontAwesomeIcon icon={faTrash} />
          </button>
        </div>
      </div>
      <div className="job-details">
        <div className="job-attribute">
          <span className="job-attribute-title">Schedule:</span>
          <span className="job-attribute-value">{schedule}</span>
        </div>
        <div className="job-attribute">
          <span className="job-attribute-title">Command:</span>
          <span className="job-attribute-value">{job.command}</span>
        </div>
        <div className="job-attribute">
          <span className="job-attribute-title">Status:</span>
          <select
            className="status-select"
            value={selectedStatus}
            onChange={handleStatusChange}
            style={{ backgroundColor: getStatusColor(selectedStatus) }}
          >
            <option value="scheduled">Scheduled</option>
            <option value="inactive">Inactive</option>
            <option value="complete">Complete</option>
          </select>
        </div>
        <div className="job-attribute">
          <span className="job-attribute-title">Last Run:</span>
          <span className="job-attribute-value">
            {job.last_run ? new Date(job.last_run).toLocaleString() : "Never"}
          </span>
        </div>
        <div className="job-attribute">
          <span className="job-attribute-title">Next Run:</span>
          <span className="job-attribute-value">
            {job.next_run ? new Date(job.next_run).toLocaleString() : "N/A"}
          </span>
        </div>
        <div className="job-attribute">
          <span className="job-attribute-title">Run Count:</span>
          <span className="job-attribute-value">{job.run_count}</span>
        </div>
        {job.dependencies && job.dependencies.length > 0 ? (
          <div className="dependency-arrow">
            <FontAwesomeIcon icon={faArrowRight} />
            <span>Depends on: {dependencyNames.join(", ")}</span>
          </div>
        ) : (
          <div className="dependency-arrow">
            <FontAwesomeIcon icon={faArrowRight} />
            <span>Depends on: None</span>
          </div>
        )}
      </div>

      {/* Delete Confirmation Modal */}
      {showDeleteModal && (
        <ConfirmationModal
          message="Are you sure you want to delete this job?"
          onConfirm={handleDelete}
          onCancel={() => setShowDeleteModal(false)}
        />
      )}
    </motion.div>
  );
};

export default JobCard; 