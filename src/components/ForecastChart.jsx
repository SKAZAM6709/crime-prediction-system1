import { Area, CartesianGrid, ComposedChart, Legend, Line, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export default function ForecastChart({ history, forecast }) {
  if (!history?.length) return null;
  const last = history[history.length - 1];
  const data = [
    ...history.map((h) => ({ period: h.period, actual: h.count })),
    ...forecast.map((f) => ({ period: f.period, predicted: f.predicted, band: [f.lower, f.upper] })),
  ];
  // Repeat the last actual value on the forecast line so the two lines connect.
  data[history.length - 1].predicted = last.count;

  return (
    <ResponsiveContainer width="100%" height={340}>
      <ComposedChart data={data} margin={{ top: 8, right: 12, left: 0, bottom: 0 }}>
        <CartesianGrid stroke="var(--line)" vertical={false} />
        <XAxis dataKey="period" tick={{ fontSize: 12 }} minTickGap={40} />
        <YAxis tick={{ fontSize: 12 }} width={44} />
        <Tooltip />
        <Legend />
        <Area dataKey="band" name="Likely range (80%)" stroke="none" fill="var(--forecast-soft)" />
        <Line dataKey="actual" name="Recorded" stroke="var(--steel)" strokeWidth={2} dot={false} />
        <Line dataKey="predicted" name="Forecast" stroke="var(--forecast)" strokeWidth={2} strokeDasharray="6 4" dot={false} />
      </ComposedChart>
    </ResponsiveContainer>
  );
}
