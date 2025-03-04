import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./SearchBar.css";

export default function SearchBar() {
  const [query, setQuery] = useState("");
  const navigate = useNavigate();

  function handleSearch(e) {
    e.preventDefault(); // Previene il submit del form
    
    // Rimuovi spazi all'inizio e alla fine
    const trimmedQuery = query.trim();
    
    if (trimmedQuery) {
      // Naviga alla pagina del giocatore
      navigate(`/${trimmedQuery}`);
    }
  }

  return (
    <div className="search-section">
      {/* Titolo */}
      <h1 className="search-title">Search any<br/>Chess Player</h1>

      {/* Barra di ricerca */}
      <form 
        className="search-bar gradient-border no-query" 
        onSubmit={handleSearch}
      >
        <input 
          id="search-bar-input" 
          maxLength="100" 
          placeholder='Try searching "hikaru"' 
          autoComplete="off" 
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button 
          type="submit" 
          className="vs-button primary-red md square_button round"
        >
          🔍
        </button>
      </form>
    </div>
  );
}