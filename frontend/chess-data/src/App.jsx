import Entry from './components/Entry';
import Footer from './components/Footer';
import Header from './components/Header';
import SearchBar from "./components/SearchBar";
import './index.css';
export default function App(){
  return (

    <>
      <Header/>
      <SearchBar/>
      <Entry/>
      <Footer/>
    </>
  )
}