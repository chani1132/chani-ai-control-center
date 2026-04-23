import clsx from "clsx";

const SIDE_COLOR = {
  buy: "text-emerald-400",
  long: "text-emerald-400",
  sell: "text-red-400",
  short: "text-red-400",
};

export function TradeTable({ trades }) {
  if (!trades?.length) {
    return (
      <div className="text-center text-gray-600 py-12 text-sm">거래 내역이 없습니다.</div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-xs text-gray-500 border-b border-dark-600">
            {["거래소", "심볼", "방향", "가격", "수량", "비용", "PnL", "전략", "시간"].map((h) => (
              <th key={h} className="text-left pb-2 pr-4 font-medium">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-dark-700">
          {trades.map((t) => (
            <tr key={t.id} className="hover:bg-dark-700/30 transition-colors">
              <td className="py-2 pr-4">
                <span className="uppercase text-xs font-semibold text-gray-400">{t.exchange}</span>
              </td>
              <td className="py-2 pr-4 font-mono text-xs">{t.symbol}</td>
              <td className={clsx("py-2 pr-4 font-semibold uppercase", SIDE_COLOR[t.side])}>{t.side}</td>
              <td className="py-2 pr-4 font-mono">{t.price.toLocaleString()}</td>
              <td className="py-2 pr-4 font-mono">{t.amount}</td>
              <td className="py-2 pr-4 font-mono">{t.cost.toLocaleString()}</td>
              <td className={clsx("py-2 pr-4 font-mono", t.pnl > 0 ? "text-emerald-400" : t.pnl < 0 ? "text-red-400" : "text-gray-500")}>
                {t.pnl > 0 ? "+" : ""}{t.pnl}
              </td>
              <td className="py-2 pr-4 text-xs text-gray-500">{t.strategy}</td>
              <td className="py-2 text-xs text-gray-500">{new Date(t.created_at).toLocaleString("ko-KR")}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
