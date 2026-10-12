import { useCallback, useEffect, useState } from "react";
import { startOfWeek, toISODate } from "../lib/dates";
import {
  fetchEvents,
  googleConnectUrl,
  googleStatus,
  googleSync,
} from "../lib/googleApi";

// Google connection state, time blocks for the viewed week, and sync.
export function useGoogle(anchor, onSynced) {
  const [connected, setConnected] = useState(null); // null = unknown (e.g. backend unreachable)
  const [events, setEvents] = useState([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const viewedWeek = toISODate(startOfWeek(anchor));

  const loadEvents = useCallback(async () => {
    if (!connected) return setEvents([]);
    try {
      setEvents(await fetchEvents(viewedWeek));
    } catch (e) {
      setEvents([]);
      setError(e.message);
    }
  }, [connected, viewedWeek]);

  const sync = useCallback(async () => {
    setBusy(true);
    try {
      await googleSync();
      await Promise.all([onSynced(), loadEvents()]);
      setError(null);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }, [onSynced, loadEvents]);

  // On load: check the connection. Coming back from Google's consent screen, import right away.
  useEffect(() => {
    const returned = new URLSearchParams(window.location.search).get("google");
    googleStatus()
      .then((s) => {
        setConnected(s.connected);
        if (s.connected && returned === "connected") sync();
      })
      .catch(() => setConnected(null));
    if (returned)
      window.history.replaceState(null, "", window.location.pathname);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    loadEvents();
  }, [loadEvents]);

  const connect = async () => {
    try {
      window.location.assign((await googleConnectUrl()).url);
    } catch (e) {
      setError(e.message);
    }
  };

  return { connected, events, busy, error, connect, sync };
}
