import React from 'react';
import {useEffect, useState} from 'react';
import {getMutualFund} from "../../api/mutual_fund";


const FundWidget = ({fundName}) => {

    const [currentNAV, setCurrentNAV] = useState(0);
    const [AUM, setAUM] = useState(0);
    const [minInvestment, setMinInvestment] = useState(0);
    const [CAGR, setCAGR] = useState(0);
    const [oneYearReturn, setOneYearReturn] = useState(0);
    const [threeYearReturn, setThreeYearReturn] = useState(0);
    const [fiveYearReturn, setFiveYearReturn] = useState(0);

    // const [chartOptions, setChartOptions] = useState({});
    // const [chartSeries, setChartSeries] = useState([]);

    useEffect(() => {
        getMutualFund(fundName).then((response) => {
            console.log(response.data);
            setCurrentNAV(response.data.nav);
            setAUM(response.data.aum);
            setMinInvestment(response.data.min_investment_amount);
            setCAGR(response.data.sip_return.return3y);
            setOneYearReturn(response.data.return_stats[0].return1y);
            setThreeYearReturn(response.data.return_stats[0].return3y);
            setFiveYearReturn(response.data.return_stats[0].return5y);

            // const url = "https://api.mfapi.in/mf/" + response.data.scheme_code;
            // fetch(url)
            //     .then((response) => response.json())
            //     .then((data) => {
            //         let series = [];
            //         let labels = [];
            //         for (let i = 0; i < data.data.length; i++) {
            //             const parts = data.data[i].date.split("-");
            //             const date = new Date(parts[2], parts[1] - 1, parts[0]).toISOString();
            //             let nav = parseFloat(data.data[i].nav);
            //             series.push(nav);
            //             labels.push(date);
            //         }
            //         setChartOptions({
            //             chart: {
            //                 type: 'area',
            //             },
            //             xaxis: {
            //                 type: 'datetime',
            //                 categories: labels
            //             },
            //             series: [{
            //                 name: fundName,
            //                 data: series
            //             }]
            //         });
            //     });
        });
    }, [fundName]);


    return (
        <div className="border-2 border-orange max-w-sm mx-auto bg-white shadow-md rounded-lg">
            <div className="flex justify-start">
                <h2 className="text-xl text-left font-semibold text-black px-4 pt-4">{fundName}</h2>
            </div>
            <div className="flex flex-col px-2 pt-3">
                <div className="flex justify-between px-2">
          <span className="flex flex-col justify-end">
            <div className="text-md text-gray-700">Current NAV</div>
            <div className="text-xl font-bold text-green-600">₹{currentNAV.toFixed(2)}</div>
          </span>
                    <span className="flex flex-col justify-end">
            {oneYearReturn > 0 ? (
                <div className="text-lg font-bold text-blue-600">{oneYearReturn.toFixed(2)}%</div>
            ) : (
                <div className="text-lg text-red-600">{oneYearReturn.toFixed(2)}%</div>
            )}
                        <div className="text-sm text-gray-700">1 Year</div>
          </span>
                    <span className="flex flex-col justify-end">
            {threeYearReturn > 0 ? (
                <div className="text-lg font-bold text-blue-600">{threeYearReturn.toFixed(2)}%</div>
            ) : (
                <div className="text-lg font-bold text-red-600">{threeYearReturn.toFixed(2)}%</div>
            )}
                        <div className="text-sm text-gray-700">3 Year</div>
          </span>
                    <span className="flex flex-col justify-end">
            {fiveYearReturn > 0 ? (
                <div className="text-lg font-bold text-blue-600">{fiveYearReturn.toFixed(2)}%</div>
            ) : (
                <div className="text-lg font-bold text-red-600">{fiveYearReturn.toFixed(2)}%</div>
            )}
                        <div className="text-sm text-gray-700">5 Year</div>
          </span>
                </div>
                <div className="grid grid-cols-3 gap-2 px-1 h-max mb-4 mx-2 mt-4">
                    <div className="bg-gray-200 border-2 rounded-full h-max">
                        <span
                            className="inline-block text-xs text-gray-800 py-1 px-1">AUM - ₹{AUM.toFixed(0)} Cr</span>
                    </div>
                    <div className="bg-gray-200 border-2 rounded-full h-max">
                        <span className="inline-block text-xs text-gray-800 py-1 px-1">Min Inv - ₹{minInvestment}</span>
                    </div>
                    <div className="bg-orange-light border-solid border-2 border-orange rounded-full h-max">
                        <div className="text-xs font-bold text-orange py-1 px-1">CAGR - {CAGR.toFixed(2)}%</div>
                    </div>
                </div>
            </div>
        </div>
    );
};

function App() {
    return (
        <div className="min-h-screen bg-gray-100 flex items-center justify-center">
            <FundWidget fundName="Baroda BNP Paribas Large Cap Fund" CAGR={12} AUM={500} currentNAV={10.6}
                        minInvestment={1000}/>
        </div>
    );
}

export default App;