import { Route, BrowserRouter as Router, Routes } from "react-router-dom";
import SearchBar from "./components/SearchBar";
import ResultsPage from "./pages/ResultsPage";

function App() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-black via-gray-900 to-black">
      <Router>
        <Routes>
          <Route path="/" element={<SearchBar />} />
          <Route path="/results/:player_name" element={<ResultsPage />} />
        </Routes>
      </Router>
    </div>
  );
}

export default App;