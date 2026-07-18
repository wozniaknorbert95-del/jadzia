const API_BASE = window.location.origin;
const TOKEN_KEY = "coi_commander_jwt";
let pendingUndoEntryId = null;
let undoTimer = null;
let selectedEntries = new Set();
let roleMap = {};

function getToken() {
  return localStorage.getItem(TOKEN_KEY) || "";
}

function setToken(t) {
  localStorage.setItem(TOKEN_KEY, t || "");
  if (!t) localStorage.removeItem(TOKEN_KEY);
  updateAuthStatus();
}

function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
  const input = document.getElementById("jwt-input");
  if (input) input.value = "";
  updateAuthStatus();
}

function setAuthExpanded(expanded) {
  const panel = document.getElementById("auth-panel");
  const body = document.getElementById("auth-body");
  const toggle = document.getElementById("auth-toggle");
  if (!panel || !body) return;
  panel.classList.toggle("auth-collapsed", !expanded);
  body.hidden = !expanded;
  if (toggle) {
    toggle.hidden = expanded || !getToken();
    toggle.setAttribute("aria-expanded", expanded ? "true" : "false");
  }
}

function updateAuthStatus() {
  const loggedIn = !!getToken();
  const el = document.getElementById("auth-status");
  if (el) {
    el.textContent = loggedIn
      ? "Zalogowano (sesja JWT w przeglądarce)."
      : "Telegram: /commander → jednorazowy link (15 min).";
  }
  // Always sync chrome even if status node missing
  setAuthExpanded(!loggedIn);
  const input = document.getElementById("jwt-input");
  if (input && loggedIn) input.value = "";
}

async function exchangeLoginCode(code) {
  const res = await fetch(`${API_BASE}/api/v1/commander/auth/exchange`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Kod logowania nieważny lub wygasł");
  }
  return res.json();
}

function stripAuthParamsFromUrl() {
  const url = new URL(window.location.href);
  if (!url.searchParams.has("code") && !url.searchParams.has("jwt")) return;
  url.searchParams.delete("code");
  url.searchParams.delete("jwt");
  const qs = url.searchParams.toString();
  const next = `${url.pathname}${qs ? `?${qs}` : ""}${url.hash}`;
  window.history.replaceState({}, "", next);
}

function registerServiceWorker() {
  if (!("serviceWorker" in navigator)) return;
  navigator.serviceWorker.register("./sw.js", { scope: "./" }).catch(() => {
    /* non-fatal on http/dev */
  });
}

async function api(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;
  if (options.body && typeof options.body === "object") {
    headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(options.body);
  } else if (typeof options.body === "string" && !headers["Content-Type"]) {
    // Call sites that pre-stringify still need JSON content-type
    headers["Content-Type"] = "application/json";
  }
  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (res.status === 401) {
    setAuthExpanded(true);
    throw new Error("Sesja wygasła — Telegram /commander lub wklej token");
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    const detail = err.detail;
    const msg = typeof detail === "object" ? detail.message || JSON.stringify(detail) : detail;
    throw new Error(msg || res.statusText);
  }
  return res.json();
}

function toast(msg) {
  const el = document.getElementById("toast");
  el.textContent = msg;
  el.hidden = false;
  setTimeout(() => { el.hidden = true; }, 4000);
}

function confirmAction(message, requireReason = false) {
  return new Promise((resolve) => {
    const dlg = document.getElementById("confirm-dialog");
    document.getElementById("confirm-body").textContent = message;
    const reasonLabel = document.getElementById("reason-label");
    const reasonInput = document.getElementById("reason-input");
    reasonLabel.hidden = !requireReason;
    reasonInput.hidden = !requireReason;
    reasonInput.value = "";
    dlg.showModal();
    dlg.onclose = () => {
      if (dlg.returnValue === "ok" && requireReason && !reasonInput.value.trim()) {
        toast("Podaj powód");
        resolve({ ok: false });
        return;
      }
      resolve({
        ok: dlg.returnValue === "ok",
        reason: reasonInput.value.trim(),
      });
    };
  });
}

function approvalCard(item, actionsHtml = "") {
  return `
    <article class="card approval-card severity-${item.severity}" role="listitem">
      <header class="card-header">
        <strong>${item.title}</strong>
        <span class="badge">${item.severity}</span>
        <span class="badge ${item.sla_status}">${item.sla_status}</span>
      </header>
      <p class="escalation">${item.escalation_reason || ""}</p>
      <dl class="meta">
        <dt>Źródło</dt><dd>${item.source}</dd>
        <dt>Pewność</dt><dd>${Math.round((item.confidence || 0) * 100)}%</dd>
        <dt>Polityka</dt><dd>${item.severity_policy_ref || "D0.8"}</dd>
      </dl>
      <div class="actions">${actionsHtml}</div>
    </article>`;
}

