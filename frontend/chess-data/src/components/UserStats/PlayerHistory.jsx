import { CategoryScale, Chart, Legend, LinearScale, LineElement, PointElement, Title, Tooltip } from "chart.js";
import React, { useEffect, useState } from "react";
import { Line } from "react-chartjs-2";
import { useParams } from "react-router-dom";
import "./PlayerHistory.css"; // Importa il CSS per lo stile

// Registrazione degli elementi per il grafico a linee
Chart.register(LineElement, PointElement, LinearScale, CategoryScale, Title, Tooltip, Legend);

export default function PlayerHistory({ selectedGameType }) {
  const { username } = useParams();
  const [historyData, setHistoryData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState("MAX");

  const calculateStartDate = () => {
    const today = new Date();
    if (dateRange === "1D") {
      return new Date(today.setDate(today.getDate() - 1)).toISOString().split("T")[0];
    } else if (dateRange === "2D") {
      return new Date(today.setDate(today.getDate() - 2)).toISOString().split("T")[0];
    } else if (dateRange === "7D") {
      return new Date(today.setDate(today.getDate() - 7)).toISOString().split("T")[0];
    } else if (dateRange === "3M") {
      return new Date(today.setMonth(today.getMonth() - 3)).toISOString().split("T")[0];
    }
    return "2025-03-01"; // Default MAX
  };

  useEffect(() => {
    async function fetchHistory() {
      setLoading(true);
      setHistoryData(null);
      try {
        const startDate = calculateStartDate();
        const response = await fetch(
          `http://127.0.0.1:8989/player-history/?player_name=${username}&game_type=${selectedGameType}&start_date=${startDate}`
        );
        const data = await response.json();
        setHistoryData(data.history);
        setLoading(false);
      } catch (err) {
        console.error("Error loading player history:", err);
        setHistoryData(null);
        setLoading(false);
      }
    }
    fetchHistory();
  }, [username, selectedGameType, dateRange]);

  const isDataAvailable = historyData && historyData.length > 0;

  // Preparazione dati per il grafico
  const labels = isDataAvailable ? historyData.map((entry) => new Date(entry.timestamp).toLocaleDateString()) : [];
  const ratings = isDataAvailable ? historyData.map((entry) => entry.last_rating) : [];

  const data = {
    labels: labels,
    datasets: isDataAvailable
      ? [
        {
          label: "Rating nel tempo",
          data: ratings,
          borderColor: "#007bff",
          backgroundColor: "rgba(255, 0, 183, 0.5)",
          tension: 0.3,
        },
      ]
      : [],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: "top",
      },
      title: {
        display: true,
        text: `Storico Rating di ${username} (${selectedGameType.replace("chess_", "").toUpperCase()})`,
      },
    },
  };

  return (
    <div className="player-history-container">
      <div className="date-range-buttons">
        {["MAX", "1D", "2D", "7D", "3M"].map((range) => (
          <button
            key={range}
            type="button"  // Aggiunto per evitare refresh della pagina
            className={`date-button ${dateRange === range ? "active" : ""}`}
            onClick={() => setDateRange(range)}
          >
            {range}
          </button>
        ))}
      </div>
      {loading ? (
        <div className="loading-message">Caricamento dati...</div>
      ) : isDataAvailable ? (
        <Line data={data} options={options} />
      ) : (
        <div className="error-message">No data found.</div>
      )}
    </div>
  );
}
