import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

function ResultsPage() {
  const { player_name } = useParams();
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchData = async () => {
      try {
        
        const response = await fetch(`http://127.0.0.1:8000/search/?player_name=${player_name}`);
        const result = await response.json();

        if (response.ok) {
          setData(result.stats);
        } else {
          setError(result.message || "Errore nel caricamento dei dati.");
        }
      } catch (err) {
        setError("Errore di connessione al server.");
      }
    };

    fetchData();
  }, [player_name]);

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <h1 className="text-4xl font-bold mb-6">Results for {player_name}</h1>

      {error && <p className="text-red-500">{error}</p>}

      {data ? (
        <table className="w-full border-collapse border border-gray-700">
          <thead>
            <tr className="bg-gray-800">
              <th className="p-3 border border-gray-700">Game Type</th>
              <th className="p-3 border border-gray-700">Last Rating</th>
              <th className="p-3 border border-gray-700">Best Rating</th>
            </tr>
          </thead>
          <tbody>
            {data.map((row, index) => (
              <tr key={index} className="text-center">
                <td className="p-3 border border-gray-700">{row.game_type}</td>
                <td className="p-3 border border-gray-700">{row.last_rating}</td>
                <td className="p-3 border border-gray-700">{row.best_rating}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p>Loading...</p>
      )}
    </div>
  );
}

export default ResultsPage;