function renderPriorities(items) {
  const el = document.getElementById("priorities");
  el.innerHTML = items.length
    ? items.map((p) => approvalCard(p)).join("")
    : "<p>Brak priorytetów — spokój ✓</p>";
}

function leadDispositionActions(item) {
  if (item.queue_type !== "hot_lead" && item.queue_type !== "sales_cta") return "";
  const leadId = item.payload?.lead_id || item.payload?.id;
  if (!leadId) return "";
  return `
    <button type="button" data-lead-disp="${leadId}" data-disp="acked">Potwierdź</button>
    <button type="button" data-lead-disp="${leadId}" data-disp="snoozed">Odłóż</button>
    <button type="button" data-lead-disp="${leadId}" data-disp="closed">Zamknij</button>
  `;
}

function ticketDispositionActions(item) {
  if (item.queue_type !== "cs_followup") return "";
  const ticketId = item.payload?.ticket_id;
  if (!ticketId) return "";
  return `
    <button type="button" data-ticket-disp="${ticketId}" data-disp="acked">Potwierdź</button>
    <button type="button" data-ticket-disp="${ticketId}" data-disp="snoozed">Odłóż</button>
    <button type="button" data-ticket-disp="${ticketId}" data-disp="closed">Zamknij</button>
  `;
}

function queueItemActions(item) {
  return leadDispositionActions(item) + ticketDispositionActions(item);
}

function renderQueue(items) {
  const filtered = items.filter((i) => i.severity !== "INFO");
  const el = document.getElementById("queue-list");
  el.innerHTML = filtered.length
    ? filtered.map((q) => approvalCard(q, queueItemActions(q))).join("")
    : "<p>Kolejka pusta</p>";
  el.querySelectorAll("[data-lead-disp]").forEach((btn) => {
    btn.onclick = async () => {
      const id = btn.dataset.leadDisp;
      const disp = btn.dataset.disp;
      try {
        await api(`/api/v1/commander/leads/${id}/disposition`, {
          method: "POST",
          body: JSON.stringify({ disposition: disp }),
        });
        toast(`Lead ${id} → ${disp}`);
        loadHome().catch((e) => toast(e.message));
      } catch (e) {
        toast(e.message || "Nie udało się zmienić statusu leada");
      }
    };
  });
  el.querySelectorAll("[data-ticket-disp]").forEach((btn) => {
    btn.onclick = async () => {
      const id = btn.dataset.ticketDisp;
      const disp = btn.dataset.disp;
      try {
        await api(`/api/v1/commander/tickets/${id}/disposition`, {
          method: "POST",
          body: JSON.stringify({ disposition: disp }),
        });
        toast(`Ticket ${id} → ${disp}`);
        loadHome().catch((e) => toast(e.message));
      } catch (e) {
        toast(e.message || "Nie udało się zmienić statusu ticketu");
      }
    };
  });
}

function showUndoBar(entryId) {
  pendingUndoEntryId = entryId;
  const bar = document.getElementById("undo-bar");
  bar.hidden = false;
  let left = 60;
  const msg = document.getElementById("undo-msg");
  clearInterval(undoTimer);
  undoTimer = setInterval(() => {
    left -= 1;
    msg.textContent = `Cofnij zatwierdzenie (${left}s)`;
    if (left <= 0) {
      clearInterval(undoTimer);
      bar.hidden = true;
      pendingUndoEntryId = null;
    }
  }, 1000);
}

