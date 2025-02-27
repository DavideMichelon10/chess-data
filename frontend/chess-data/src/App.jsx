import { Route, BrowserRouter as Router, Routes } from "react-router-dom";
import Footer from "./components/Footer";
import Header from "./components/Header";
import Home from "./pages/Home";
import TopPlayers from "./pages/TopPlayers";

import "./App.css";

export default function App() {
  return (
    <div className="app-container">
      <Router>
        <Header />
        <main className="content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/top-players" element={<TopPlayers />} />
          </Routes>
        </main>
        <Footer />
      </Router>
    </div>
  );
}