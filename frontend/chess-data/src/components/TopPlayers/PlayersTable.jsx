import React from "react";

export default function PlayersTable({ players }) {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full border-collapse bg-gray-900 text-white rounded-lg shadow-lg">
        <thead>
          <tr className="bg-gray-800 text-gray-300 text-left">
            <th className="px-6 py-3 text-sm font-medium">Rank</th>
            <th className="px-6 py-3 text-sm font-medium">Player</th>
            <th className="px-6 py-3 text-sm font-medium">Game Type</th>
            <th className="px-6 py-3 text-sm font-medium text-right">Best Rating</th>
          </tr>
        </thead>
        <tbody>
          {players.map((player, index) => (
            <tr key={index} className="border-b border-gray-700 hover:bg-gray-800 transition">
              <td className="px-6 py-4 text-gray-400">{index + 1}</td>
              <td className="px-6 py-4 flex items-center space-x-3">
                {/* Se avatar_url esiste, mostra l’immagine */}
                {player.avatar_url ? (
                  <img
                    src={player.avatar_url}
                    className="w-10 h-10 rounded-full"
                    alt={`${player.player_name} avatar`}
                  />
                ) : (
                  <div className="w-10 h-10 bg-gray-700 rounded-full flex items-center justify-center text-lg font-semibold">
                    {player.player_name.charAt(0)}
                  </div>
                )}
                <span className="font-semibold">{player.player_name}</span>
              </td>
              <td className="px-6 py-4">{player.game_type}</td>
              <td className="px-6 py-4 text-right text-green-400 font-bold">
                {player.best_rating?.toLocaleString()}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}