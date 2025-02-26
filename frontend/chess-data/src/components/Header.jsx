import React from "react";
import logo from "../assets/logo.png";
import "./Header.css";

export default function Header() {
  return (
    <header className="header">
      {/* Logo */}
      <div className="header-left">
        <img src={logo} alt="logo" className="logo" />
        <span className="brand-name">CHESSDATA</span>
      </div>

      {/* Navbar */}
      <nav className="nav">
        <ul className="nav-list">
          <li className="nav-list-item dropdown">Top Players</li>
        </ul>
      </nav>

      {/* Search e Login */}
      <div className="header-right"> 
        <button className="btn login">Log In</button>
        <button className="btn signup">
          <span className="user-icon">👤</span> Sign Up
        </button>
      </div>
    </header>
  );
};
