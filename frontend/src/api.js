async function req(path, options = {}) {
  const res = await fetch(`/api${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) throw new Error((await res.json()).detail || res.statusText);
  return res.status === 204 ? null : res.json();
}

export const api = {
  clients: () => req("/clients"),
  stats: () => req("/stats"),
  addClient: (name) => req("/clients", { method: "POST", body: JSON.stringify({ name }) }),
  deleteClient: (id) => req(`/clients/${id}`, { method: "DELETE" }),
  addAccount: (clientId, platform) =>
    req(`/clients/${clientId}/accounts`, { method: "POST", body: JSON.stringify({ platform }) }),
  updateAccount: (id, patch) =>
    req(`/accounts/${id}`, { method: "PATCH", body: JSON.stringify(patch) }),
};
