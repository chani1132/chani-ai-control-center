import { useState, useCallback } from "react";
import { BotCard } from "./components/BotCard";
import { SummaryCards } from "./components/SummaryCards";
import { TradeTable } from "./components/TradeTable";
import { PnlChart } from "./components/PnlChart";
import { usePolling } from "./hooks/usePolling";
import { fetchBotStatus, fetchTrades, fetchSummary } from "./api";

export default function App() {
  const [botStatus, setBotStatus] = useState({ upbit: null, okx: null });
  const [trades, setTrades] = useState([]);
  const [summary, setSummary] = useState(null);
  const [exchange, setExchange] = useState("all");

  const refresh = useCallback(async () => {
    const [status, summary] = await Promise.all([fetchBotStatus(), fetchSummary()]);
    setBotStatus(status);
    setSummary(summary);
  }, []);

  const loadTrades = useCallback(async () => {
    const params = exchange !== "all" ? { exchange } : {};
    setTrades(await fetchTrades(params));
  }, [exchange]);

  usePolling(refresh, 5000);
  usePolling(loadTrades, 10000);

  return (
    <div className="min-h-screen bg-dark-900">
      {/* Header */}
      <header className="border-b border-dark-600 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-violet-500 flex items-center justify-center font-bold text-sm">C</div>
          <h1 className="font-semibold text-white">Chani AI Trading</h1>
        </div>
        <div className="text-xs text-gray-500">{new Date().toLocaleString("ko-KR")}</div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-6 space-y-6">
        {/* Bot Controls */}
        <section>
          <h2 className="text-sm font-semibold text-gray-400 mb-3">봇 제어</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <BotCard exchange="upbit" status={botStatus.upbit} onRefresh={refresh} />
            <BotCard exchange="okx" status={botStatus.okx} onRefresh={refresh} />
          </div>
        </section>

        {/* Summary */}
        <section>
          <h2 className="text-sm font-semibold text-gray-400 mb-3">수익 요약</h2>
          <SummaryCards summary={summary} />
        </section>

        {/* PnL Chart */}
        {trades.length > 0 && (
          <section>
            <PnlChart trades={trades} />
          </section>
        )}

        {/* Trade History */}
        <section>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-semibold text-gray-400">거래 내역</h2>
            <div className="flex gap-2">
              {["all", "upbit", "okx"].map((ex) => (
                <button
                  key={ex}
                  onClick={() => setExchange(ex)}
                  className={`px-3 py-1 rounded-lg text-xs font-medium transition-all ${
                    exchange === ex
                      ? "bg-blue-500/20 text-blue-400 border border-blue-500/30"
                      : "text-gray-500 hover:text-gray-300"
                  }`}
                >
                  {ex === "all" ? "전체" : ex.toUpperCase()}
                </button>
              ))}
            </div>
          </div>
          <div className="bg-dark-800 border border-dark-600 rounded-xl p-5">
            <TradeTable trades={trades} />
          </div>
        </section>
      </main>
    </div>
  );
}
