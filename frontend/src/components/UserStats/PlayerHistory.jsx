import { CategoryScale, Chart, Legend, LinearScale, LineElement, PointElement, Title, Tooltip } from "chart.js";
import React, { useEffect, useState } from "react";
import { Line } from "react-chartjs-2";
import { useParams } from "react-router-dom";
import "./PlayerHistory.css"; // Importa il CSS per lo stile

// Registrazione degli elementi per il grafico a linee
Chart.register(LineElement, PointElement, LinearScale, CategoryScale, Title, Tooltip, Legend);

export default function PlayerHistory({ selectedGameType }) {
  const { username } = useParams();
  const [historyData, setHistoryData] = useState([]);
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
      setHistoryData([]);
      try {
        const startDate = calculateStartDate();
        const response = await fetch(
          `http://127.0.0.1:8989/player-history/?player_name=${username}&game_type=${selectedGameType}&start_date=${startDate}`
        );
        const data = await response.json();
        setHistoryData(data.history || []);
      } catch (err) {
        console.error("Error loading player history:", err);
        setHistoryData([]);
      } finally {
        setLoading(false);
      }
    }
    fetchHistory();
  }, [username, selectedGameType, dateRange]);

  const isDataAvailable = historyData.length > 0;

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false, // Rimuove la legenda
      },
      title: {
        display: true,
        text: `RATING ${selectedGameType.replace("chess_", "").toUpperCase()}`,
        align: 'start', // Allinea il titolo a sinistra
        color: 'white', // Colore del testo del titolo
        font: {
          size: 16,
          weight: 'bold'
        },
        padding: {
          bottom: 20 // Aggiunge un po' di spazio sotto il titolo
        }
      }
    },
    scales: {
      x: {
        display: isDataAvailable,
        grid: {
          color: 'rgba(255,255,255,0.1)' // Colore griglia più chiaro
        }
      },
      y: {
        display: isDataAvailable,
        grid: {
          color: 'rgba(255,255,255,0.1)' // Colore griglia più chiaro
        }
      }
    }
  };

  const data = {
    labels: isDataAvailable ? historyData.map((entry) => new Date(entry.timestamp).toLocaleDateString()) : [],
    datasets: [
      {
        label: "", // Rimuove l'etichetta del dataset
        data: isDataAvailable ? historyData.map((entry) => entry.last_rating) : [],
        borderColor: "#00FF00", // Verde acceso
        backgroundColor: "rgba(0,255,0,0.2)", // Verde trasparente
        borderWidth: 2,
        pointBackgroundColor: "#00FF00",
        pointBorderColor: "#00FF00",
        pointRadius: 4,
        tension: 0.3,
      },
    ],
  };
  return (
    <div className="player-history-container">
      <div className="date-range-buttons">
        {["MAX", "1D", "2D", "7D", "3M"].map((range) => (
          <button
            key={range}
            type="button"
            className={`interactive-button date-button ${dateRange === range ? "active" : ""}`}
            onClick={() => setDateRange(range)}
          >
            {range}
          </button>
        ))}
      </div>

      {/* Contenitore fisso per mantenere la dimensione */}
      <div className="chart-container-graph">
        {loading ? (
          <div className="loading-message">Caricamento dati...</div>
        ) : isDataAvailable ? (
          <Line data={data} options={options} />
        ) : (
          <div className="error-message">Nessun dato disponibile</div>
        )}
      </div>
    </div>
  );
}