import playersData from "../../data";
import Entry from "./Entry";
import "./Entry.css";

console.log(playersData)
export default function EntryList(){
    const playerElements = playersData.map((player)=> {
        return  <Entry
            key={player.name} 
            {...player}
            />
    })
    return (
        <>
            <div className="user-card-container">
                <div className="user-list">
                    {playerElements}
                </div>
            </div>
        </> 
    )
}