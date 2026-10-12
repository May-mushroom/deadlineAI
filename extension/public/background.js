// Opens the side panel when the user clicks the extension's toolbar button.
chrome.runtime.onInstalled.addListener(() => {
  chrome.sidePanel
    .setPanelBehavior({ openPanelOnActionClick: true })
    .catch((error) => console.error(error));
});

// NOTE (business logic / platform behavior, left as a stub):
// - A side panel registered via manifest "side_panel.default_path" is shared
//   globally across tabs by default. To make the panel close/change
//   automatically when the user switches tabs, manage it per-tab instead,
//   e.g. using chrome.sidePanel.setOptions({ tabId, path, enabled }) from
//   this service worker, driven by chrome.tabs.onActivated.
// - The in-panel "X" close button currently just calls window.close() from
//   the React app (see App.jsx handleClose). If that doesn't close the panel
//   on your Chrome version, message this service worker instead and call
//   chrome.sidePanel.setOptions({ tabId, enabled: false }) here.
