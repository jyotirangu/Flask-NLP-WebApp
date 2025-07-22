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
  LabelList
} from 'recharts';
import './Emotion.css'

const Emotion = () => {
  const [text, setText] = useState('');
  const [result, setResult] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post(
        `${import.meta.env.VITE_API_BASE_URL}/perform_emotion_detection`, 
        { text },
        { withCredentials: true }
      );
      setResult(res.data);
    } catch (err) {
      alert("Error performing emotion detection");
      console.error(err);
    }
  };

  return (
    <div className="emo">
      <h2 className="emo-h2">Emotion Detection</h2>
      <form onSubmit={handleSubmit}>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Type your text here"
          className="emo-textarea"
          rows={5}
        />
        <button className="emo-btn">Detect Emotion</button>
      </form>
      {result && (
        <div className="emo-div">
          <p><strong>Detected Emotion:</strong> {result[0]?.label}</p>
          <p><strong>Confidence:</strong> {(result[0]?.score * 100).toFixed(2)}%</p>
          <div style={{ width: '100%', height: 300, marginTop: '1rem' }}>
            <ResponsiveContainer>
              <BarChart
                data={result.map(emotion => ({
                  name: emotion.label,
                  value: +(emotion.score * 100).toFixed(2),
                }))}
                layout="vertical"
                margin={{ top: 10, right: 30, left: 40, bottom: 10 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" domain={[0, 100]} />
                <YAxis type="category" dataKey="name" />
                <Tooltip />
                <Bar dataKey="value" fill="#82ca9d" barSize={30}>
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

export default Emotion;



