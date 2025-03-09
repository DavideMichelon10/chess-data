import { ArcElement, Chart, Tooltip } from "chart.js";
import React from "react";
import { Doughnut } from "react-chartjs-2";
import "./WinLossDrawChart.css";

// Registriamo gli elementi necessari per il Doughnut Chart
Chart.register(ArcElement, Tooltip);

export default function WinLossDrawChart({ win, loss, draw }) {
  const data = {
    datasets: [
      {
        data: [win, loss, draw],
        backgroundColor: ["#00cc66", "#cc3333", "#aaaaaa"], // Colori per ogni sezione
        borderWidth: 0, // Rimuove i bordi tra le sezioni per un look più pulito
        cutout: "70%", // Rende il doughnut più sottile e simile al design richiesto
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false, // Nasconde la legenda interna del grafico
      },
      tooltip: {
        callbacks: {
          label: (tooltipItem) => {
            const value = tooltipItem.raw;
            return ` ${value} games`;
          },
        },
      },
    },
  };

  return (
    <div className="win-loss-draw-card">
      <h3 className="chart-title">Win vs Loss vs Draw</h3>
      <div className="chart-content">
        {/* Legenda a sinistra */}
        <div className="chart-legend">
          <div className="legend-item">
            <span className="legend-color" style={{ backgroundColor: "#00cc66" }}></span>
            <span className="legend-text">Wins</span>
            <span className="legend-value">{win}</span>
          </div>
          <div className="legend-item">
            <span className="legend-color" style={{ backgroundColor: "#cc3333" }}></span>
            <span className="legend-text">Losses</span>
            <span className="legend-value">{loss}</span>
          </div>
          <div className="legend-item">
            <span className="legend-color" style={{ backgroundColor: "#aaaaaa" }}></span>
            <span className="legend-text">Draws</span>
            <span className="legend-value">{draw}</span>
          </div>
        </div>

        {/* Grafico più grande */}
        <div className="chart-container">
          <Doughnut data={data} options={options} />
        </div>
      </div>
    </div>
  );
}