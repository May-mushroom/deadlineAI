export default function StatCard({ label, children, valueClass = "text-2xl font-semibold" }) {
  return (
    <section className="rounded-lg border border-line bg-surface p-4">
      <h2 className="text-sm text-muted">{label}</h2>
      <p className={`mt-2 ${valueClass}`}>{children}</p>
    </section>
  );
}
