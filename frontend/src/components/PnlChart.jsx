import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine } from "recharts";

export function PnlChart({ trades }) {
  if (!trades?.length) return null;

  let cumulative = 0;
  const data = trades
    .slice()
    .reverse()
    .map((t) => {
      cumulative += t.pnl;
      return {
        time: new Date(t.created_at).toLocaleDateString("ko-KR"),
        pnl: Math.round(cumulative * 10000) / 10000,
      };
    });

  return (
    <div className="bg-dark-800 border border-dark-600 rounded-xl p-5">
      <p className="text-sm font-semibold mb-4 text-gray-300">누적 손익 (PnL)</p>
      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={data}>
          <XAxis dataKey="time" tick={{ fontSize: 11, fill: "#6b7280" }} axisLine={false} tickLine={false} />
          <YAxis tick={{ fontSize: 11, fill: "#6b7280" }} axisLine={false} tickLine={false} width={50} />
          <Tooltip
            contentStyle={{ backgroundColor: "#1a1d27", border: "1px solid #222535", borderRadius: 8, fontSize: 12 }}
            labelStyle={{ color: "#9ca3af" }}
          />
          <ReferenceLine y={0} stroke="#374151" strokeDasharray="4 4" />
          <Line
            type="monotone"
            dataKey="pnl"
            stroke="#10b981"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4, fill: "#10b981" }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
