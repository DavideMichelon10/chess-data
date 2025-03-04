import React, { useCallback, useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import PlayerHistory from "../components/UserStats/PlayerHistory";
import WinLossDrawChart from "../components/UserStats/WinLossDrawChart";
import "./UserStats.css";

// Funzione separata per la chiamata API
const fetchUserData = async (username) => {
  try {
    const response = await fetch(
      `http://127.0.0.1:8989/search?player_name=${username}`
    );
    
    if (!response.ok) {
      throw new Error('Errore nel recupero dei dati');
    }
    
    return await response.json();
  } catch (error) {
    console.error("Errore nel caricamento dell'utente:", error);
    return null;
  }
};

export default function UserStats() {
  const { username } = useParams();
  
  // Stato con struttura più esplicita
  const [state, setState] = useState({
    userData: null,
    loading: true,
    error: null,
    selectedGameType: "chess_blitz"
  });

  // Utilizzare useCallback per ottimizzare le chiamate
  const loadUserData = useCallback(async () => {
    setState(prev => ({ ...prev, loading: true }));
    
    try {
      const data = await fetchUserData(username);
      
      setState(prev => ({
        ...prev,
        userData: data,
        loading: false,
        error: data ? null : new Error('Nessun risultato trovato')
      }));
    } catch (error) {
      setState(prev => ({
        ...prev,
        userData: null,
        loading: false,
        error: error
      }));
    }
  }, [username]);

  // useEffect con dipendenze precise
  useEffect(() => {
    loadUserData();
  }, [loadUserData]);

  // Funzione per cambiare modalità di gioco
  const handleGameTypeChange = (gameType) => {
    setState(prev => ({ ...prev, selectedGameType: gameType }));
  };

  // Rendering condizionale con gestione errori
  if (state.loading) return <div className="loading">Caricamento...</div>;
  if (state.error) return <div className="error-message">{state.error.message}</div>;
  if (!state.userData) return <div className="error-message">Nessun risultato</div>;

  const { username: fetchedUsername, user_data } = state.userData;
  const displayName = user_data.name || fetchedUsername;
  const avatarUrl = user_data.avatar_storage_url
    ? user_data.avatar_storage_url.replace("gs://", "https://storage.googleapis.com/")
    : null;
  const category = user_data.category || "-";

  // Dati della modalità selezionata
  const gameData = user_data[state.selectedGameType] || {};
  const { last_rating, best_rating, win, loss, draw, best_game_url } = gameData;

  return (
    <div className="user-profile-container">
      <div className="user-card">
        <div className="profile-top">
          {avatarUrl && <img src={avatarUrl} alt="avatar" className="user-avatar" />}
          <div className="user-info">
            <h1 className="user-name">{displayName}</h1>
            <p className="user-username">@{fetchedUsername}</p>
            <span className="user-category">{category}</span>
          </div>
        </div>

        {/* Selettore modalità di gioco */}
        <div className="game-mode-selector">
          {["chess_blitz", "chess_bullet", "chess_rapid", "chess_daily"].map((type) => (
            <button
              key={type}
              className={`game-type-button ${state.selectedGameType === type ? "active" : ""}`}
              onClick={() => handleGameTypeChange(type)}
            >
              {type.replace("chess_", "").toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      {/* Resto del codice rimane invariato */}
      <div className="stats-chart-container">
        <div className="rating-column">
          <div className="stat-card">
            <span className="stat-title">Current Rating</span>
            <span className="stat-value">{last_rating || "-"}</span>
          </div>
          <div className="stat-card">
            <span className="stat-title">Best Rating</span>
            <span className="stat-value">{best_rating || "-"}</span>
          </div>
        </div>

        <div className="chart-column">
          <WinLossDrawChart win={win} loss={loss} draw={draw} />
        </div>
      </div>

      {best_game_url && (
        <div className="best-game">
          <h3>Miglior Partita</h3>
          <a href={best_game_url} target="_blank" rel="noopener noreferrer">
            Guarda la partita
          </a>
        </div>
      )}

      <div className="player-history">
        <PlayerHistory selectedGameType={state.selectedGameType} />
      </div>
    </div>
  );
}