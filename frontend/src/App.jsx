import React, { useState, useEffect } from "react";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [bubbles, setBubbles] = useState([]);
  const [loading, setLoading] = useState(false);

  // Générer l'URL de preview de l'image quand file change
  useEffect(() => {
    if (!file) {
      setPreviewUrl(null);
      return;
    }
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);

    // Nettoyer l'URL pour éviter les fuites mémoire
    return () => URL.revokeObjectURL(url);
  }, [file]);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setBubbles([]); // reset traductions à chaque nouvelle image
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

      if (!response.ok) throw new Error("Erreur réseau");

      const data = await response.json();
      setBubbles(data.bubbles);
    } catch (error) {
      console.error("Erreur lors de la requête:", error);
      alert("Erreur côté serveur.");
    }
    setLoading(false);
  };

  return (
    <div className="App" style={{ display: "flex", gap: "20px", padding: "20px" }}>
      {/* Partie gauche : affichage image */}
      <div style={{ flex: 1, border: "1px solid #ccc", padding: "10px" }}>
        <h2>Image chargée</h2>
        {previewUrl ? (
          <img
            src={previewUrl}
            alt="Preview"
            style={{ maxWidth: "100%", maxHeight: "80vh", objectFit: "contain" }}
          />
        ) : (
          <p>Aucune image sélectionnée</p>
        )}
        <form onSubmit={handleSubmit} style={{ marginTop: "20px" }}>
          <input type="file" accept="image/*" onChange={handleFileChange} />
          <button type="submit" disabled={loading} style={{ marginLeft: "10px" }}>
            Traduire
          </button>
        </form>
        {loading && <p>Chargement...</p>}
      </div>

      {/* Partie droite : traductions */}
      <div style={{ flex: 1, border: "1px solid #ccc", padding: "10px", overflowY: "auto", maxHeight: "90vh" }}>
        <h2>Traductions des bulles</h2>
        {bubbles.length === 0 && <p>Aucune traduction pour l'instant</p>}
        <ul style={{ listStyleType: "none", padding: 0 }}>
          {bubbles.map((bubble, index) => (
            <li key={index} style={{ marginBottom: "15px", borderBottom: "1px solid #eee", paddingBottom: "10px" }}>
              <strong>Original :</strong> {bubble.original_text} <br />
              <strong>Traduction :</strong> {bubble.translated_text} <br />
              <em>Confiance : {bubble.confidence.toFixed(2)}</em>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default App;
