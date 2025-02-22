import React from "react";

const Navbar = () => {
  return (
    <div className="navbar">
      <div className="search-bar">
        <input type="text" placeholder="Search jobs..." />
      </div>
      <div className="user-profile">
        <span>Admin</span>
        <img src="https://via.placeholder.com/40" alt="Profile" />
      </div>
    </div>
  );
};

export default Navbar; 