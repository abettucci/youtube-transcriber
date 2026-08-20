"use client";

import { useState } from "react";

const BACKEND = process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000";

type Result = {
  transcript: string;
  summary?: string;
  method: "captions" | "whisper";
  word_count?: number;
  cached: boolean;
};

export default function Home() {
  const [url, setUrl] = useState("");
  const [lang, setLang] = useState("es");
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState<"transcript" | "summary" | null>(null);
  const [result, setResult] = useState<Result | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  async function run(endpoint: "transcript" | "summary") {
    if (!url.trim()) return;
    setLoading(true);
    setMode(endpoint);
    setResult(null);
    setError(null);

    try {
      const res = await fetch(`${BACKEND}/${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: url.trim(), lang }),
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail ?? "Error desconocido");
      }
      setResult(await res.json());
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Error inesperado");
    } finally {
      setLoading(false);
    }
  }

  function copy() {
    if (!result) return;
    const text = result.summary ?? result.transcript;
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  }

  return (
    <main style={{ maxWidth: 760, margin: "0 auto", padding: "48px 24px" }}>
      {/* Header */}
      <div style={{ marginBottom: 40 }}>
        <h1 style={{ fontSize: 28, fontWeight: 700, marginBottom: 8 }}>
          📹 YouTube Transcriber
        </h1>
        <p style={{ color: "#888", fontSize: 15 }}>
          Pegá una URL de YouTube para transcribir o resumir el video.
        </p>
      </div>

      {/* Input */}
      <div style={{ marginBottom: 16 }}>
        <input
          type="text"
          placeholder="https://www.youtube.com/watch?v=..."
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && run("transcript")}
          style={{
            width: "100%",
            padding: "12px 16px",
            fontSize: 15,
            background: "#1a1a1a",
            border: "1px solid #333",
            borderRadius: 8,
            color: "#e8e8e8",
            outline: "none",
          }}
        />
      </div>

      {/* Lang + Buttons */}
      <div style={{ display: "flex", gap: 10, alignItems: "center", marginBottom: 32, flexWrap: "wrap" }}>
        <select
          value={lang}
          onChange={(e) => setLang(e.target.value)}
          style={{
            padding: "10px 14px",
            background: "#1a1a1a",
            border: "1px solid #333",
            borderRadius: 8,
            color: "#e8e8e8",
            fontSize: 14,
            cursor: "pointer",
          }}
        >
          <option value="es">Español</option>
          <option value="en">English</option>
          <option value="pt">Português</option>
        </select>

        <button
          onClick={() => run("transcript")}
          disabled={loading || !url.trim()}
          style={btnStyle("#2563eb")}
        >
          {loading && mode === "transcript" ? "Transcribiendo..." : "Transcribir"}
        </button>

        <button
          onClick={() => run("summary")}
          disabled={loading || !url.trim()}
          style={btnStyle("#7c3aed")}
        >
          {loading && mode === "summary" ? "Resumiendo..." : "Transcribir + Resumir"}
        </button>
      </div>

      {/* Error */}
      {error && (
        <div style={{
          background: "#1f0a0a", border: "1px solid #7f1d1d",
          borderRadius: 8, padding: "14px 16px", marginBottom: 24, color: "#fca5a5",
        }}>
          {error}
        </div>
      )}

      {/* Result */}
      {result && (
        <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
          {/* Meta */}
          <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
            <Badge label={result.method === "captions" ? "⚡ Captions" : "🎙 Whisper"} color="#1e3a5f" />
            {result.cached && <Badge label="💾 Caché" color="#1a3a1a" />}
            {result.word_count && <Badge label={`${result.word_count.toLocaleString()} palabras`} color="#2a1f1f" />}
          </div>

          {/* Summary */}
          {result.summary && (
            <div>
              <SectionHeader title="Resumen" onCopy={copy} copied={copied} />
              <ResultBox text={result.summary} />
            </div>
          )}

          {/* Transcript */}
          <div>
            <SectionHeader
              title="Transcripción completa"
              onCopy={!result.summary ? copy : undefined}
              copied={!result.summary ? copied : false}
            />
            <ResultBox text={result.transcript} maxHeight={320} />
          </div>
        </div>
      )}
    </main>
  );
}

function btnStyle(bg: string): React.CSSProperties {
  return {
    padding: "10px 20px",
    background: bg,
    border: "none",
    borderRadius: 8,
    color: "#fff",
    fontSize: 14,
    fontWeight: 600,
    cursor: "pointer",
    opacity: 1,
  };
}

function Badge({ label, color }: { label: string; color: string }) {
  return (
    <span style={{
      background: color, padding: "4px 10px",
      borderRadius: 20, fontSize: 12, color: "#ccc",
    }}>
      {label}
    </span>
  );
}

function SectionHeader({ title, onCopy, copied }: {
  title: string; onCopy?: () => void; copied?: boolean;
}) {
  return (
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
      <span style={{ fontSize: 13, fontWeight: 600, color: "#888", textTransform: "uppercase", letterSpacing: 1 }}>
        {title}
      </span>
      {onCopy && (
        <button onClick={onCopy} style={{
          background: "none", border: "1px solid #333",
          borderRadius: 6, color: "#888", fontSize: 12, padding: "4px 10px", cursor: "pointer",
        }}>
          {copied ? "✓ Copiado" : "Copiar"}
        </button>
      )}
    </div>
  );
}

function ResultBox({ text, maxHeight }: { text: string; maxHeight?: number }) {
  return (
    <div style={{
      background: "#1a1a1a",
      border: "1px solid #2a2a2a",
      borderRadius: 8,
      padding: "16px",
      fontSize: 14,
      lineHeight: 1.7,
      whiteSpace: "pre-wrap",
      overflowY: maxHeight ? "auto" : undefined,
      maxHeight,
      color: "#d4d4d4",
    }}>
      {text}
    </div>
  );
}