async function loadHome() {
  const prioEl = document.getElementById("priorities");
  const queueEl = document.getElementById("queue-list");
  const healthEl = document.getElementById("health-strip");
  prioEl.innerHTML = "<p class=\"hint\">Ładowanie priorytetów…</p>";
  queueEl.innerHTML = "<p class=\"hint\">Ładowanie kolejki…</p>";

  let prio;
  let queue;
  try {
    [prio, queue] = await Promise.all([
      api("/api/v1/commander/priorities/today"),
      api("/api/v1/commander/queue"),
    ]);
    renderPriorities(prio.priorities || []);
    renderQueue(queue.items || []);
  } catch (e) {
    prioEl.innerHTML = `<p class="state-error">Nie udało się pobrać priorytetów. <button type="button" id="home-retry">Spróbuj ponownie</button></p>`;
    queueEl.innerHTML = `<p class="state-error">Nie udało się pobrać kolejki.</p>`;
    const retry = document.getElementById("home-retry");
    if (retry) retry.onclick = () => loadHome().catch((err) => toast(err.message));
    throw e;
  }

  const [agents, snap, settings] = await Promise.all([
    api("/api/v1/agents").catch(() => ({ agents: [] })),
    api("/api/v1/commander/analytics/snapshot").catch(() => null),
    api("/api/v1/commander/settings").catch(() => ({})),
  ]);
  const slaBad = (agents.agents || []).filter((a) => !a.sla_ok).length;
  const fresh = snap?.freshness?.ga4?.status || "—";
  const worker = snap?.freshness?.worker?.status || "—";
  const staleNote = fresh === "stale" || worker === "stale" ? " · Dane nieaktualne" : "";
  healthEl.textContent =
    `Agenci SLA breach: ${slaBad} · GA4: ${fresh} · Worker: ${worker}${staleNote}`;
  document.getElementById("delegat-banner").hidden = !!settings.delegat_configured;
}

let marketingFilter = "all";

const STATUS_LABELS = {
  draft: "Szkic",
  approved: "Zaplanowane",
  published: "Opublikowane",
  failed: "Nieudane",
  cancelled: "Anulowane",
  pending_approval: "Do zatwierdzenia",
  held: "Wstrzymane",
};

function humanizePublishError(publishResultRaw) {
  if (!publishResultRaw) return "Publikacja nie powiodła się";
  let pr = publishResultRaw;
  if (typeof pr === "string") {
    try {
      pr = JSON.parse(pr);
    } catch {
      return pr.slice(0, 160);
    }
  }
  if (pr.message_pl) return pr.message_pl;
  let fb = {};
  if (pr.details) {
    try {
      const parsed = typeof pr.details === "string" ? JSON.parse(pr.details) : pr.details;
      fb = parsed.error || {};
    } catch {
      fb = {};
    }
  }
  const msg = String(fb.message || pr.error || pr.message || "");
  if (fb.code === 190 || fb.error_subcode === 463 || /expired/i.test(msg)) {
    return "Token Facebook wygasł — odśwież Page Token FlexGrafik";
  }
  if (/publish_actions/i.test(msg)) {
    return "Wymagany Page Token FlexGrafik (nie User Token)";
  }
  if (/photo|image|url/i.test(msg)) {
    return "Meta nie pobrała grafiki — sprawdź udostępnianie pliku na Drive";
  }
  return msg.slice(0, 160) || "Publikacja na Facebooku nie powiodła się";
}

function statusBadgeClass(status) {
  if (status === "failed") return "status-failed";
  if (status === "published") return "status-published";
  if (status === "approved") return "status-approved";
  return "";
}

function fbPostUrl(fbPostId) {
  if (!fbPostId) return null;
  return `https://www.facebook.com/${fbPostId}`;
}

function toIsoSchedule(localValue) {
  if (!localValue) return null;
  const d = new Date(localValue);
  if (Number.isNaN(d.getTime())) return null;
  return d.toISOString();
}

function formatSchedule(iso) {
  if (!iso) return "—";
  try {
    return new Date(iso).toLocaleString("pl-PL", { dateStyle: "short", timeStyle: "short" });
  } catch {
    return iso;
  }
}

function toggleMediaField() {
  const type = document.getElementById("content-type").value;
  const show = type === "image" || type === "video";
  document.getElementById("entry-media-url").hidden = !show;
  document.getElementById("media-url-label").hidden = !show;
}

async function submitMarketingEntry(status) {
  const title = document.getElementById("entry-title").value.trim();
  const body = document.getElementById("entry-body").value.trim();
  const type = document.getElementById("content-type").value;
  const mediaUrl = document.getElementById("entry-media-url").value.trim();
  const schedLocal = document.getElementById("entry-schedule").value;
  const schedIso = toIsoSchedule(schedLocal) || new Date().toISOString();

  if (!title || !body) {
    toast("Tytuł i treść są wymagane");
    return;
  }
  if (status === "approved" && !schedLocal) {
    toast("Ustaw datę publikacji");
    return;
  }
  if ((type === "image" || type === "video") && !mediaUrl) {
    toast("Wklej link do pliku z Google Drive");
    return;
  }

  const payload = {
    platform: "facebook",
    title,
    body_nl: body,
    scheduled_at: schedIso,
    scheduled_publish_at: schedIso,
    content_type: type,
    status,
  };
  if (mediaUrl) payload.media_url = mediaUrl;

  await api("/api/v1/content-calendar", { method: "POST", body: payload });
  toast(status === "approved" ? "Zaplanowano publikację" : "Szkic zapisany");
  document.getElementById("marketing-composer").reset();
  toggleMediaField();
  loadMarketing();
}

