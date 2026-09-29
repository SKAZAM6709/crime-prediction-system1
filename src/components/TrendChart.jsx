import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export default function TrendChart({ data }) {
  if (!data?.length) return <p className="empty">No incidents match these filters.</p>;
  return (
    <ResponsiveContainer width="100%" height={300}>
      <AreaChart data={data} margin={{ top: 8, right: 12, left: 0, bottom: 0 }}>
        <CartesianGrid stroke="var(--line)" vertical={false} />
        <XAxis dataKey="period" tick={{ fontSize: 12 }} minTickGap={48} />
        <YAxis tick={{ fontSize: 12 }} width={44} />
        <Tooltip formatter={(v) => [v.toLocaleString(), "Incidents"]} />
        <Area type="monotone" dataKey="count" stroke="var(--steel)" fill="var(--steel-soft)" strokeWidth={2} />
      </AreaChart>
    </ResponsiveContainer>
  );
}
