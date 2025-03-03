import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import "./UserStats.css"; // CSS dedicato per lo stile

export default function UserStats() {
  const { username } = useParams();
  const [userData, setUserData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedGameType, setSelectedGameType] = useState("chess_blitz");

  useEffect(() => {
    async function fetchUser() {
      try {
        const response = await fetch(
          `http://127.0.0.1:8000/search?player_name=${username}`
        );
        const data = await response.json();

        setUserData(data);
        setLoading(false);
      } catch (err) {
        console.error("Error loading user:", err);
        setUserData(null);
        setLoading(false);
      }
    }
    fetchUser();
  }, [username]);

  if (loading) return <div className="loading">Loading...</div>;

  if (!userData || userData.message) {
    return <div className="error-message">Nessun risultato trovato</div>;
  }

  const { username: fetchedUsername, user_data } = userData;
  const displayName = user_data.name || fetchedUsername;
  const avatarUrl = user_data.avatar_storage_url
    ? user_data.avatar_storage_url.replace("gs://", "https://storage.googleapis.com/")
    : null;
  const category = user_data.category || "-";

  // Dati della modalità selezionata
  const gameData = user_data[selectedGameType] || {};
  const { last_rating, best_rating, win, loss, draw, best_game_url } = gameData;

  return (
    <div className="user-profile-container">
      {/* 🏆 Sezione profilo con bottoni delle modalità */}
      <div className="user-card">
      {/* Sezione superiore con info utente */}
        <div className="profile-top">
          {avatarUrl && <img src={avatarUrl} alt="avatar" className="user-avatar" />}
          <div className="user-info">
            <h1 className="user-name">{displayName}</h1>
            <p className="user-username">@{fetchedUsername}</p>
            <span className="user-category">{category}</span>
          </div>
        </div>
        
        {/* Selettore modalità di gioco - rimane nella card ma in posizione fissa */}
        <div className="game-mode-selector">
          {["chess_blitz", "chess_bullet", "chess_rapid", "chess_daily"].map((type) => (
            <button
              key={type}
              className={`game-type-button ${selectedGameType === type ? "active" : ""}`}
              onClick={() => setSelectedGameType(type)}
            >
              {type.replace("chess_", "").toUpperCase()}
            </button>
          ))}
        </div>
  </div>

      {/* 📊 Box con statistiche */}
      <div className="stats-container">
        <div className="stat-card">
          <span className="stat-title">Current Rating</span>
          <span className="stat-value">{last_rating || "-"}</span>
        </div>
        <div className="stat-card">
          <span className="stat-title">Best Rating</span>
          <span className="stat-value">{best_rating || "-"}</span>
        </div>
      </div>

      {/* ♟️ Miglior Partita */}
      {best_game_url && (
        <div className="best-game">
          <h3>Miglior Partita</h3>
          <a href={best_game_url} target="_blank" rel="noopener noreferrer">
            Guarda la partita
          </a>
        </div>
      )}
    </div>
  );
}