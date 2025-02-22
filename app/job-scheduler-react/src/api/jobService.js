import axios from "axios";

const API_URL = "http://localhost:8000";

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