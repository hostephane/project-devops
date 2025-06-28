import React, { useState, useEffect, useRef } from "react";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [bubbles, setBubbles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(null); // "processing", "done", "error"
  const [errorMsg, setErrorMsg] = useState(null);
  const [apiUrl, setApiUrl] = useState("https://backend-production-4bc6.up.railway.app/translate-manga");
  const [confirmation, setConfirmation] = useState(false);
  const pollingInterval = useRef(null);
  const pollingTimeout = useRef(null);

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
      clearTimeout(pollingTimeout.current);
    };
  }, []);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setBubbles([]);
    setStatus(null);
    setErrorMsg(null);
  };

  const formatApiUrl = (url) => {
    if (!url) return "https://backend-production-4bc6.up.railway.app/translate-manga";
    return url.endsWith("/translate-manga")
      ? url
      : url.replace(/\/+$/, "") + "/translate-manga";
  };

  const getBaseApiUrl = (url) => {
    if (!url) return "https://backend-production-4bc6.up.railway.app";
    return url.endsWith("/translate-manga")
      ? url.slice(0, -"/translate-manga".length)
      : url.replace(/\/+$/, "");
  };

  const pollResult = async (taskId, baseUrl) => {
    try {
      const res = await fetch(`${baseUrl}/result?id=${taskId}`);
      if (!res.ok) throw new Error("Erreur réseau");

      const data = await res.json();

      if (data.status === "done") {
        setBubbles(data.bubbles);
        setStatus("done");
        setLoading(false);
        clearInterval(pollingInterval.current);
        clearTimeout(pollingTimeout.current);
      } else if (data.status === "error") {
        setStatus("error");
        setErrorMsg(data.error || "Unknown error");
        setLoading(false);
        clearInterval(pollingInterval.current);
        clearTimeout(pollingTimeout.current);
      } else {
        setStatus("processing");
        // status processing → on attend la prochaine boucle
      }
    } catch (err) {
      console.error(err);
      setStatus("error");
      setErrorMsg("Erreur réseau pendant la récupération du résultat.");
      setLoading(false);
      clearInterval(pollingInterval.current);
      clearTimeout(pollingTimeout.current);
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

    const finalApiUrl = formatApiUrl(apiUrl);
    const baseApiUrl = getBaseApiUrl(apiUrl);
    console.log("Requête API vers :", finalApiUrl);

    try {
      const response = await fetch(finalApiUrl, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error("Erreur réseau");

      const data = await response.json();
      if (!data.task_id) throw new Error("ID de tâche manquant");

      setStatus("processing");

      // Timeout au bout de 60 secondes pour arrêter le polling (à adapter)
      pollingTimeout.current = setTimeout(() => {
        clearInterval(pollingInterval.current);
        setLoading(false);
        setStatus("error");
        setErrorMsg("Temps d’attente dépassé. Veuillez réessayer.");
      }, 60000);

      // Lance le polling toutes les 2s
      pollingInterval.current = setInterval(() => {
        pollResult(data.task_id, baseApiUrl);
      }, 2000);
    } catch (error) {
      console.error("Erreur lors de la requête:", error);
      setLoading(false);
      setStatus("error");
      setErrorMsg("Erreur côté serveur.");
    }
  };

  const handleConfirmClick = () => {
    setConfirmation(true);
    setTimeout(() => setConfirmation(false), 3000);
  };

  return (
    <div className="app-container">
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
