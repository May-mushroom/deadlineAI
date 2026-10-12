import { api } from "./api";

export const googleStatus = () => api("/integrations/google/status");
export const googleConnectUrl = () => api("/integrations/google/connect");
export const googleSync = () =>
  api("/integrations/google/sync", { method: "POST" });
export const fetchEvents = (weekStart) =>
  api(`/integrations/google/events?week_start=${weekStart}`);
