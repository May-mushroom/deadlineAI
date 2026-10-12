// Connect Google (OAuth) when not connected, otherwise import Google Tasks on demand.
export default function GoogleButton({ connected, busy, onConnect, onSync }) {
  if (connected === null) return null; // backend unreachable or status unknown
  return (
    <button
      onClick={connected ? onSync : onConnect}
      disabled={busy}
      className="rounded border border-white/30 px-3 py-1.5 text-sm hover:bg-white/10 disabled:opacity-60"
    >
      {connected ? (busy ? "Syncing…" : "Sync Google") : "Connect Google"}
    </button>
  );
}
