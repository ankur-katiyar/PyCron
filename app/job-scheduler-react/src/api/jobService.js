import axios from "axios";

const API_URL = "http://localhost:8000";

export const getJobs = async (token) => {
  const response = await axios.get(`${API_URL}/jobs`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return response;
};

export const fetchJobs = async () => {
  try {
    const token = localStorage.getItem("token");
    console.log("Token being sent:", token);
    const response = await axios.get(`${API_URL}/jobs`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  } catch (error) {
    console.error("Error fetching jobs:", error);
    throw error; // Rethrow the error to handle it in the component
  }
};

export const deleteJob = async (jobId) => {
  try {
    const token = localStorage.getItem("token");
    const response = await axios.delete(`${API_URL}/jobs/${jobId}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  } catch (error) {
    console.error("Error deleting job:", error);
    throw error;
  }
};

export const runJobAdhoc = async (jobId, token) => {
  try {
    const response = await axios.post(
      `${API_URL}/jobs/${jobId}/run`,
      {}, // Empty body
      {
        headers: {
          Authorization: `Bearer ${token}`,
          accept: "application/json", // Add the accept header
        },
      }
    );
    return response.data;
  } catch (error) {
    console.error("Error running job ad-hoc:", error);
    throw error;
  }
};

export const updateJobStatus = async (jobId, status, token) => {
  try {
    const response = await axios.put(
      `${API_URL}/jobs/${jobId}/status`,
      { status }, // Request body
      {
        headers: {
          Authorization: `Bearer ${token}`,
          accept: "application/json",
          "Content-Type": "application/json",
        },
      }
    );
    return response.data;
  } catch (error) {
    console.error("Error updating job status:", error);
    throw error;
  }
}; 