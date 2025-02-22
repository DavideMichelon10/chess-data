import { Search } from 'lucide-react';
import { useState } from 'react';
import './App.css';

function App() {
  const [query, setQuery] = useState('');

  const handleSearch = (e) => {
    e.preventDefault();
    console.log("Searching:", query);
  };

  return (
    <>
      {/* Search Bar Section */}
      <div className="w-full max-w-3xl mx-auto mb-8 px-4">
        <h1 className="text-4xl font-bold mb-6 text-center">
          Search any Chess Player
        </h1>
        
        <form onSubmit={handleSearch} className="relative">
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
    </>
  );
}

export default App;