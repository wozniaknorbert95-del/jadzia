const API_BASE = window.location.origin;
const TOKEN_KEY = "coi_commander_jwt";

function getToken() {
  return localStorage.getItem(TOKEN_KEY) || "";
}

function setToken(t) {
  localStorage.setItem(TOKEN_KEY, t);
}

async function api(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;
  if (options.body && typeof options.body === "object") {
    headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(options.body);
  }
  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (res.status === 401) throw new Error("Brak autoryzacji — ustaw JWT");
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail?.message || err.detail || res.statusText);
  }
  return res.json();
}

function toast(msg) {
  const el = document.getElementById("toast");
  el.textContent = msg;
  el.hidden = false;
  setTimeout(() => { el.hidden = true; }, 4000);
}

function confirmAction(message) {
  return new Promise((resolve) => {
    const dlg = document.getElementById("confirm-dialog");
    document.getElementById("confirm-body").textContent = message;
    dlg.showModal();
    dlg.onclose = () => resolve(dlg.returnValue === "ok");
  });
}

function showView(name) {
  document.querySelectorAll(".view").forEach((v) => {
    v.hidden = v.id !== `view-${name}`;
    v.classList.toggle("active", v.id === `view-${name}`);
  });
  document.querySelectorAll(".nav-btn").forEach((b) => {
    b.classList.toggle("active", b.dataset.view === name);
  });
}

function renderPriorities(items) {
  const el = document.getElementById("priorities");
  el.innerHTML = items.length
    ? items.map((p) => `
      <article class="card severity-${p.severity}" role="listitem">
        <strong>${p.title}</strong>
        <div class="badge">${p.severity}</div>
        <p>${p.escalation_reason || ""}</p>
        <small>SLA: <span class="badge ${p.sla_status}">${p.sla_status}</span></small>
      </article>`).join("")
    : "<p>Brak priorytetów — spokój ✓</p>";
}

function renderQueue(items) {
  const filtered = items.filter((i) => i.severity !== "INFO");
  const el = document.getElementById("queue-list");
  el.innerHTML = filtered.map((q) => `
    <article class="card severity-${q.severity}" role="listitem">
      <strong>${q.title}</strong>
      <span class="badge">${q.severity}</span>
      <span class="badge ${q.sla_status}">${q.sla_status}</span>
      <p>Pewność: ${Math.round((q.confidence || 0) * 100)}% · Źródło: ${q.source}</p>
    </article>`).join("") || "<p>Kolejka pusta</p>";
}

async function loadHome() {
  const [prio, queue, agents, snap] = await Promise.all([
    api("/api/v1/commander/priorities/today"),
    api("/api/v1/commander/queue"),
    api("/api/v1/agents"),
    api("/api/v1/commander/analytics/snapshot").catch(() => null),
  ]);
  renderPriorities(prio.priorities || []);
  renderQueue(queue.items || []);
  const slaBad = (agents.agents || []).filter((a) => !a.sla_ok).length;
  const fresh = snap?.freshness?.ga4?.status || "—";
  document.getElementById("health-strip").textContent =
    `Agenci SLA breach: ${slaBad} · GA4 freshness: ${fresh} · Worker: sprawdź Analytics`;
}

async function loadMarketing() {
  const cal = await api("/api/v1/content-calendar");
  const agents = await api("/api/v1/agents");
  const mkt = (agents.agents || []).find((a) => a.agent_id === "marketing");
  const held = document.getElementById("held-banner");
  if (mkt?.status === "PAUSED" || (mkt?.held_count || 0) > 0) {
    held.hidden = false;
    held.textContent = `Agent marketing wstrzymany — ${mkt.held_count || 0} postów w kolejce held`;
  } else {
    held.hidden = true;
  }
  const el = document.getElementById("calendar-entries");
  el.innerHTML = (cal.entries || []).map((e) => `
    <article class="card">
      <strong>${e.title}</strong>
      <p class="badge">${e.status}</p>
      <p lang="nl">${(e.body_nl || "").slice(0, 120)}…</p>
      <div>
        ${e.status === "draft" || e.status === "pending_approval"
          ? `<button type="button" data-approve="${e.entry_id}">Zatwierdź</button>` : ""}
        ${e.status === "approved"
          ? `<button type="button" data-publish="${e.entry_id}">Opublikuj</button>` : ""}
        ${e.status === "published"
          ? `<button type="button" data-unpublish="${e.entry_id}">Cofnij publikację</button>` : ""}
      </div>
    </article>`).join("") || "<p>Brak wpisów kalendarza</p>";

  el.querySelectorAll("[data-approve]").forEach((btn) => {
    btn.onclick = async () => {
      if (!await confirmAction("Zatwierdzić post?")) return;
      await api(`/api/v1/content-calendar/${btn.dataset.approve}`, {
        method: "PATCH",
        body: { status: "approved" },
      });
      toast("Zatwierdzono");
      loadMarketing();
    };
  });
  el.querySelectorAll("[data-publish]").forEach((btn) => {
    btn.onclick = async () => {
      if (!await confirmAction("Opublikować na Facebooku? Akcja publiczna.")) return;
      try {
        await api(`/api/v1/content-calendar/${btn.dataset.publish}/publish`, {
          method: "POST",
          body: {},
        });
        toast("Opublikowano");
      } catch (err) {
        toast(String(err.message));
      }
      loadMarketing();
    };
  });
  el.querySelectorAll("[data-unpublish]").forEach((btn) => {
    btn.onclick = async () => {
      if (!await confirmAction("Usunąć post z FB? (unpublish)")) return;
      await api(`/api/v1/content-calendar/${btn.dataset.unpublish}/unpublish`, {
        method: "POST",
        body: { reason: "operator_unpublish" },
      });
      toast("Cofnięto publikację");
      loadMarketing();
    };
  });
}

