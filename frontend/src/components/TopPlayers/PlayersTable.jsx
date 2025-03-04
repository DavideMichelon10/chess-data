import React from "react";
import { Link } from "react-router-dom";

export default function PlayersTable({ players }) {
  return (
    <div className="vs-content">
      {players.map((player, index) => {
        // Determina se mostrare il name o lo username
        const displayName = player.name && player.name.trim() !== ""
          ? player.name
          : player.username;

        return (
         
          <Link
            to={`/${player.username}`}
            className="vs-row vs-player-row"
            key={player.username + index}
            style={{ textDecoration: "none", color: "inherit" }}
          >
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
                <div className="vs-channel-name">{displayName}</div>
                {/* Se name è diverso dallo username, mostra sotto @username */}
                {displayName !== player.username && (
                  <div className="vs-channel-id">@{player.username}</div>
                )}
              </div>
            </div>

            {/* Rating, Win, Loss, Draw (esempio) */}
            <div className="vs-item vs-rating vs-item--green">
              {player.last_rating ?? "-"}
            </div>
            <div className="vs-item vs-win">{player.win ?? 0}</div>
            <div className="vs-item vs-loss">{player.loss ?? 0}</div>
            <div className="vs-item vs-draw">{player.draw ?? 0}</div>
          </Link>
        );
      })}
    </div>
  );
}