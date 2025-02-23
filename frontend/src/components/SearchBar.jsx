import { Search } from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

const SearchBar = () => {
  const [query, setQuery] = useState("");
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim() !== "") {
      navigate(`/results/${query.trim()}`);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-black via-gray-900 to-black px-6">
      <div className="text-center max-w-2xl w-full">
        <h1 className="text-white text-6xl font-extrabold mb-10">
          Search a Chess Player
        </h1>

        <form
          onSubmit={handleSubmit}
          className="relative w-full flex items-center"
        >
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Try searching 'Magnus Carlsen'..."
            className="w-full px-6 py-4 pr-16 rounded-full bg-gray-800 text-white text-lg placeholder-gray-400 border border-gray-700 focus:outline-none focus:ring-4 focus:ring-blue-500 transition-shadow"
          />
          <button
            type="submit"
            className="absolute right-4 top-1/2 -translate-y-1/2 bg-blue-600 p-4 rounded-full text-white hover:bg-blue-700 transition-transform hover:scale-110"
          >
            <Search size={24} />
          </button>
        </form>
      </div>
    </div>
  );
};

export default SearchBar;