async function loadAnalytics() {
  const [snap, orders, leads] = await Promise.all([
    api("/api/v1/commander/analytics/snapshot"),
    api("/api/v1/orders"),
    api("/api/v1/leads"),
  ]);
  const tiles = document.getElementById("analytics-tiles");
  const f = snap.freshness || {};
  tiles.innerHTML = Object.entries(f).map(([k, v]) => `
    <article class="card">
      <strong>${k.toUpperCase()}</strong>
      <p>Ostatnia sync: ${v.last_sync_at || "—"}</p>
      <span class="badge ${v.status}">${v.status}</span>
      ${v.staleness_seconds != null ? `<small>${v.staleness_seconds}s temu</small>` : ""}
    </article>`).join("");

  document.getElementById("orders-list").innerHTML =
    (orders.orders || []).slice(0, 10).map((o) =>
      `<div>#${o.order_id} · ${o.status} · €${o.total_gross}</div>`).join("") || "Brak";

  document.getElementById("leads-list").innerHTML =
    (leads.leads || []).slice(0, 10).map((l) =>
      `<div>${l.email} · score ${l.game_score ?? "—"}</div>`).join("") || "Brak";
}

async function loadAgents() {
  const data = await api("/api/v1/agents");
  document.getElementById("agents-list").innerHTML = (data.agents || []).map((a) => `
    <article class="card">
      <strong>${a.label}</strong>
      <p>Status: ${a.status} · SLA: <span class="badge ${a.sla_ok ? "ok" : "red"}">${a.sla_ok ? "ok" : "breach"}</span></p>
      <p>Held: ${a.held_count || 0}</p>
      ${a.status === "LIVE"
        ? `<button type="button" data-pause="${a.agent_id}">Pauza</button>`
        : `<button type="button" data-resume="${a.agent_id}">Wznów</button>`}
    </article>`).join("");

  document.querySelectorAll("[data-pause]").forEach((btn) => {
    btn.onclick = async () => {
      if (!await confirmAction("Pauzować agenta? Zaplanowane posty → held.")) return;
      await api(`/api/v1/agents/${btn.dataset.pause}/pause`, { method: "POST" });
      loadAgents();
    };
  });
  document.querySelectorAll("[data-resume]").forEach((btn) => {
    btn.onclick = async () => {
      await api(`/api/v1/agents/${btn.dataset.resume}/resume`, { method: "POST" });
      loadAgents();
    };
  });
}

async function loadSettings() {
  const s = await api("/api/v1/commander/settings");
  document.getElementById("delegat-email").value = s.delegat_email || "";
}

async function refresh() {
  if (!getToken()) return;
  const active = document.querySelector(".view:not([hidden])")?.id?.replace("view-", "") || "home";
  if (active === "home") await loadHome();
  if (active === "marketing") await loadMarketing();
  if (active === "analytics") await loadAnalytics();
  if (active === "agents") await loadAgents();
  if (active === "settings") await loadSettings();
}

document.querySelectorAll(".nav-btn").forEach((btn) => {
  btn.addEventListener("click", async () => {
    showView(btn.dataset.view);
    try { await refresh(); } catch (e) { toast(e.message); }
  });
});

document.getElementById("auth-save").onclick = () => {
  setToken(document.getElementById("jwt-input").value.trim());
  toast("Token zapisany");
  refresh().catch((e) => toast(e.message));
};

document.getElementById("settings-form").onsubmit = async (e) => {
  e.preventDefault();
  try {
    await api("/api/v1/commander/settings", {
      method: "PATCH",
      body: {
        delegat_email: document.getElementById("delegat-email").value,
        ui_language: "pl",
      },
    });
    toast("Ustawienia zapisane");
  } catch (err) {
    toast(err.message);
  }
};

const params = new URLSearchParams(window.location.search);
if (params.get("ticket")) {
  showView("home");
  toast(`Ticket #${params.get("ticket")} — zaloguj JWT aby kontynuować`);
}

if (getToken()) {
  document.getElementById("jwt-input").value = getToken();
  refresh().catch((e) => toast(e.message));
}
