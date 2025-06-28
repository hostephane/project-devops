import React, { useState, useEffect } from "react";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [bubbles, setBubbles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [apiUrl, setApiUrl] = useState("http://localhost:8000/translate-manga");
  const [confirmation, setConfirmation] = useState(false);

  useEffect(() => {
    if (!file) {
      setPreviewUrl(null);
      return;
    }
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setBubbles([]);
  };

  const formatApiUrl = (url) => {
    if (!url) return "http://localhost:8000/translate-manga";
    // Si l'URL ne se termine pas par /translate-manga, on l'ajoute
    return url.endsWith("/translate-manga") ? url : url.replace(/\/+$/, "") + "/translate-manga";
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    const finalApiUrl = formatApiUrl(apiUrl);
    console.log("Requête API vers :", finalApiUrl);

    setLoading(true);
    try {
      const response = await fetch(finalApiUrl, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error("Erreur réseau");

      const data = await response.json();
      setBubbles(data.bubbles);
    } catch (error) {
      console.error("Erreur lors de la requête:", error);
      alert("Erreur côté serveur.");
    }
    setLoading(false);
  };

  const handleConfirmClick = () => {
    setConfirmation(true);
    setTimeout(() => setConfirmation(false), 3000); // disparaît au bout de 3 secondes
  };

  return (
    <div className="app-container">
      {/* Champ API URL avec bouton */}
      <div
        className="api-url-input"
        style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "10px" }}
      >
        <input
          type="text"
          value={apiUrl}
          onChange={(e) => setApiUrl(e.target.value)}
          title="Modifier l'URL de l'API"
          placeholder="URL API (optionnel)"
          style={{ flexGrow: 1, padding: "6px 8px" }}
        />
        <button onClick={handleConfirmClick} style={{ padding: "6px 12px", cursor: "pointer" }}>
          Confirmer
        </button>
      </div>
      {confirmation && (
        <div style={{ color: "green", marginBottom: "10px" }}>URL de l'API mise à jour !</div>
      )}

      <div className="main-content">
        {/* Partie gauche : image */}
        <div className="left-panel">
          <h2>Image chargée</h2>
          {previewUrl ? (
            <img src={previewUrl} alt="Preview" className="preview-image" />
          ) : (
            <p className="placeholder">Aucune image sélectionnée</p>
          )}

          <form onSubmit={handleSubmit} className="upload-form">
            <input type="file" accept="image/*" onChange={handleFileChange} />
            <button type="submit" disabled={loading}>
              Traduire
            </button>
          </form>

          {loading && <p className="loading-text">Chargement...</p>}
        </div>

        {/* Partie droite : traductions */}
        <div className="right-panel">
          <h2>Traductions des bulles</h2>
          {bubbles.length === 0 ? (
            <p className="placeholder">Aucune traduction pour l'instant</p>
          ) : (
            <ul className="bubble-list">
              {bubbles.map((bubble, index) => (
                <li key={index} className="bubble-card">
                  <strong>Original :</strong> {bubble.original_text} <br />
                  <strong>Traduction :</strong> {bubble.translated_text} <br />
                  <em>Confiance : {bubble.confidence.toFixed(2)}</em>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
