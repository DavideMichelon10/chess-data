import EntryList from './components/EntryList';
import Footer from './components/Footer';
import Header from './components/Header';
import SearchBar from "./components/SearchBar";
import './index.css';
export default function App(){
  return (

    <>
      <Header/>
      <SearchBar/>
      <EntryList/>
      <Footer/>
    </>
  )
}