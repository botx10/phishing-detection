import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

export default function App() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  const [error, setError] = useState(null);

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2,
      },
    },
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: { y: 0, opacity: 1, transition: { duration: 0.5 } },
  };

  const cardVariants = {
    hidden: { scale: 0.9, opacity: 0 },
    visible: { scale: 1, opacity: 1, transition: { duration: 0.5 } },
  };

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
    <motion.div
      initial="hidden"
      animate="visible"
      variants={containerVariants}
      className="min-h-screen relative bg-gradient-to-br from-black via-neutral-900 to-black text-neutral-200 p-6 overflow-hidden"
    >
      {/* Cyber Background Animation */}
      <div className="absolute inset-0 pointer-events-none">
        {Array.from({ length: 50 }).map((_, i) => (
          <motion.div
            key={i}
            className="absolute text-green-500/20 text-xs font-mono"
            initial={{ y: -20, x: Math.random() * 100 + '%' }}
            animate={{ y: '120vh' }}
            transition={{
              duration: Math.random() * 8 + 4,
              repeat: Infinity,
              delay: Math.random() * 10,
              ease: "linear"
            }}
          >
            {Math.random() > 0.5 ? '1' : '0'}
          </motion.div>
        ))}
      </div>

      {/* Scanning Line */}
      <motion.div
        className="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-transparent via-green-500/30 to-transparent"
        initial={{ y: -10 }}
        animate={{ y: '110vh' }}
        transition={{ duration: 4, repeat: Infinity, ease: "linear", delay: 2 }}
      />

      {/* Floating Cyber Elements */}
      <motion.div
        className="absolute top-20 right-20 text-4xl opacity-20"
        animate={{
          rotate: 360,
          scale: [1, 1.2, 1]
        }}
        transition={{
          rotate: { duration: 10, repeat: Infinity, ease: "linear" },
          scale: { duration: 3, repeat: Infinity }
        }}
      >
        ⚙️
      </motion.div>
      <motion.div
        className="absolute bottom-40 left-20 text-3xl opacity-15"
        animate={{
          y: [0, -20, 0],
          rotate: [0, 180, 360]
        }}
        transition={{
          duration: 6,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      >
        🔧
      </motion.div>

      <motion.header variants={itemVariants} className="mb-6 relative z-10">
        <motion.h1
          className="text-3xl font-bold flex items-center gap-2"
          animate={{
            x: [0, -2, 2, -1, 1, 0],
            textShadow: [
              "0 0 0px #00ff00",
              "0 0 10px #00ff00",
              "0 0 0px #00ff00"
            ]
          }}
          transition={{
            duration: 0.3,
            repeat: Infinity,
            repeatDelay: 5,
            ease: "easeInOut"
          }}
        >
          <motion.span
            animate={{
              rotate: [0, 360],
              scale: [1, 1.2, 1],
              color: ["#ffffff", "#00ff00", "#ffffff"]
            }}
            transition={{
              rotate: { duration: 2, repeat: Infinity, ease: "linear" },
              scale: { duration: 1, repeat: Infinity, repeatDelay: 1 },
              color: { duration: 2, repeat: Infinity }
            }}
            className="text-4xl"
          >
            🔐
          </motion.span>
          PhishGuard
        </motion.h1>
        <p className="text-sm text-neutral-400">
          Real-time phishing detection dashboard
        </p>
      </motion.header>

      {/* Navigation */}
      <motion.nav variants={itemVariants} className="mb-12">
        <div className="flex justify-center space-x-8">
          <a href="#about" className="text-neutral-300 hover:text-blue-400 transition-colors">About</a>
          <a href="#features" className="text-neutral-300 hover:text-blue-400 transition-colors">Features</a>
          <a href="#how-it-works" className="text-neutral-300 hover:text-blue-400 transition-colors">How It Works</a>
          <a href="#scanner" className="text-neutral-300 hover:text-blue-400 transition-colors">Scanner</a>
        </div>
      </motion.nav>

      {/* About Section */}
      <motion.section id="about" variants={itemVariants} className="mb-12 text-center">
        <div className="flex justify-center items-center gap-4 mb-4">
          <motion.div
            className="text-6xl"
            animate={{
              rotate: [0, 5, -5, 0],
              scale: [1, 1.05, 1]
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: "easeInOut"
            }}
          >
            🤖
          </motion.div>
          <motion.div
            animate={{
              opacity: [1, 0, 1],
              scale: [1, 0.8, 1]
            }}
            transition={{
              duration: 0.3,
              repeat: Infinity,
              repeatDelay: 2
            }}
            className="text-4xl"
          >
            👁️
          </motion.div>
          <motion.div
            animate={{
              opacity: [1, 0, 1],
              scale: [1, 0.8, 1]
            }}
            transition={{
              duration: 0.3,
              repeat: Infinity,
              repeatDelay: 2.1
            }}
            className="text-4xl"
          >
            👁️
          </motion.div>
        </div>
        <h2 className="text-2xl font-bold mb-4">About PhishGuard</h2>
        <p className="text-neutral-400 max-w-2xl mx-auto leading-relaxed">
          PhishGuard is an advanced AI-powered phishing detection system designed to protect users from malicious websites.
          Leveraging cutting-edge machine learning algorithms, it analyzes URLs in real-time to identify potential phishing threats
          with high accuracy and speed. Built for security professionals and everyday users alike.
        </p>
      </motion.section>

      {/* Features Section */}
      <motion.section id="features" variants={itemVariants} className="mb-12">
        <h2 className="text-2xl font-bold mb-6 text-center">Key Features</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <motion.div
            variants={cardVariants}
            whileHover={{ y: -5, boxShadow: "0 10px 25px rgba(0,0,0,0.3)" }}
            className="bg-neutral-900/80 border border-neutral-800 rounded-xl p-6 text-center"
          >
            <motion.div
              className="text-4xl mb-4"
              animate={{ scale: [1, 1.1, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              🛡️
            </motion.div>
            <h3 className="font-semibold mb-2">Real-Time Detection</h3>
            <p className="text-sm text-neutral-400">
              Instant analysis of URLs with immediate threat assessment and confidence scoring.
            </p>
          </motion.div>
          <motion.div
            variants={cardVariants}
            whileHover={{ y: -5, boxShadow: "0 10px 25px rgba(0,0,0,0.3)" }}
            className="bg-neutral-900/80 border border-neutral-800 rounded-xl p-6 text-center"
          >
            <div className="text-4xl mb-4">🎯</div>
            <h3 className="font-semibold mb-2">High Accuracy</h3>
            <p className="text-sm text-neutral-400">
              Advanced AI models trained on extensive datasets for reliable phishing identification.
            </p>
          </motion.div>
          <motion.div
            variants={cardVariants}
            whileHover={{ y: -5, boxShadow: "0 10px 25px rgba(0,0,0,0.3)" }}
            className="bg-neutral-900/80 border border-neutral-800 rounded-xl p-6 text-center"
          >
            <div className="text-4xl mb-4">📊</div>
            <h3 className="font-semibold mb-2">Detailed Insights</h3>
            <p className="text-sm text-neutral-400">
              Comprehensive risk indicators and contribution analysis for better understanding.
            </p>
          </motion.div>
        </div>
      </motion.section>

      {/* How It Works Section */}
      <motion.section id="how-it-works" variants={itemVariants} className="mb-12">
        <h2 className="text-2xl font-bold mb-6 text-center">How It Works</h2>
        <div className="space-y-6 max-w-4xl mx-auto">
          <motion.div
            variants={cardVariants}
            className="flex items-center bg-neutral-900/80 border border-neutral-800 rounded-xl p-6"
          >
            <motion.div
              className="flex-shrink-0 w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center text-xl font-bold mr-4"
              animate={{
                boxShadow: ["0 0 0px #3b82f6", "0 0 20px #3b82f6", "0 0 0px #3b82f6"]
              }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              1
            </motion.div>
            <div>
              <h3 className="font-semibold mb-1">Enter URL</h3>
              <p className="text-sm text-neutral-400">Paste the suspicious URL into the scanner input field.</p>
            </div>
          </motion.div>
          <motion.div
            variants={cardVariants}
            className="flex items-center bg-neutral-900/80 border border-neutral-800 rounded-xl p-6"
          >
            <motion.div
              className="flex-shrink-0 w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center text-xl font-bold mr-4"
              animate={{
                boxShadow: ["0 0 0px #3b82f6", "0 0 20px #3b82f6", "0 0 0px #3b82f6"]
              }}
              transition={{ duration: 2, repeat: Infinity, delay: 0.5 }}
            >
              2
            </motion.div>
            <div>
              <h3 className="font-semibold mb-1">AI Analysis</h3>
              <p className="text-sm text-neutral-400">Our machine learning model analyzes multiple features including domain, content, and behavioral patterns.</p>
            </div>
          </motion.div>
          <motion.div
            variants={cardVariants}
            className="flex items-center bg-neutral-900/80 border border-neutral-800 rounded-xl p-6"
          >
            <motion.div
              className="flex-shrink-0 w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center text-xl font-bold mr-4"
              animate={{
                boxShadow: ["0 0 0px #3b82f6", "0 0 20px #3b82f6", "0 0 0px #3b82f6"]
              }}
              transition={{ duration: 2, repeat: Infinity, delay: 1 }}
            >
              3
            </motion.div>
            <div>
              <h3 className="font-semibold mb-1">Get Results</h3>
              <p className="text-sm text-neutral-400">Receive instant verdict with confidence score and detailed risk indicators.</p>
            </div>
          </motion.div>
        </div>
      </motion.section>

      {/* Main Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Scan Panel */}
        <motion.div id="scanner" variants={itemVariants} className="bg-neutral-900/80 border border-neutral-800 rounded-xl p-6">
          <h2 className="font-semibold mb-3">URL Scanner</h2>

          <input
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://example.com"
            className="w-full px-4 py-3 rounded-lg bg-neutral-800 border border-neutral-700 focus:ring-2 focus:ring-blue-600 outline-none"
          />

          <motion.button
            onClick={handleScan}
            disabled={loading}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="w-full mt-4 py-3 rounded-lg bg-blue-600 hover:bg-blue-700 transition disabled:opacity-50"
          >
            {loading ? "Scanning..." : "Scan URL"}
          </motion.button>

          <motion.button
            onClick={() => setShowHistory(true)}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="w-full mt-3 py-2 rounded-lg bg-neutral-800 border border-neutral-700 hover:bg-neutral-700"
          >
            📜 View Scan History
          </motion.button>

          {error && (
            <p className="mt-3 text-sm text-red-400">⚠ {error}</p>
          )}
        </motion.div>

        {/* Result Panel */}
        <motion.div variants={itemVariants} className="md:col-span-2 bg-neutral-900/80 border border-neutral-800 rounded-xl p-6">
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
                <motion.div
                  className={`h-2 rounded-full ${
                    isPhishing ? "bg-red-500" : "bg-green-500"
                  }`}
                  initial={{ width: 0 }}
                  animate={{ width: `${confidencePct}%` }}
                  transition={{ duration: 1 }}
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
        </motion.div>
      </div>

      {/* History Modal */}
      <AnimatePresence>
        {showHistory && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            transition={{ duration: 0.3 }}
            className="fixed inset-0 bg-black/70 flex items-center justify-center z-50"
          >
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

            <motion.button
              onClick={() => setShowHistory(false)}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="mt-4 w-full py-2 rounded-lg bg-neutral-800 hover:bg-neutral-700"
            >
              Close
            </motion.button>
          </div>
        </motion.div>
      )}
      </AnimatePresence>

      <motion.footer variants={itemVariants} className="mt-16 bg-neutral-900/50 border-t border-neutral-800 rounded-t-xl p-8">
        <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <h3 className="font-bold mb-4">PhishGuard</h3>
            <p className="text-sm text-neutral-400">
              Advanced AI-powered phishing detection for a safer internet.
            </p>
          </div>
          <div>
            <h4 className="font-semibold mb-4">Quick Links</h4>
            <ul className="space-y-2 text-sm">
              <li><a href="#about" className="text-neutral-400 hover:text-blue-400 transition-colors">About</a></li>
              <li><a href="#features" className="text-neutral-400 hover:text-blue-400 transition-colors">Features</a></li>
              <li><a href="#how-it-works" className="text-neutral-400 hover:text-blue-400 transition-colors">How It Works</a></li>
            </ul>
          </div>
          {/* <div>
            <h4 className="font-semibold mb-4">Support</h4>
            <ul className="space-y-2 text-sm">
              <li><a href="#" className="text-neutral-400 hover:text-blue-400 transition-colors">Documentation</a></li>
              <li><a href="#" className="text-neutral-400 hover:text-blue-400 transition-colors">API</a></li>
              <li><a href="#" className="text-neutral-400 hover:text-blue-400 transition-colors">Contact Us</a></li>
            </ul>
          </div> */}
          <div>
            <h4 className="font-semibold mb-4">Legal</h4>
            <ul className="space-y-2 text-sm">
              <li><a href="#" className="text-neutral-400 hover:text-blue-400 transition-colors">Privacy Policy</a></li>
              <li><a href="#" className="text-neutral-400 hover:text-blue-400 transition-colors">Terms of Service</a></li>
              <li><a href="#" className="text-neutral-400 hover:text-blue-400 transition-colors">Disclaimer</a></li>
            </ul>
          </div>
        </div>
        <div className="mt-8 pt-8 border-t border-neutral-800 text-center text-sm text-neutral-500">
          © 2025 PhishGuard — Developed by Aryaman Menon. All rights reserved.
        </div>
      </motion.footer>
    </motion.div>
  );
}
