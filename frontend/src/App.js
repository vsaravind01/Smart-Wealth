import './App.css';
import MutualFund from "./components/widgets/mutual_fund";
import StockWidget from "./components/widgets/stock";
import ChatArea from "./components/widgets/chat_area";

function App() {
    return (
        <div className="min-h-screen flex flex-col">
            <ChatArea/>
            <MutualFund/>
            <StockWidget/>
        </div>
    );
}

export default App;
