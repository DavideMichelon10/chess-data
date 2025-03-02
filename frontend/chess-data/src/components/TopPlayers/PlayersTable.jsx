// PlayersTable.jsx
import React from "react";

export default function PlayersTable({ players }) {
  return (
    <div className="vs-content">
      {players.map((player, index) => {
        // Scegli come mostrarlo:
        const hasName = player.name && player.name.trim() !== "" && player.name !== player.username;
        
        return (
          <div className="vs-row vs-player-row" key={player.username + index}>
            {/* Rank */}
            <div className="vs-item vs-rank">{index + 1}</div>

            {/* Avatar + Nome e Username */}
            <div className="vs-item vs-channel-wrapper">
              {player.avatar_url ? (
                <img
                  src={player.avatar_url}
                  alt={`${player.username} avatar`}
                  className="vs-channel-image"
                />
              ) : (
                <div className="vs-channel-placeholder">
                  {player.username.charAt(0)}
                </div>
              )}

              <div className="vs-channel">
                {/* Riga superiore: se esiste un name, mostralo. Altrimenti user. */}
                <div className="vs-channel-name">
                  {hasName ? player.name : player.username}
                </div>
                {/* Riga inferiore: se esiste un name diverso, mostra @username */}
                {hasName && (
                  <div className="vs-channel-id">@{player.username}</div>
                )}
              </div>
            </div>

            {/* ...altre colonne (rating, win, loss, draw)... */}
            <div className="vs-item vs-rating vs-item--green"> 
              {player.last_rating ?? "-"}
            </div>
            <div className="vs-item vs-win">{player.win ?? 0}</div>
            <div className="vs-item vs-loss">{player.loss ?? 0}</div>
            <div className="vs-item vs-draw">{player.draw ?? 0}</div>
          </div>
        );
      })}
    </div>
  );
}