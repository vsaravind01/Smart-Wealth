import axios from 'axios';

const baseUrl = 'http://localhost:8000/api/stocks';

export const getStocks = async (stocks) => {
    console.log(stocks)
    const response = await axios.get(`${baseUrl}/?stocks=${stocks.join(',')}`);
    return response.data;
}

export const getStock = async (symbol) => {
    const response = await axios.get(`${baseUrl}/${symbol}`);
    return response.data;
}