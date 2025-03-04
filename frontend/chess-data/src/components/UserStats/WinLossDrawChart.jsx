import { ArcElement, Chart, Legend, Tooltip } from "chart.js";
import React from "react";
import { Doughnut } from "react-chartjs-2";
import "./WinLossDrawChart.css";

// Registriamo gli elementi necessari per il Doughnut Chart
Chart.register(ArcElement, Tooltip, Legend);

export default function WinLossDrawChart({ win, loss, draw }) {
  const data = {
    labels: ["Wins", "Losses", "Draws"],
    datasets: [
      {
        data: [win, loss, draw],
        backgroundColor: ["#00cc66", "#cc3333", "#aaaaaa"], // Colori per ogni sezione
        borderColor: ["#00aa55", "#aa2222", "#888888"], // Bordo sottile per ogni sezione
        borderWidth: 2,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: "bottom",
        labels: {
          color: "#fff",
        },
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
      <h3 className="chart-title">Win / Loss / Draw</h3>
      <div className="chart-container">
        <Doughnut data={data} options={options} />
      </div>
    </div>
  );
}