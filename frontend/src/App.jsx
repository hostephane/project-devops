import React, { useState } from "react";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [bubbles, setBubbles] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    setLoading(true);
    try {
      const response = await fetch("http://localhost:8000/translate-manga", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      setBubbles(data.bubbles);
    } catch (error) {
      console.error("Erreur lors de la requête:", error);
      alert("Erreur côté serveur.");
    }
    setLoading(false);
  };

  return (
    <div className="App">
      <h1>Traduction Manga</h1>

      <form onSubmit={handleSubmit}>
        <input type="file" accept="image/*" onChange={handleFileChange} />
        <button type="submit">Traduire</button>
      </form>

      {loading && <p>Chargement...</p>}

      {bubbles.length > 0 && (
        <div>
          <h2>Résultats :</h2>
          <ul>
            {bubbles.map((bubble, index) => (
              <li key={index}>
                <strong>Original :</strong> {bubble.original_text} <br />
                <strong>Traduction :</strong> {bubble.translated_text} <br />
                <em>Confiance : {bubble.confidence.toFixed(2)}</em>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default App;
