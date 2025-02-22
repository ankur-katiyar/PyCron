import React from "react";
import { motion } from "framer-motion";
import { deleteJob } from "../api/jobService";
import { useNavigate } from "react-router-dom";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faEdit, faTrash } from "@fortawesome/free-solid-svg-icons";

const JobCard = ({ job, onClick, onDelete }) => {
  const navigate = useNavigate();
  // Convert schedule to a string if it's an object
  const schedule = typeof job.schedule === "object" ? JSON.stringify(job.schedule) : job.schedule;

  const handleDelete = async (e) => {
    e.stopPropagation(); // Prevent the card's onClick from firing
    try {
      await deleteJob(job.id);
      onDelete(job.id); // Notify the parent component to remove the job from the list
    } catch (error) {
      console.error("Error deleting job:", error);
    }
  };

  const handleEdit = (e) => {
    e.stopPropagation(); // Prevent the card's onClick from firing
    navigate(`/edit-job/${job.id}`); // Navigate to the edit job page
  };

  return (
    <motion.div
      className="job-card"
      onClick={onClick}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
    >
      <div className="job-header">
        <h3>{job.name}</h3>
        <div className="job-actions">
          <button className="icon-button" onClick={handleEdit}>
            <FontAwesomeIcon icon={faEdit} />
          </button>
          <button className="icon-button" onClick={handleDelete}>
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
          <span className={`status-badge ${job.status}`}>{job.status}</span>
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
      </div>
    </motion.div>
  );
};

export default JobCard; 