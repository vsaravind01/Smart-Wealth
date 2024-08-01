/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "./src/**/*.{js,jsx,ts,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                "orange-light": "rgba(242, 94, 25, 0.4)",
                "orange": "#f25e19",
            }
        },
    },
    plugins: [],
}