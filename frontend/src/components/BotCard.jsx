import { useState } from "react";
import { StatusBadge } from "./StatusBadge";
import { startBot, stopBot } from "../api";

export function BotCard({ exchange, status, onRefresh }) {
  const [loading, setLoading] = useState(false);
  const [symbol, setSymbol] = useState(
    exchange === "upbit" ? "BTC/KRW" : "BTC/USDT:USDT"
  );

  const isRunning = status?.running;

  const handleToggle = async () => {
    setLoading(true);
    try {
      if (isRunning) {
        await stopBot(exchange);
      } else {
        await startBot({ exchange, strategy: "manual", symbol, config: {} });
      }
      onRefresh();
    } catch (e) {
      alert(e?.response?.data?.detail || "오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  const label = exchange === "upbit" ? "Upbit" : "OKX";
  const type = exchange === "upbit" ? "현물" : "선물";
  const accent = exchange === "upbit" ? "from-blue-600 to-blue-400" : "from-violet-600 to-violet-400";

  return (
    <div className="bg-dark-800 border border-dark-600 rounded-xl p-5 flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${accent} flex items-center justify-center text-sm font-bold`}>
            {label[0]}
          </div>
          <div>
            <p className="font-semibold text-sm">{label}</p>
            <p className="text-xs text-gray-500">{type}</p>
          </div>
        </div>
        <StatusBadge running={isRunning} />
      </div>

      <div>
        <label className="text-xs text-gray-500 mb-1 block">심볼</label>
        <input
          className="w-full bg-dark-700 border border-dark-600 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
          value={symbol}
          onChange={(e) => setSymbol(e.target.value)}
          disabled={isRunning}
        />
      </div>

      <button
        onClick={handleToggle}
        disabled={loading}
        className={`w-full py-2 rounded-lg text-sm font-semibold transition-all disabled:opacity-50 ${
          isRunning
            ? "bg-red-500/20 text-red-400 hover:bg-red-500/30 border border-red-500/30"
            : "bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30 border border-emerald-500/30"
        }`}
      >
        {loading ? "처리중..." : isRunning ? "봇 정지" : "봇 시작"}
      </button>
    </div>
  );
}
