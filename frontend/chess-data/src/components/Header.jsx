import React from "react";
import { Link } from "react-router-dom";
import logo from "../assets/logo.png";
import "./Header.css";

export default function Header() {
  return (
    <header className="header">
      {/* Logo con link alla home */}
      <div className="header-left">
        <Link to="/">
          <img src={logo} alt="logo" className="logo" />
        </Link>
        <span className="brand-name">CHESSDATA</span>
      </div>

      {/* Navbar */}
      <nav className="nav">
        <ul className="nav-list">
          <li className="nav-list-item dropdown">
            <Link to="/top-players">Top Players</Link>
          </li>
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
}