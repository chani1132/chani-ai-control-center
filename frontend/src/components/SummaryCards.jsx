export function SummaryCards({ summary }) {
  const cards = [
    { label: "총 거래 수", value: summary?.total_trades ?? "-", unit: "건" },
    {
      label: "총 손익",
      value: summary?.total_pnl != null ? (summary.total_pnl > 0 ? "+" : "") + summary.total_pnl : "-",
      unit: "USDT",
      color: summary?.total_pnl > 0 ? "text-emerald-400" : summary?.total_pnl < 0 ? "text-red-400" : "",
    },
    { label: "승률", value: summary?.win_rate ?? "-", unit: "%" },
    { label: "승 / 패", value: summary ? `${summary.win_count} / ${summary.loss_count}` : "-", unit: "" },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
      {cards.map((c) => (
        <div key={c.label} className="bg-dark-800 border border-dark-600 rounded-xl p-4">
          <p className="text-xs text-gray-500 mb-1">{c.label}</p>
          <p className={`text-xl font-bold ${c.color || "text-white"}`}>
            {c.value}
            {c.unit && <span className="text-sm font-normal text-gray-400 ml-1">{c.unit}</span>}
          </p>
        </div>
      ))}
    </div>
  );
}
