import React, { useEffect, useState } from "react";
import Filters from "../components/TopPlayers/Filters";
import PlayersList from "../components/TopPlayers/PlayersList";
import "./TopPlayers.css";
export default function TopPlayers() {
  const [players, setPlayers] = useState([]);
  const [filter, setFilter] = useState("last7days"); // Valore di default

  // Simula la chiamata API
  useEffect(() => {
    async function fetchPlayers() {
      try {
        const response = await fetch(`https://api.example.com/players?filter=${filter}`);
        const data = await response.json();
        setPlayers(data);
      } catch (error) {
        console.error("Errore nel recupero dati", error);
      }
    }

    fetchPlayers();
  }, [filter]);

  return (
    <div className="top-players-container">
      <Filters setFilter={setFilter} />
      <PlayersList players={players} />
    </div>
  );
}