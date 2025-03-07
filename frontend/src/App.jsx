import { Route, BrowserRouter as Router, Routes } from "react-router-dom";
import "./App.css";
import Footer from "./components/Footer";
import Header from "./components/Header";
import Home from "./pages/Home";
import TopPlayers from "./pages/TopPlayers";
import UserStats from "./pages/UserStats";

export default function App() {
  return (
    <div className="app-container">
      <Router>
        <Header />
        <main className="content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/top-players" element={<TopPlayers />} />
            <Route path="/:username" element={<UserStats />} />
          </Routes>
        </main>
        <Footer />
      </Router>
    </div>
  );
}