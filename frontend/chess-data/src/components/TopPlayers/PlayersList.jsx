import React from "react";
import "./PlayersList.css"; // Stile della tabella

export default function PlayersList({ players }) {
  return (
    <div className="players-list">
      <table>
        <thead>
          <tr>
            <th>Rank</th>
            <th>Channel</th>
            <th>New Subs</th>
            <th>Total Subs</th>
            <th>Total Views</th>
          </tr>
        </thead>
        <tbody>
          {players.map((player, index) => (
            <tr key={player.id}>
              <td>{index + 1}</td>
              <td>
                <img src={player.avatar} alt={player.name} className="avatar" />
                {player.name}
              </td>
              <td className="green-text">+{player.newSubs.toLocaleString()}</td>
              <td>{player.totalSubs.toLocaleString()}M</td>
              <td>{player.totalViews.toLocaleString()}B</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}