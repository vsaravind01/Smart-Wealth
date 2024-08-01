import axios from "axios";


export const chatAgent = async (messages) => {
    const response = await axios.post('http://localhost:8000/api/agent/chat/', {messages: messages});
    return response.data;
}