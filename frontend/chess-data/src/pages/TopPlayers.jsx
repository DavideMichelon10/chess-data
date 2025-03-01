import React, { useEffect, useState } from "react";
import "../components/TopPlayers/Filters.css";
import PlayersTable from "../components/TopPlayers/PlayersTable";
import "./TopPlayers.css";

export default function TopPlayers() {
  const [filter, setFilter] = useState("chess_blitz");
  const [players, setPlayers] = useState([]);
  const [cachedData, setCachedData] = useState({});

  useEffect(() => {
    if (cachedData[filter]) {
      setPlayers(cachedData[filter]);
    } else {
      fetchTopPlayers(filter);
    }
  }, [filter]);

  async function fetchTopPlayers(gameType) {
    try {
      const response = await fetch(`http://127.0.0.1:8000/top-players/?game_type=${gameType}&limit=10`);
      const data = await response.json();
      if (data.top_players) {
        setPlayers(data.top_players);
        setCachedData((prev) => ({
          ...prev,
          [gameType]: data.top_players,
        }));
      } else {
        setPlayers([]);
      }
    } catch (error) {
      console.error("Errore nel recupero dei dati:", error);
      setPlayers([]);
    }
  }

  function handleFilterChange(newFilter) {
    if (newFilter !== filter) {
      setFilter(newFilter);
    }
  }

  return (
    <div className="top-players-container">
      <div className="filters">
        <div className="filter-category elevated rounded">
          <h4>By Game Mode</h4>
          <button
            className={filter === "chess_blitz" ? "selected" : ""}
            onClick={() => handleFilterChange("chess_blitz")}
          >
            Blitz
          </button>
          <button
            className={filter === "chess_rapid" ? "selected" : ""}
            onClick={() => handleFilterChange("chess_rapid")}
          >
            Rapid
          </button>
          <button
            className={filter === "chess_bullet" ? "selected" : ""}
            onClick={() => handleFilterChange("chess_bullet")}
          >
            Bullet
          </button>
          <button
            className={filter === "chess_daily" ? "selected" : ""}
            onClick={() => handleFilterChange("chess_daily")}
          >
            Daily
          </button>
        </div>
      </div>

      <div className="players-list">
        <PlayersTable players={players} />
      </div>
    </div>
  );
}