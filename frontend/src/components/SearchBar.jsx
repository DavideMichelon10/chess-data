import { Search } from 'lucide-react';
import React, { useState } from 'react';

const SearchBar = ({ onSearch }) => {
  const [query, setQuery] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    onSearch(query);
  };

  return (
    <div className="min-h-screen bg-black flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-3xl text-center mb-8">
        <h1 className="text-white text-5xl font-bold mb-12">
          Search any Chess Player
        </h1>
        
        <form onSubmit={handleSubmit} className="relative">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Try searching 'Magnus Carlsen'..."
            className="w-full px-4 py-3 pr-12 rounded-lg bg-gray-800 text-white placeholder-gray-400 border border-gray-700 focus:outline-none focus:border-gray-500"
          />
          <button
            type="submit"
            className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white"
          >
            <Search size={20} />
          </button>
        </form>
      </div>
    </div>
  );
};

export default SearchBar;