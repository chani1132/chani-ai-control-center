import clsx from "clsx";

export function StatusBadge({ running }) {
  return (
    <span className={clsx(
      "inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold",
      running ? "bg-emerald-900/60 text-emerald-300" : "bg-gray-700/60 text-gray-400"
    )}>
      <span className={clsx("w-1.5 h-1.5 rounded-full", running ? "bg-emerald-400 animate-pulse" : "bg-gray-500")} />
      {running ? "실행중" : "정지"}
    </span>
  );
}