function matchesMarketingFilter(entry) {
  if (marketingFilter === "all") return true;
  if (marketingFilter === "approved") return entry.status === "approved";
  if (marketingFilter === "draft") return entry.status === "draft";
  if (marketingFilter === "published") return entry.status === "published";
  if (marketingFilter === "failed") return entry.status === "failed";
  return true;
}

async function loadMarketing() {
  let cal;
  let agents;
  let settings;
  let fbHealth;
  try {
    [cal, agents, settings, fbHealth] = await Promise.all([
      api("/api/v1/content-calendar"),
      api("/api/v1/agents"),
      api("/api/v1/commander/settings").catch(() => ({})),
      api("/api/v1/commander/marketing/fb-health").catch(() => null),
    ]);
  } catch (e) {
    document.getElementById("calendar-entries").innerHTML =
      `<p class="state-error">Nie udało się pobrać kolejki marketingu. <button type="button" id="mkt-retry">Spróbuj ponownie</button></p>`;
    const retry = document.getElementById("mkt-retry");
    if (retry) retry.onclick = () => loadMarketing().catch((err) => toast(err.message));
    throw e;
  }

  const folderUrl = settings.marketing_gdrive_folder_url;
  const folderHint = document.getElementById("gdrive-folder-hint");
  if (folderUrl) {
    folderHint.hidden = false;
    folderHint.innerHTML = `Folder media: <a href="${folderUrl}" target="_blank" rel="noopener">COI-Marketing (Drive)</a>`;
  } else {
    folderHint.hidden = true;
  }

  const fbStrip = document.getElementById("fb-health-strip");
  if (fbHealth) {
    fbStrip.hidden = false;
    fbStrip.className = "health-strip";
    if (fbHealth.ok) fbStrip.classList.add("fb-health-ok");
    else if (fbHealth.configured) fbStrip.classList.add("fb-health-bad");
    else fbStrip.classList.add("fb-health-warn");
    const expiry = fbHealth.days_left != null
      ? ` · ważny jeszcze ${fbHealth.days_left} dni`
      : "";
    fbStrip.textContent = `Facebook: ${fbHealth.message_pl || "—"}${expiry}`;
  } else {
    fbStrip.hidden = true;
  }

  const entries = (cal.entries || []).slice().sort((a, b) => {
    const da = a.scheduled_publish_at || a.scheduled_at || "";
    const db = b.scheduled_publish_at || b.scheduled_at || "";
    return da.localeCompare(db);
  });

  const approved = entries.filter((e) => e.status === "approved");
  const drafts = entries.filter((e) => e.status === "draft");
  const failed = entries.filter((e) => e.status === "failed");
  const published = entries.filter((e) => e.status === "published");
  const next = approved.find((e) => {
    const t = e.scheduled_publish_at || e.scheduled_at;
    return t && new Date(t) > new Date();
  });
  document.getElementById("marketing-status-strip").textContent =
    `Następna: ${next ? formatSchedule(next.scheduled_publish_at || next.scheduled_at) : "—"} · Zaplanowane: ${approved.length} · Szkice: ${drafts.length} · Nieudane: ${failed.length} · Opublikowane: ${published.length}`;

  const mkt = (agents.agents || []).find((a) => a.agent_id === "marketing");
  const held = document.getElementById("held-banner");
  if (mkt?.status === "PAUSED" || (mkt?.held_count || 0) > 0) {
    held.hidden = false;
    held.textContent = `Agent marketing wstrzymany — ${mkt.held_count || 0} postów held`;
  } else {
    held.hidden = true;
  }

  const filtered = entries.filter(matchesMarketingFilter);
  const el = document.getElementById("calendar-entries");
  el.innerHTML = filtered.length
    ? filtered.map((e) => {
        const typeLabel = e.content_type || "text";
        const sched = formatSchedule(e.scheduled_publish_at || e.scheduled_at);
        const statusLabel = STATUS_LABELS[e.status] || e.status;
        const statusCls = statusBadgeClass(e.status);
        const errMsg = e.status === "failed" ? humanizePublishError(e.publish_result) : "";
        const fbUrl = fbPostUrl(e.fb_post_id);
        const actions = [];
        if (e.status === "draft") {
          actions.push(`<button type="button" data-approve="${e.entry_id}">Zaplanuj</button>`);
        }
        if (e.status === "approved") {
          actions.push(`<button type="button" data-publish="${e.entry_id}">Opublikuj teraz</button>`);
        }
        if (e.status === "failed") {
          actions.push(`<button type="button" class="primary" data-retry="${e.entry_id}">Ponów publikację</button>`);
        }
        if (e.status === "published") {
          actions.push(`<button type="button" data-unpublish="${e.entry_id}">Cofnij publikację</button>`);
        }
        if (e.status !== "published") {
          actions.push(`<button type="button" data-cancel="${e.entry_id}">Anuluj</button>`);
        }
        return `
    <article class="card approval-card${e.status === "failed" ? " severity-CRITICAL" : ""}">
      <header class="card-header">
        <strong>${e.title}</strong>
        <span class="badge ${statusCls}">${statusLabel}</span>
        <span class="badge">${typeLabel}</span>
      </header>
      <p class="meta">Publikacja: ${sched}</p>
      <p lang="nl">${(e.body_nl || "").slice(0, 160)}${(e.body_nl || "").length > 160 ? "…" : ""}</p>
      ${e.media_url ? `<p class="hint">Media: <a href="${e.media_url}" target="_blank" rel="noopener">link</a></p>` : ""}
      ${fbUrl ? `<p class="hint"><a href="${fbUrl}" target="_blank" rel="noopener">Zobacz na Facebooku</a></p>` : ""}
      ${errMsg ? `<p class="error-box" role="alert">${errMsg}</p>` : ""}
      <div class="actions">${actions.join("")}</div>
    </article>`;
      }).join("")
    : "<p>Brak wpisów — dodaj pierwszy post powyżej</p>";

  el.querySelectorAll("[data-approve]").forEach((btn) => {
    btn.onclick = async () => {
      await api(`/api/v1/content-calendar/${btn.dataset.approve}`, {
        method: "PATCH",
        body: { status: "approved" },
      });
      toast("Zaplanowano");
      showUndoBar(btn.dataset.approve);
      loadMarketing();
    };
  });
  el.querySelectorAll("[data-publish]").forEach((btn) => {
    btn.onclick = async () => {
      if (!(await confirmAction("Opublikować na Facebooku teraz?")).ok) return;
      try {
        await api(`/api/v1/content-calendar/${btn.dataset.publish}/publish`, { method: "POST", body: {} });
        toast("Opublikowano");
      } catch (err) {
        toast(String(err.message));
      }
      loadMarketing();
    };
  });
  el.querySelectorAll("[data-retry]").forEach((btn) => {
    btn.onclick = async () => {
      if (!(await confirmAction("Ponowić publikację na Facebooku?")).ok) return;
      try {
        await api(`/api/v1/content-calendar/${btn.dataset.retry}/publish`, { method: "POST", body: {} });
        toast("Opublikowano");
      } catch (err) {
        toast(String(err.message));
      }
      loadMarketing();
    };
  });
  el.querySelectorAll("[data-unpublish]").forEach((btn) => {
    btn.onclick = async () => {
      if (!(await confirmAction("Usunąć post z FB? (unpublish)")).ok) return;
      await api(`/api/v1/content-calendar/${btn.dataset.unpublish}/unpublish`, {
        method: "POST",
        body: { reason: "operator_unpublish" },
      });
      toast("Cofnięto publikację");
      loadMarketing();
    };
  });
  el.querySelectorAll("[data-cancel]").forEach((btn) => {
    btn.onclick = async () => {
      if (!(await confirmAction("Anulować wpis?")).ok) return;
      await api(`/api/v1/content-calendar/${btn.dataset.cancel}`, {
        method: "PATCH",
        body: { status: "cancelled" },
      });
      toast("Anulowano");
      loadMarketing();
    };
  });
}

