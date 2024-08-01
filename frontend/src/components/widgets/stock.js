import react from 'react';
import {useEffect, useState} from 'react';
import {getStock, getStocks} from "../../api/stocks";
import React from "react";

const StockWidget = ({stocks}) => {

    const [stockDetails, setStockDetails] = useState([]);

    useEffect(() => {
        getStocks(stocks).then((response) => {
            setStockDetails(response.data);
        });
    }, [stocks]);

    return (
        <div className="bg-white border-2 border-orange p-4 rounded-xl shadow-md w-96">
            <h1 className="text-xl text-left font-bold mb-3">Stocks</h1>
            <div className="flex-row justify-between">
                {stockDetails.map((stock) => (
                    <div className="flex justify-between">
                        <div className="text-left">
                            <h2 className="text-xl font-semibold">{stock.companyName}</h2>
                            <p className="text-sm text-gray-500">NSE: {stock.symbol}</p>
                        </div>
                        <div className="text-right">
                            <p className="text-xl font-semibold">{stock.currentPrice}</p>
                            {stock.oneYearChange > 0 ? (
                                <p className="text-green-600">{stock.oneYearChange.toFixed(2)}%</p>
                            ) : (
                                <p className="text-red-600">{stock.oneYearChange.toFixed(2)}%</p>
                            )}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

function Stock() {
    return (
        <div className="min-h-screen bg-gray-100 flex items-center justify-center">
            <StockWidget stocks={["HDFCBANK.NS", "RELIANCE.NS"]}/>
        </div>
    );
}

export default Stock;