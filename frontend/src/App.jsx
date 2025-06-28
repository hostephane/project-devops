import React, { useState, useEffect, useRef } from "react";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [bubbles, setBubbles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(null); // "processing", "done", "error"
  const [errorMsg, setErrorMsg] = useState(null);
  const pollingInterval = useRef(null);

  useEffect(() => {
    if (!file) {
      setPreviewUrl(null);
      return;
    }
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);

  useEffect(() => {
    // Nettoyer polling si on quitte le composant
    return () => {
      clearInterval(pollingInterval.current);
    };
  }, []);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setBubbles([]);
    setStatus(null);
    setErrorMsg(null);
  };

  const pollResult = async (taskId) => {
    const baseApiUrl = "https://backend-production-4bc6.up.railway.app";
    try {
      console.log(`Polling /result?id=${taskId} ...`);
      const res = await fetch(`${baseApiUrl}/result?id=${taskId}`);

      if (!res.ok) throw new Error("Erreur réseau");

      const contentType = res.headers.get("content-type") || "";
      if (!contentType.includes("application/json")) {
        throw new Error("Réponse non JSON reçue");
      }

      const data = await res.json();

      if (data.status === "done") {
        setBubbles(data.bubbles);
        setStatus("done");
        setLoading(false);
        clearInterval(pollingInterval.current); // stop polling
      } else if (data.status === "error") {
        setStatus("error");
        setErrorMsg(data.error || "Erreur inconnue");
        setLoading(false);
        clearInterval(pollingInterval.current); // stop polling
      } else {
        // Toujours processing, on continue à poller
        setStatus("processing");
      }
    } catch (err) {
      console.error(err);
      setStatus("error");
      setErrorMsg("Erreur lors du polling.");
      setLoading(false);
      clearInterval(pollingInterval.current);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    setBubbles([]);
    setStatus(null);
    setErrorMsg(null);

    const formData = new FormData();
    formData.append("file", file);

    const baseApiUrl = "https://backend-production-4bc6.up.railway.app";

    try {
      const response = await fetch(`${baseApiUrl}/translate-manga`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error("Erreur réseau");

      const data = await response.json();
      if (!data.task_id) throw new Error("ID de tâche manquant");

      console.log("Démarrage du polling avec task_id:", data.task_id);
      setStatus("processing");

      clearInterval(pollingInterval.current);
      pollingInterval.current = setInterval(() => {
        pollResult(data.task_id);
      }, 10000); // toutes les 10 secondes
    } catch (error) {
      console.error("Erreur lors de la requête:", error);
      setLoading(false);
      setStatus("error");
      setErrorMsg("Erreur côté serveur.");
    }
  };

  return (
    <div className="app-container">
      <div className="main-content">
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
          {status === "processing" && <p>Traitement en cours...</p>}
          {status === "error" && <p style={{ color: "red" }}>Erreur : {errorMsg}</p>}
        </div>

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