document.getElementById("content-type")?.addEventListener("change", toggleMediaField);
document.getElementById("save-draft")?.addEventListener("click", () => {
  submitMarketingEntry("draft").catch((e) => toast(e.message));
});
document.getElementById("schedule-post")?.addEventListener("click", () => {
  submitMarketingEntry("approved").catch((e) => toast(e.message));
});
document.querySelectorAll("#queue-filters .chip").forEach((chip) => {
  chip.addEventListener("click", () => {
    document.querySelectorAll("#queue-filters .chip").forEach((c) => c.classList.remove("active"));
    chip.classList.add("active");
    marketingFilter = chip.dataset.filter || "all";
    loadMarketing().catch((e) => toast(e.message));
  });
});
toggleMediaField();

async function loadAnalytics() {
  const tiles = document.getElementById("analytics-tiles");
  const ordersEl = document.getElementById("orders-list");
  const leadsEl = document.getElementById("leads-list");
  tiles.innerHTML = "<p class=\"hint\">Ładowanie analityki…</p>";
  let snap;
  let orders;
  let leads;
  try {
    [snap, orders, leads] = await Promise.all([
      api("/api/v1/commander/analytics/snapshot"),
      api("/api/v1/orders"),
      api("/api/v1/leads"),
    ]);
  } catch (e) {
    tiles.innerHTML = `<p class="state-error">Nie udało się pobrać analityki. <button type="button" id="analytics-retry">Spróbuj ponownie</button></p>`;
    ordersEl.innerHTML = "";
    leadsEl.innerHTML = "";
    const retry = document.getElementById("analytics-retry");
    if (retry) retry.onclick = () => loadAnalytics().catch((err) => toast(err.message));
    throw e;
  }
  const f = snap.freshness || {};
  const entries = Object.entries(f);
  tiles.innerHTML = entries.length
    ? entries.map(([k, v]) => `
    <article class="card">
      <strong>${k.toUpperCase()}</strong>
      <p>Ostatnia sync: ${v.last_sync_at || "—"}</p>
      <span class="badge stale-${v.status} ${v.status}">${v.status === "stale" ? "nieaktualne" : v.status}</span>
      ${v.staleness_seconds != null ? `<small>${v.staleness_seconds}s temu</small>` : ""}
    </article>`).join("")
    : "<p class=\"state-empty\">Brak kafelków świeżości — spokój.</p>";
  ordersEl.innerHTML =
    (orders.orders || []).slice(0, 10).map((o) =>
      `<div>#${o.order_id} · ${o.status} · €${o.total_gross}</div>`).join("")
    || "<p class=\"state-empty\">Brak zamówień.</p>";
  leadsEl.innerHTML =
    (leads.leads || []).slice(0, 10).map((l) =>
      `<div>${l.email} · score ${l.game_score ?? "—"} · ${l.disposition || "open"}
        <button type="button" data-lead-list-disp="${l.id}" data-disp="acked">Potwierdź</button>
        <button type="button" data-lead-list-disp="${l.id}" data-disp="closed">Zamknij</button>
      </div>`).join("")
    || "<p class=\"state-empty\">Brak leadów.</p>";
  document.querySelectorAll("[data-lead-list-disp]").forEach((btn) => {
    btn.onclick = async () => {
      try {
        await api(`/api/v1/commander/leads/${btn.dataset.leadListDisp}/disposition`, {
          method: "POST",
          body: JSON.stringify({ disposition: btn.dataset.disp }),
        });
        loadAnalytics().catch((e) => toast(e.message));
      } catch (e) {
        toast(e.message || "Nie udało się zmienić statusu leada");
      }
    };
  });
}

