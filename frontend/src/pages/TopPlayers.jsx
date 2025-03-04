import React, { useEffect, useState } from "react";
import PlayersTable from "../components/TopPlayers/PlayersTable";
import "./TopPlayers.css";

export default function TopPlayers() {
  // Impostiamo un valore di default sia per il game mode che per il title
  const [gameFilter, setGameFilter] = useState("chess_blitz");
  const [titleFilter, setTitleFilter] = useState("GM"); // di default GM

  const [players, setPlayers] = useState([]);
  const [cachedData, setCachedData] = useState({});

  // Ricarica i dati quando cambia uno dei due filtri
  useEffect(() => {
    const cacheKey = `${gameFilter}_${titleFilter}`;
    if (cachedData[cacheKey]) {
      setPlayers(cachedData[cacheKey]);
    } else {
      fetchTopPlayers(gameFilter, titleFilter);
    }
  }, [gameFilter, titleFilter]);

  async function fetchTopPlayers(gameType, category) {
    try {
      // Se la categoria è sempre selezionata, non c'è bisogno di un controllo "if"
      const url = `http://127.0.0.1:8989/top-players/?game_type=${gameType}&category=${category}&limit=100`;
      const response = await fetch(url);
      const data = await response.json();

      if (data.top_players) {
        const newPlayers = data.top_players;
        const cacheKey = `${gameType}_${category}`;
        setPlayers(newPlayers);
        setCachedData((prev) => ({
          ...prev,
          [cacheKey]: newPlayers,
        }));
      } else {
        setPlayers([]);
      }
    } catch (error) {
      console.error("Errore nel recupero dei dati:", error);
      setPlayers([]);
    }
  }

  function handleGameFilterChange(newGame) {
    if (newGame !== gameFilter) {
      setGameFilter(newGame);
    }
  }

  function handleTitleFilterChange(newTitle) {
    if (newTitle !== titleFilter) {
      setTitleFilter(newTitle);
    }
  }

  return (
    <div className="toplist-container">
      {/* ------------- SIDEBAR ------------- */}
      <div className="tp-sidebar">
        
        {/* -------- FILTRI GAME MODE -------- */}
        <div className="tp-sidebar-container">
          <div className="tp-sidebar-header">
            <span className="tp-sidebar-header--lg">By Game Mode</span>
          </div>
          <div className="tp-sidebar-content-search">
            {["chess_blitz", "chess_rapid", "chess_bullet", "chess_daily"].map((mode) => (
              <div
                key={mode}
                className={
                  "tp-sidebar-item " + 
                  (gameFilter === mode ? "tp-sidebar-item--active" : "")
                }
                onClick={() => handleGameFilterChange(mode)}
              >
                {mode.replace("chess_", "").toUpperCase()}
              </div>
            ))}
          </div>
        </div>

        {/* -------- FILTRI TITLE -------- */}
        <div className="tp-sidebar-container">
          <div className="tp-sidebar-header">
            <span className="tp-sidebar-header--lg">Title</span>
          </div>
          <div className="tp-sidebar-content-search">
            {/* Nessuna opzione "vuota", così uno dei tre è sempre selezionato */}
            {["GM", "IM", "FM"].map((title) => (
              <div
                key={title}
                className={
                  "tp-sidebar-item " +
                  (titleFilter === title ? "tp-sidebar-item--active" : "")
                }
                onClick={() => handleTitleFilterChange(title)}
              >
                {title}
              </div>
            ))}
          </div>
        </div>

      </div>

      {/* ------------- TABELLA ------------- */}
      <div className="viewstats-table">
        <div className="vs-header">
          <div className="vs-row">
            <div className="vs-item vs-rank">Rank</div>
            <div className="vs-item">Player</div>
            <div className="vs-item vs-rating">Rating</div>
            <div className="vs-item vs-win">Win</div>
            <div className="vs-item vs-loss">Loss</div>
            <div className="vs-item vs-draw">Draw</div>
          </div>
        </div>
          
        {/* Corpo tabella */}
        <PlayersTable players={players} />
      </div>
    </div>
  );
}