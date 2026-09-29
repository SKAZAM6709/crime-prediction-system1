import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export default function StateChart({ data }) {
  if (!data?.length) return <p className="empty">No data for this period.</p>;
  return (
    <ResponsiveContainer width="100%" height={Math.max(220, data.length * 28)}>
      <BarChart data={data} layout="vertical" margin={{ top: 4, right: 16, left: 8, bottom: 0 }}>
        <CartesianGrid stroke="var(--line)" horizontal={false} />
        <XAxis type="number" tick={{ fontSize: 12 }} />
        <YAxis type="category" dataKey="state" width={110} tick={{ fontSize: 12 }} />
        <Tooltip formatter={(v) => [v.toLocaleString(), "Incidents"]} />
        <Bar dataKey="total" fill="var(--steel)" radius={[0, 3, 3, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
