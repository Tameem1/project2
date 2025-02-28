// arachatfrontend/src/components/NavBar.jsx
import React from 'react';
import { Link } from 'react-router-dom';

export default function NavBar() {
  const navStyle = {
    display: 'flex',
    justifyContent: 'space-around',
    alignItems: 'center',
    padding: '10px 20px',
    backgroundColor: '#2c3e50',
    color: '#fff',
  };

  const linkStyle = {
    color: '#fff',
    textDecoration: 'none',
    fontWeight: 'bold',
  };

  return (
    <nav style={navStyle}>
     <Link to="/profile" style={linkStyle}>
       Profile
     </Link>
      <Link to="/" style={linkStyle}>
        My Chatbots
      </Link>
      <Link to="/pricing" style={linkStyle}>
        Pricing
      </Link>
      <Link to="/create-chatbot" style={linkStyle}>
        Create Chatbot
      </Link>
      {/* Add more links as needed */}
    </nav>
  );
}