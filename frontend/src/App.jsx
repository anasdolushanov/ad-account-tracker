import { useEffect, useState } from "react";
import { api } from "./api.js";

const STATUSES = ["not_started", "in_progress", "blocked", "live"];
const label = (s) => s.replace("_", " ");

export default function App() {
  const [clients, setClients] = useState([]);
  const [stats, setStats] = useState({});
  const [name, setName] = useState("");
  const [error, setError] = useState("");

  const load = async () => {
    try {
      const [c, s] = await Promise.all([api.clients(), api.stats()]);
      setClients(c);
      setStats(s);
      setError("");
    } catch (e) {
      setError(`Could not reach the API: ${e.message}`);
    }
  };

  useEffect(() => { load(); }, []);

  const run = (fn) => async (...args) => {
    try { await fn(...args); await load(); } catch (e) { setError(e.message); }
  };

  const addClient = run(async (e) => {
    e.preventDefault();
    if (!name.trim()) return;
    await api.addClient(name);
    setName("");
  });

  return (
    <main>
      <h1>Ad Account Tracker</h1>

      <section className="stats">
        {STATUSES.map((s) => (
          <div key={s} className={`stat ${s}`}>
            <strong>{stats[s] ?? 0}</strong>
            <span>{label(s)}</span>
          </div>
        ))}
      </section>

      <form onSubmit={addClient} className="row">
        <input value={name} onChange={(e) => setName(e.target.value)} placeholder="New client name" />
        <button>Add client</button>
      </form>

      {error && <p className="error">{error}</p>}

      {clients.map((c) => (
        <ClientCard key={c.id} client={c}
          onAddAccount={run(api.addAccount)}
          onUpdate={run(api.updateAccount)}
          onDelete={run(api.deleteClient)} />
      ))}
      {clients.length === 0 && !error && <p className="muted">No clients yet. Add one above.</p>}
    </main>
  );
}

function ClientCard({ client, onAddAccount, onUpdate, onDelete }) {
  const [platform, setPlatform] = useState("");

  const submit = (e) => {
    e.preventDefault();
    if (!platform.trim()) return;
    onAddAccount(client.id, platform);
    setPlatform("");
  };

  return (
    <article className="card">
      <header className="row">
        <h2>{client.name}</h2>
        <button className="ghost" onClick={() => confirm(`Delete ${client.name}?`) && onDelete(client.id)}>Delete</button>
      </header>

      <table>
        <tbody>
          {client.accounts.map((a) => (
            <tr key={a.id}>
              <td>{a.platform}</td>
              <td>
                <select value={a.status} className={a.status}
                  onChange={(e) => onUpdate(a.id, { status: e.target.value })}>
                  {STATUSES.map((s) => <option key={s} value={s}>{label(s)}</option>)}
                </select>
              </td>
              <td>
                <input defaultValue={a.notes} placeholder="Notes"
                  onBlur={(e) => e.target.value !== a.notes && onUpdate(a.id, { notes: e.target.value })} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <form onSubmit={submit} className="row">
        <input value={platform} onChange={(e) => setPlatform(e.target.value)} placeholder="Platform (e.g. Google Ads)" />
        <button>Add account</button>
      </form>
    </article>
  );
}
