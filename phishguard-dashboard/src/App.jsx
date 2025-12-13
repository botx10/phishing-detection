import React, { useState } from "react";

export default function App() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const API_URL = import.meta.env.VITE_API_URL;

  async function handleScan() {
    if (!url.trim()) return;

    setLoading(true);
    setResult(null);

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });

      const data = await response.json();
      setResult(data);
    } catch (error) {
      setResult({ error: "API request failed", details: error.message });
    }

    setLoading(false);
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4">
      <div className="w-full max-w-lg bg-neutral-900 border border-neutral-800 rounded-2xl p-8 shadow-xl">
        <h1 className="text-3xl font-semibold text-center mb-6">
          🔐 PhishGuard Scanner
        </h1>

        <input
          type="text"
          placeholder="Enter URL to scan..."
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          className="w-full px-4 py-3 rounded-xl bg-neutral-800 border border-neutral-700 text-neutral-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />

        <button
          onClick={handleScan}
          disabled={loading}
          className="w-full mt-4 py-3 rounded-xl bg-blue-600 hover:bg-blue-700 transition disabled:bg-neutral-700"
        >
          {loading ? "Scanning..." : "Scan"}
        </button>

        {loading && (
          <div className="flex items-center justify-center mt-4">
            <div className="h-6 w-6 animate-spin rounded-full border-2 border-neutral-400 border-t-transparent"></div>
          </div>
        )}

        {result && (
          <div className="mt-6 p-4 bg-neutral-800 rounded-xl border border-neutral-700">
            <h2 className="text-lg font-semibold mb-2">Prediction Result</h2>

            {"prediction" in result && (
              <p className="text-blue-400 text-lg">
                🧠 Prediction: <b>{result.prediction}</b>
              </p>
            )}

            {"confidence" in result && (
              <p className="text-green-400 mt-1">
                🎯 Confidence: <b>{result.confidence}%</b>
              </p>
            )}

            <pre className="mt-4 p-3 bg-neutral-900 rounded-lg text-sm overflow-x-auto border border-neutral-700">
{JSON.stringify(result, null, 2)}
            </pre>
          </div>
        )}
      </div>

      <footer className="mt-6 text-neutral-500 text-sm">
        © PhishGuard — Developed by <b>Aryaman Menon</b>
      </footer>
    </div>
  );
}
