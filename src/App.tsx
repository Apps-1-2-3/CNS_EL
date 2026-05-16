import { useState } from "react";
import { EncodePanel } from "./components/EncodePanel";
import { DecodePanel } from "./components/DecodePanel";
import { Shield, Lock, Unlock } from "lucide-react";

export default function App() {
  const [tab, setTab] = useState<"encode" | "decode">("encode");

  return (
    <div className="min-h-screen">
      <header className="border-b border-border bg-panel/60 backdrop-blur sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-5 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-accent to-accent2 flex items-center justify-center shadow-lg shadow-accent/20">
              <Shield size={18} className="text-bg" />
            </div>
            <div>
              <h1 className="text-lg font-semibold tracking-tight">StegoVault</h1>
              <div className="text-[11px] text-slate-400 mono uppercase tracking-wider">
                Secure Steganographic Analysis · v2.0
              </div>
            </div>
          </div>
          <div className="flex items-center gap-1 bg-bg/60 border border-border rounded-lg p-1">
            <TabBtn active={tab === "encode"} onClick={() => setTab("encode")}>
              <Lock size={14} /> Encode
            </TabBtn>
            <TabBtn active={tab === "decode"} onClick={() => setTab("decode")}>
              <Unlock size={14} /> Decode
            </TabBtn>
          </div>
        </div>
      </header>
      <main className="max-w-6xl mx-auto p-5">
        {tab === "encode" ? <EncodePanel /> : <DecodePanel />}
      </main>
      <footer className="max-w-6xl mx-auto px-5 py-8 text-center text-xs text-slate-500 mono">
        AES-128-CBC · HMAC-SHA256 · PBKDF2 (200k) · Adaptive LSB · Key-seeded PRNG
      </footer>
    </div>
  );
}

function TabBtn({ active, onClick, children }: { active: boolean; onClick: () => void; children: React.ReactNode }) {
  return (
    <button onClick={onClick}
      className={`px-3 py-1.5 rounded-md text-sm flex items-center gap-1.5 transition
        ${active ? "bg-accent text-bg shadow" : "text-slate-400 hover:text-slate-200"}`}>
      {children}
    </button>
  );
}
