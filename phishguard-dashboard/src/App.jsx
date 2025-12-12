import { useState } from "react";
import { Shield, Loader2, CheckCircle, XCircle } from "lucide-react";

export default function App() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const API_URL = import.meta.env.VITE_API_URL || "/predict";

  async function scanUrl() {
    if (!url) return;

    setLoading(true);
    setResult(null);

    try {
      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });

      const data = await res.json();
      setResult(data);
    } catch (e) {
      setResult({ error: "Failed to connect to API." });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen px-6 py-10 flex flex-col items-center">
      {/* HEADER */}
      <div className="flex items-center gap-3 mb-10">
        <div className="bg-blue-600/20 p-3 rounded-xl">
          <Shield size={32} className="text-blue-400" />
        </div>
        <div>
          <h1 className="text-3xl font-bold">PhishGuard</h1>
          <p className="text-neutral-400">Real-time URL safety scanner</p>
        </div>
      </div>

      {/* MAIN CARD */}
      <div className="w-full max-w-2xl bg-neutral-900 p-8 rounded-2xl border border-neutral-800 shadow-xl">
        <label className="text-neutral-300 font-medium">Enter URL</label>
        <div className="flex items-center gap-2 mt-2">
          <input
            type="text"
            className="w-full p-3 rounded-lg bg-neutral-800 border border-neutral-700 text-neutral-100"
            placeholder="https://example.com/login"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
          />
          <button
            onClick={scanUrl}
            className="px-5 py-3 bg-blue-600 hover:bg-blue-500 rounded-lg font-semibold"
            disabled={loading}
          >
            {loading ? <Loader2 className="animate-spin" /> : "Scan"}
          </button>
        </div>

        {/* RESULT BOX */}
        <div className="mt-6">
          {!result && !loading && (
            <p className="text-neutral-500 text-sm">Scan a URL to see results.</p>
          )}

          {loading && (
            <div className="flex items-center justify-center py-6">
              <Loader2 size={30} className="animate-spin text-blue-400" />
            </div>
          )}

          {result && (
            <div className="mt-4 p-4 bg-neutral-800 rounded-xl border border-neutral-700">
              {result.error ? (
                <p className="text-red-400">{result.error}</p>
              ) : (
                <>
                  <div className="flex items-center gap-2 text-lg font-semibold">
                    {result.prediction === "Phishing" ? (
                      <XCircle className="text-red-400" />
                    ) : (
                      <CheckCircle className="text-green-400" />
                    )}
                    {result.prediction}
                  </div>
                  <p className="text-neutral-400 text-sm mt-1">
                    Confidence: {result.confidence == null ? "N/A" : (result.confidence * 100).toFixed(1) + "%"}
                  </p>

                  <pre className="mt-4 p-4 bg-neutral-900 text-neutral-300 rounded-lg overflow-auto text-sm max-h-60">
{JSON.stringify(result, null, 2)}
                  </pre>
                </>
              )}
            </div>
          )}
        </div>
      </div>

      <footer className="mt-12 text-neutral-600 text-sm">
        © PhishGuard — Developed by Aryaman Menon
      </footer>
    </div>
  );
}
