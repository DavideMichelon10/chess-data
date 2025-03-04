import React from "react";
import "./Filters.css";

export default function Filters({ setFilter }) {
  return (
    <div className="filters">

      <div className="filter-category elevated rounded">
        <h4>By Game Mode</h4>
        <button onClick={() => setFilter("blitz")}>Blitz</button>
        <button onClick={() => setFilter("rapid")}>Rapid</button>
        <button onClick={() => setFilter("bullet")}>Bullet</button>
        <button onClick={() => setFilter("daily")}>Daily</button>
      </div>
      
      <div className="filter-category elevated rounded">
        <h4>By Title</h4>
        <button onClick={() => setFilter("GM")}>Grandmaster (GM)</button>
        <button onClick={() => setFilter("IM")}>International Master (IM)</button>
        <button onClick={() => setFilter("FM")}>FIDE Master (FM)</button>
        <button onClick={() => setFilter("NM")}>National Master (NM)</button>
        <button onClick={() => setFilter("CM")}>Candidate Master (CM)</button>
      </div>
    </div>
  );
}