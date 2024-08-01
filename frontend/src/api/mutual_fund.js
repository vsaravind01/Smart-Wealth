import axios from "axios";

const baseUrl = "http://localhost:8000/api/mutual-funds";


export const getMutualFunds = async (mutual_funds) => {
    const response = await axios.get(`${baseUrl}/?mutual_funds=${mutual_funds.join(',')}`);
    return response.data;
}


export const getMutualFund = async (name) => {
    const response = await axios.get(`${baseUrl}/${name}`);
    return response.data;
}