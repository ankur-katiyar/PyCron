import React from "react";

const JobDetailsModal = ({ job, onClose }) => {
  // Convert schedule to a string if it's an object
  const schedule = typeof job.schedule === "object" ? JSON.stringify(job.schedule) : job.schedule;

  return (
    <div className="modal-overlay">
      <div className="modal">
        <div className="modal-header">
          <h2>{job.name}</h2>
          <button onClick={onClose}>×</button>
        </div>
        <div className="modal-body">
          <p><strong>Schedule:</strong> {schedule}</p>
          <p><strong>Command:</strong> {job.command}</p>
          <p><strong>Status:</strong> <span className={`status-badge ${job.status}`}>{job.status}</span></p>
          <h3>Logs</h3>
          <div className="logs-table">
            <table>
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>STDOUT</th>
                  <th>STDERR</th>
                  <th>Execution Time</th>
                </tr>
              </thead>
              <tbody>
                {job.logs.map((log, index) => (
                  <tr key={index}>
                    <td>{log.timestamp}</td>
                    <td>{log.stdout}</td>
                    <td>{log.stderr}</td>
                    <td>{log.execution_time} seconds</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default JobDetailsModal; 