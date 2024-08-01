import react from 'react';
import {useMemo} from 'react';
import ReactMarkdown from 'react-markdown'
import remarkBreaks from 'remark-breaks';


export const ChatBubble = ({message, sender}) => {
    console.log(message)
    const modifiedText = useMemo(() => {
        const lines = message.split('\n');

        return lines.map((line, index) => {
            // Check if the line is part of a list
            const isListItem = /^\s*[*\-+]\s+|^\s*\d+\.\s+/.test(line);
            const isNextLineListItem = index < lines.length - 1 && /^\s*[*\-+]\s+|^\s*\d+\.\s+/.test(lines[index + 1]);

            if (isListItem || isNextLineListItem)
                return line;

            if (line.trim() === '\\')
                return line.replace('\\', '&nbsp;\n');

            return line + '&nbsp;\n';
        }).join('\n');
    }, [message]);


    return (
        <div>
            {sender === "bot" ? (
                <div className="flex">
                    <div
                        className="bg-orange max-w-2xl text-white p-2 rounded-lg">
                        <ReactMarkdown remarkPlugins={[remarkBreaks]}>
                            {message}
                        </ReactMarkdown>
                    </div>
                </div>
            ) : (
                <div className="flex justify-end">
                    <div className="bg-gray-300 p-2 max-w-2xl rounded-lg">
                        <ReactMarkdown remarkPlugins={[remarkBreaks]}>{modifiedText}</ReactMarkdown>
                    </div>
                </div>
            )}
        </div>
    );
};
