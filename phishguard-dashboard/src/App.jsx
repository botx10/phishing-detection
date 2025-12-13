import { useState } from "react";

export default function App() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  const [error, setError] = useState(null);

  const API_URL = import.meta.env.VITE_API_URL;

  const handleScan = async () => {
    if (!url.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Scan failed");

      setResult(data);

      setHistory((prev) => [
        {
          url,
          prediction: data.prediction,
          confidence: data.confidence,
          time: new Date().toLocaleTimeString(),
        },
        ...prev,
      ]);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const isPhishing = result?.prediction === "Phishing";
  const confidencePct = result?.confidence
    ? Math.round(result.confidence * 100)
    : 0;

  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-neutral-900 to-black text-neutral-200 p-6">
      {/* Header */}
      <header className="mb-6">
        <h1 className="text-3xl font-bold">🔐 PhishGuard </h1>
        <p className="text-sm text-neutral-400">
          Real-time phishing detection dashboard
        </p>
      </header>

      {/* Main Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Scan Panel */}
        <div className="bg-neutral-900/80 border border-neutral-800 rounded-xl p-6">
          <h2 className="font-semibold mb-3">URL Scanner</h2>

          <input
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://example.com"
            className="w-full px-4 py-3 rounded-lg bg-neutral-800 border border-neutral-700 focus:ring-2 focus:ring-blue-600 outline-none"
          />

          <button
            onClick={handleScan}
            disabled={loading}
            className="w-full mt-4 py-3 rounded-lg bg-blue-600 hover:bg-blue-700 transition disabled:opacity-50"
          >
            {loading ? "Scanning..." : "Scan URL"}
          </button>

          <button
            onClick={() => setShowHistory(true)}
            className="w-full mt-3 py-2 rounded-lg bg-neutral-800 border border-neutral-700 hover:bg-neutral-700"
          >
            📜 View Scan History
          </button>

          {error && (
            <p className="mt-3 text-sm text-red-400">⚠ {error}</p>
          )}
        </div>

        {/* Result Panel */}
        <div className="md:col-span-2 bg-neutral-900/80 border border-neutral-800 rounded-xl p-6">
          <h2 className="font-semibold mb-4">Scan Result</h2>

          {!result && (
            <p className="text-neutral-500 text-sm">
              No scan performed yet.
            </p>
          )}

          {result && (
            <>
              {/* Status */}
              <div
                className={`inline-block px-4 py-2 rounded-full font-semibold text-sm mb-4 ${
                  isPhishing
                    ? "bg-red-500/20 text-red-400"
                    : "bg-green-500/20 text-green-400"
                }`}
              >
                {isPhishing ? "🚨 PHISHING DETECTED" : "✅ LEGITIMATE URL"}
              </div>

              {/* Confidence */}
              <p className="text-sm mb-2 text-neutral-400">
                Confidence: {confidencePct}%
              </p>
              <div className="w-full h-2 bg-neutral-800 rounded-full mb-4">
                <div
                  className={`h-2 rounded-full ${
                    isPhishing ? "bg-red-500" : "bg-green-500"
                  }`}
                  style={{ width: `${confidencePct}%` }}
                />
              </div>

              {/* Contributions */}
              {result.top_contributions?.length > 0 && (
                <div>
                  <h3 className="text-sm font-semibold mb-2">
                    Top Risk Indicators
                  </h3>
                  <ul className="space-y-2 text-sm">
                    {result.top_contributions.map((item, i) => (
                      <li
                        key={i}
                        className="flex justify-between bg-neutral-800 px-3 py-2 rounded-lg"
                      >
                        <span>{item.feature}</span>
                        <span className="text-neutral-400">
                          {(item.contribution * 100).toFixed(2)}%
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* History Modal */}
      {showHistory && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50">
          <div className="bg-neutral-900 border border-neutral-800 rounded-xl w-full max-w-lg p-6">
            <h2 className="font-semibold mb-4">Scan History</h2>

            {history.length === 0 && (
              <p className="text-sm text-neutral-500">
                No scans yet.
              </p>
            )}

            <ul className="space-y-2 max-h-64 overflow-y-auto text-sm">
              {history.map((h, i) => (
                <li
                  key={i}
                  className="flex justify-between bg-neutral-800 px-3 py-2 rounded-lg"
                >
                  <span className="truncate w-2/3">{h.url}</span>
                  <span
                    className={
                      h.prediction === "Phishing"
                        ? "text-red-400"
                        : "text-green-400"
                    }
                  >
                    {h.prediction}
                  </span>
                </li>
              ))}
            </ul>

            <button
              onClick={() => setShowHistory(false)}
              className="mt-4 w-full py-2 rounded-lg bg-neutral-800 hover:bg-neutral-700"
            >
              Close
            </button>
          </div>
        </div>
      )}

      <footer className="mt-8 text-xs text-neutral-500 text-center">
        © PhishGuard — Developed by Aryaman Menon
      </footer>
    </div>
  );
}
