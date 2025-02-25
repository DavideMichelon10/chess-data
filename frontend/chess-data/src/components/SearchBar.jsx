import { useState } from "react";
import "./SearchBar.css"; // Assicurati che il CSS sia importato

export default function SearchBar () {
  const [query, setQuery] = useState("");

  return (
    <div className="search-section">
      {/* Titolo */}
      <h1 className="search-title">Search any<br/>Chess Player</h1>

      {/* Barra di ricerca */}
      <form className="search-bar gradient-border no-query">
        <input 
          id="search-bar-input" 
          maxLength="100" 
          placeholder='Try searching "Magnus Carlsen"' 
          autoComplete="off" 
          type="text"
        />
        <button className="vs-button primary-red md square_button round">
          🔍
        </button>
      </form>
    </div>
  );
};