async function loadAgents() {
  let data;
  try {
    data = await api("/api/v1/agents");
  } catch (e) {
    document.getElementById("agents-list").innerHTML =
      `<p class="state-error">Nie udało się pobrać agentów. <button type="button" id="agents-retry">Spróbuj ponownie</button></p>`;
    document.getElementById("phase-c-cards").innerHTML = "";
    const retry = document.getElementById("agents-retry");
    if (retry) retry.onclick = () => loadAgents().catch((err) => toast(err.message));
    throw e;
  }
  const agents = data.agents || [];
  document.getElementById("agents-list").innerHTML = agents.length
    ? agents.map((a) => `
    <article class="card" role="listitem">
      <strong>${a.label}</strong>
      <p>Status: ${a.status} · SLA: <span class="badge ${a.sla_ok ? "ok" : "red"}">${a.sla_ok ? "ok" : "breach"}</span></p>
      <p>Held: ${a.held_count || 0}</p>
      <p class="links">
        ${a.agent_id === "design" ? '<a href="/api/v1/design-agent/health" target="_blank" rel="noopener noreferrer">INSPIRE</a>' : ""}
        ${a.agent_id === "engineering" ? '<a href="https://os.flexgrafik.nl" target="_blank" rel="noopener noreferrer">Agent OS (AI PM)</a>' : ""}
        ${a.agent_id === "marketing" ? "<span class=\"hint\">AI Marketing</span>" : ""}
      </p>
      ${a.status === "LIVE"
        ? `<button type="button" data-pause="${a.agent_id}">Pauza</button>`
        : `<button type="button" data-resume="${a.agent_id}">Wznów</button>`}
    </article>`).join("")
    : "<p class=\"state-empty\">Brak agentów w rejestrze.</p>";

  document.getElementById("phase-c-cards").innerHTML = `
    <article class="card"><strong>AI Sprzedawca</strong><p>LIVE — widget + sales_cta</p></article>
    <article class="card"><strong>AI Marketing</strong><p>LIVE — kolejka publikacji</p></article>
    <article class="card"><strong>AI Project Manager</strong><p>LIVE — hop Agent OS</p></article>
    <article class="card"><strong>AI Customer Success</strong><p>LIVE — spawn API + kolejka HITL (COI-CS-02)</p></article>
    <article class="card"><strong>AI Asystent Zarządu</strong><p>LIVE — brief HITL</p></article>`;

  document.querySelectorAll("[data-pause]").forEach((btn) => {
    btn.onclick = async () => {
      if (!(await confirmAction("Pauzować agenta? Posty → held.")).ok) return;
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

async function loadAudit() {
  try {
    const data = await api("/api/v1/commander/audit-log?limit=30");
    document.getElementById("audit-list").innerHTML = (data.entries || []).length
      ? (data.entries || []).map((e) =>
        `<div><code>${e.ts}</code> · ${e.action} · ${e.actor_id} (${e.actor_role})</div>`).join("")
      : "<p class=\"state-empty\">Brak wpisów audytu.</p>";
  } catch (e) {
    document.getElementById("audit-list").innerHTML =
      `<p class="state-error">Nie udało się pobrać audytu. <button type="button" id="audit-retry">Spróbuj ponownie</button></p>`;
    const retry = document.getElementById("audit-retry");
    if (retry) retry.onclick = () => loadAudit().catch((err) => toast(err.message));
    throw e;
  }
}

async function loadSettings() {
  const s = await api("/api/v1/commander/settings");
  document.getElementById("delegat-email").value = s.delegat_email || "";
  document.getElementById("delegat-tg").value = s.delegat_telegram_chat_id || "";
  document.getElementById("daily-budget").value = s.daily_action_budget || 200;
  roleMap = s.commander_roles || {};
  document.getElementById("roles-list").textContent = JSON.stringify(roleMap, null, 2);
  document.getElementById("delegat-banner").hidden = !!s.delegat_configured;
}

async function refresh() {
  if (!getToken()) return;
  const active = document.querySelector(".view:not([hidden])")?.id?.replace("view-", "") || "home";
  if (active === "home") await loadHome();
  if (active === "marketing") await loadMarketing();
  if (active === "analytics") await loadAnalytics();
  if (active === "agents") await loadAgents();
  if (active === "audit") await loadAudit();
  if (active === "settings") await loadSettings();
}

async function openTicketFromDeeplink(ticketId, token) {
  const panel = document.getElementById("ticket-panel");
  const detail = document.getElementById("ticket-detail");
  try {
    const row = await api(`/api/v1/commander/tickets/${ticketId}?token=${encodeURIComponent(token)}`);
    panel.hidden = false;
    detail.innerHTML = `
      <p><strong>#${row.id}</strong> ${row.title}</p>
      <p>${row.description || ""}</p>
      <p>Status: ${row.status}</p>`;
    showView("home");
  } catch (e) {
    toast(e.message);
  }
}

function showView(name) {
  document.querySelectorAll(".view").forEach((v) => {
    const active = v.id === `view-${name}`;
    v.hidden = !active;
    v.classList.toggle("active", active);
  });
  document.querySelectorAll(".nav-btn").forEach((b) => {
    const on = b.dataset.view === name;
    b.classList.toggle("active", on);
    if (on) b.setAttribute("aria-current", "page");
    else b.removeAttribute("aria-current");
  });
}

function bindNavButtons(selector) {
  document.querySelectorAll(selector).forEach((btn, idx, all) => {
    btn.addEventListener("click", async () => {
      const view = btn.dataset.view;
      showView(view);
      try {
        await refresh();
      } catch (e) {
        toast(e.message);
      }
    });
    btn.addEventListener("keydown", (e) => {
      if (e.key !== "ArrowRight" && e.key !== "ArrowLeft") return;
      e.preventDefault();
      const i = [...all].indexOf(btn);
      const next =
        e.key === "ArrowRight" ? all[i + 1] || all[0] : all[i - 1] || all[all.length - 1];
      next.focus();
    });
  });
}

bindNavButtons("#main-nav .nav-btn");
bindNavButtons("#bottom-nav .nav-btn");

const settingsToAudit = document.getElementById("settings-to-audit");
if (settingsToAudit) {
  settingsToAudit.onclick = async () => {
    showView("audit");
    try {
      await refresh();
    } catch (e) {
      toast(e.message);
    }
  };
}

document.getElementById("auth-save").onclick = () => {
  setToken(document.getElementById("jwt-input").value.trim());
  toast("Token zapisany");
  refresh().catch((e) => toast(e.message));
};

const authToggle = document.getElementById("auth-toggle");
if (authToggle) {
  authToggle.onclick = () => {
    const body = document.getElementById("auth-body");
    setAuthExpanded(!!body?.hidden);
  };
}

document.getElementById("cs-followup-form").onsubmit = async (e) => {
  e.preventDefault();
  const orderId = document.getElementById("cs-order-id").value.trim();
  if (!orderId) {
    toast("Podaj numer zamówienia");
    return;
  }
  try {
    const res = await api("/api/v1/commander/cs/followup", {
      method: "POST",
      body: {
        order_id: orderId,
        customer_hint: document.getElementById("cs-customer").value.trim(),
        note: document.getElementById("cs-note").value.trim(),
      },
    });
    toast(`CS follow-up #${res.ticket_id} utworzony`);
    document.getElementById("cs-order-id").value = "";
    document.getElementById("cs-customer").value = "";
    document.getElementById("cs-note").value = "";
    loadHome().catch((err) => toast(err.message));
  } catch (err) {
    toast(err.message || "Nie udało się utworzyć CS follow-up");
  }
};

document.getElementById("settings-form").onsubmit = async (e) => {
  e.preventDefault();
  try {
    await api("/api/v1/commander/settings", {
      method: "PATCH",
      body: {
        delegat_email: document.getElementById("delegat-email").value,
        delegat_telegram_chat_id: document.getElementById("delegat-tg").value,
        daily_action_budget: Number(document.getElementById("daily-budget").value) || 200,
        commander_roles: roleMap,
        ui_language: "pl",
      },
    });
    toast("Ustawienia zapisane");
  } catch (err) {
    toast(err.message);
  }
};

document.getElementById("role-add").onclick = () => {
  const uid = document.getElementById("role-user").value.trim();
  const role = document.getElementById("role-pick").value;
  if (!uid) return;
  roleMap[uid] = role;
  document.getElementById("roles-list").textContent = JSON.stringify(roleMap, null, 2);
  toast(`Rola ${role} → ${uid}`);
};

document.getElementById("undo-btn").onclick = async () => {
  if (!pendingUndoEntryId) return;
  try {
    await api(`/api/v1/commander/actions/calendar/${pendingUndoEntryId}/undo`, { method: "POST" });
    toast("Cofnięto");
    document.getElementById("undo-bar").hidden = true;
    pendingUndoEntryId = null;
    clearInterval(undoTimer);
    loadMarketing();
  } catch (e) {
    toast(e.message);
  }
};

document.getElementById("audit-verify").onclick = async () => {
  try {
    const r = await api("/api/v1/commander/audit-log/verify");
    document.getElementById("audit-verify-result").textContent = JSON.stringify(r, null, 2);
  } catch (e) {
    toast(e.message);
  }
};

document.getElementById("ticket-close").onclick = () => {
  document.getElementById("ticket-panel").hidden = true;
};

document.getElementById("auth-logout").onclick = () => {
  clearToken();
  setAuthExpanded(true);
  toast("Wylogowano");
};

async function bootstrapAuth() {
  const params = new URLSearchParams(window.location.search);
  const loginCode = params.get("code");
  const legacyJwt = params.get("jwt");
  const ticketParam = params.get("ticket");
  const tokenParam = params.get("token");

  if (loginCode) {
    try {
      const data = await exchangeLoginCode(loginCode);
      setToken(data.token);
      stripAuthParamsFromUrl();
      toast("Zalogowano (Telegram)");
      await refresh();
      return;
    } catch (e) {
      stripAuthParamsFromUrl();
      toast(e.message || "Logowanie nieudane");
    }
  } else if (legacyJwt) {
    // Compatibility only — prefer ?code= one-time exchange
    setToken(legacyJwt);
    stripAuthParamsFromUrl();
    toast("Zalogowano (legacy jwt param)");
  }

  if (ticketParam && tokenParam) {
    openTicketFromDeeplink(ticketParam, tokenParam);
  } else if (ticketParam) {
    showView("home");
    toast(`Ticket #${ticketParam} — /commander lub wklej JWT`);
  }

  if (getToken()) {
    document.getElementById("jwt-input").value = "";
    updateAuthStatus();
    refresh().catch((e) => toast(e.message));
  } else {
    updateAuthStatus();
  }
}

registerServiceWorker();
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => {
    bootstrapAuth();
  });
} else {
  bootstrapAuth();
}
