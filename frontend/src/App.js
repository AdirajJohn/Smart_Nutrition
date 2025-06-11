import React, { useState, useEffect } from "react";
import './App.css';

function App() {
  const [prompt, setPrompt] = useState(""); //stores the user input from the text box
  const [data, setData] = useState(null); //stores json output from LLM API
  const [dfData, setDfData] = useState([]); //stores the dataframe from backend endpoint
  const [metadata, setMetadata] = useState([]);
  const [expandedSections, setExpandedSections] = useState({});

  useEffect(() => {
    fetch("/metadata.json")
      .then(res => res.json())
      .then(data => {
        const sortedMetadata = data.sort((a, b) => a.priority - b.priority);
        console.log("Metadata:", sortedMetadata); // ✅ Log here
        setMetadata(sortedMetadata);
      });
  }, []);

  const toggleSection = (id) => {
    setExpandedSections(prev => ({
      ...prev,
      [id]: !prev[id],
    }));
  };

  const handleSubmit = async () => {
    try {
      const res1 = await fetch('http://143.110.247.163:8000/generate-data', {
        method: 'POST',
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_input: prompt }),
      });

      const result = await res1.json();
      setData(result);
      console.log("LLM JSON", result); // <-- Log here

      const res2 = await fetch("http://143.110.247.163:8000/data", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ input_json: result }),
      });

      const dfResult = await res2.json();
      setDfData(dfResult);
      console.log("DataFrame result", dfResult); // <-- Log here
      console.log("Sample row:", dfResult[0]);   // <-- Optional row preview
    } catch (error) {
      console.error("Error:", error);
    }
  };

  const renderSection = (section) => {
    const isOpen = expandedSections[section.id];
    return (
      <div key={section.id} className="section-container">
        <div className="section-header" onClick={() => toggleSection(section.id)}>
          <h3>{section.name}</h3>
          <span>{isOpen ? "▲" : "▼"}</span>
        </div>
        {isOpen && (
          <div className="custom-table-wrapper">
            <table className="custom-table">
              <thead>
                <tr>
                  <th>Name</th>
                  {section.feature.map((key) => <th key={key}>{key}</th>)}
                </tr>
              </thead>
              <tbody>
                {dfData.map((row, idx) => (
                  <tr key={idx}>
                    <td>{row.name}</td>
                    {section.feature.map((key) => (
                      <td key={key}>
                        {row[key] !== undefined ? parseFloat(row[key]).toFixed(2) : "-"}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    );
  };

  return (
    <div style={{ padding: "1rem" }}>
        <h3 className="page-title">Smart Nutrition</h3>
        <h3>Enter the ingredients details</h3>
      <textarea
        rows={4}
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder="Describe the ingredients..."
      />
      <br />
      <button onClick={handleSubmit}>Submit</button>
      <h3>API Output</h3>
      <pre>{JSON.stringify(data, null, 2)}</pre>
      {dfData.length > 0 && (
        <div className="section-wrapper">
          {metadata.map(renderSection)}
        </div>
      )}
    </div>
  );
}

export default App;