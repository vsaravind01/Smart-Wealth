import {useEffect, useState} from 'react';
import {ChatBubble} from "./chat_bubble";
import {FaArrowUp} from "react-icons/fa";
import mainLogo from "../../logo.png";
import {chatAgent} from "../../api/agent";


const dummyMessages = [
    {
        sender: "bot",
        message: "Hello! How can I help you today?"
    },
    {
        sender: "user",
        message: "I want to know about mutual funds"
    },
    {
        sender: "bot",
        message: "Sure! Which mutual fund are you interested in?"
    },
    {
        sender: "user",
        message: "I want to know about HDFC Top 100 Fund"
    },
    {
        sender: "bot",
        message: "HDFC Top 100 Fund is an open-ended equity scheme investing across large cap stocks. The scheme was launched on 11 Feb 1996 and is managed by Prashant Jain. The scheme has an AUM of ₹ 17,635 Cr and a minimum investment amount of ₹ 500. The scheme has given a CAGR return of 15.6% since its launch. The scheme has given a return of 18.5% in the last 1 year, 13.5% in the last 3 years and 13.3% in the last 5 years."
    }
];


const ChatArea = () => {

    const [messages, setMessages] = useState([]);
    const [message, setMessage] = useState("");
    const [loading, setLoading] = useState(false);

    const sendMessage = async (message) => {
        setLoading(true)
        setMessages([...messages, {sender: "user", "text": message}])
        const response = await chatAgent([...messages, {sender: "user", "text": message}]);
        setMessages(response.messages);
        setLoading(false);
    }

    return (
        <div className="w-full h-full bg-gray-100 flex items-center justify-center">
            <div className="bg-white border-2 border-orange m-10 p-10 rounded-xl w-full flex flex-col"
                 style={{height: 'calc(100vh - 100px)'}}>
                <div className="sticky top-0 bg-white z-10 pb-2">
                    <img src={mainLogo} alt="Smart Wealth"/>
                </div>

                <div className="flex flex-col gap-2 mb-4 overflow-y-auto flex-grow">
                    {messages.map((message, index) => (
                        <ChatBubble key={index} message={message.text} sender={message.sender}/>
                    ))}
                </div>
                {loading && <div className="flex justify-center items-center m-5">
                    <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-gray-900"/>
                </div>
                }
                <div className="flex gap-2 align-middle">
                    <input value={message} onChange={(event) => {
                        setMessage(event.target.value);
                    }} type="text" className="w-full border-2 border-gray-300 p-2 rounded-lg"
                           placeholder="Type your message here..."/>
                    <button className="flex justify-center align-bottom bg-gray-300 text-white pt-3.5 rounded-full"
                            style={{width: '3em'}} onClick={(event) => {
                        sendMessage(message);
                        setMessage("");
                    }}>
                        <FaArrowUp color="black"/>
                    </button>
                </div>
            </div>
        </div>
    );
}

export default ChatArea;