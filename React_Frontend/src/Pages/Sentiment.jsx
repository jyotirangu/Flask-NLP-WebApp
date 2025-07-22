import { useState } from 'react';
import axios from 'axios';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  LabelList
} from 'recharts';
import './Sentiment.css'

const Sentiment = () => {
  const [text, setText] = useState('');
  const [result, setResult] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post(`${import.meta.env.VITE_API_BASE_URL}/perform_sentiment_analysis`, 
        { text },
        { withCredentials: true }
      );
      setResult(res.data);
    } catch (err) {
      alert("Error performing sentiment analysis");
      console.error(err);
    }
  };

  const chartData = result
    ? [
        { name: 'Polarity', value: result.polarity },
        { name: 'Subjectivity', value: result.subjectivity },
      ]
    : [];

  return (
    <div className="senti">
      <h2 className="senti-h2">Sentiment Analysis</h2>
      <form onSubmit={handleSubmit}>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Type your text here"
          className="senti-textarea"
          rows={5}
        />
        <button className="senti-btn">Analyze Sentiment</button>
      </form>

      {result && (
        <div className="senti-div">
          <p>Polarity: {result.polarity}</p>
          <p>Subjectivity: {result.subjectivity}</p>

          <div className="senti-graph" style={{ width: '100%', height: 300, marginTop: '1rem' }}>
            <ResponsiveContainer>
              <BarChart
                data={chartData}
                layout="vertical"
                margin={{ top: 10, right: 30, left: 40, bottom: 10 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" domain={[-1, 1]} />
                <YAxis type="category" dataKey="name" />
                <Tooltip />
                <Legend />
                <Bar dataKey="value" fill="#8884d8" barSize={30}>
                  <LabelList dataKey="value" position="right" />
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

        </div>
      )}
    </div>
  );
};

export default Sentiment;
