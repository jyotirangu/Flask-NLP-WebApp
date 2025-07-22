import { useState } from 'react';
import axios from 'axios';
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import './NER.css'

const API_URL = import.meta.env.VITE_API_BASE_URL; // ✅ This was missing

const NER = () => {
  const [text, setText] = useState('');
  const [entities, setEntities] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const COLORS = [
    "#8884d8",
    "#82ca9d",
    "#ffc658",
    "#ff7f50",
    "#a4de6c",
    "#ff69b4",
    "#00bcd4",
  ];

  const getEntityDistribution = (entities) => {
    const counts = {};
    entities.forEach(({ category }) => {
      counts[category] = (counts[category] || 0) + 1;
    });

    return Object.entries(counts).map(([category, count]) => ({
      name: category,
      value: count,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!text.trim()) return;

    setLoading(true);
    setError("");
    setEntities([]);

    try {
      const res = await axios.post(
        `${API_URL}/perform_ner`,
        { ner_text: text },
        { 
            headers: {
                'Content-Type': 'application/json'
            },
            withCredentials: true,
         } // ✅ Needed to send cookies
      );
      console.log(res.data); // <- now safe
      setEntities(res.data);
    } catch (err) {
      console.error("NER error:", err);
      alert("Error performing NER");
    } finally {
      setLoading(false);
    }
  };

  const pieData = getEntityDistribution(entities);

  return (
    <div className="ner">
      <h2 className="ner-h2">Named Entity Recognition</h2>
      <form onSubmit={handleSubmit}>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)} rows={5}
          placeholder="Type your text here"
          className="ner-textarea"
        />
        <button className="ner-btn" disabled={loading}>
          {loading ? "Analyzing..." : "Perform NER"}
        </button>
      </form>

      {entities.length > 0 && (
        <>
      <div className="ner-div">
        {entities.map((item, index) => (
          <p key={index}>{item.entity} → {item.category}</p>
        ))}
      </div>

      {/* Pie Chart Section */}
          <div className="ner-chart">
            <h3>Entity Category Distribution</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={pieData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  label
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </>
      )}

    </div>
  );
};

export default NER;
