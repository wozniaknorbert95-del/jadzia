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
    clearToken();
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

function toast(msg, kind = "") {
  const el = document.getElementById("toast");
  el.textContent = msg;
  el.classList.remove("toast-ok", "toast-err");
  if (kind === "ok") el.classList.add("toast-ok");
  if (kind === "err") el.classList.add("toast-err");
  el.hidden = false;
  clearTimeout(toast._timer);
  toast._timer = setTimeout(() => { el.hidden = true; }, 4000);
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

function homeSkeleton(rows = 2) {
  return `<div class="skeleton-stack" aria-busy="true" aria-label="Ładowanie">${
    Array.from({ length: rows }, () => '<div class="skeleton-card"></div>').join("")
  }</div>`;
}

function renderPriorities(items) {
  const el = document.getElementById("priorities");
  el.innerHTML = items.length
    ? items.map((p) => approvalCard(p)).join("")
    : "<p class=\"state-empty\">Brak priorytetów na dziś — spokój. Sprawdź kolejkę poniżej lub mapę systemu.</p>";
}

function leadDispositionActions(item) {
  if (item.queue_type !== "hot_lead" && item.queue_type !== "sales_cta") return "";
  const leadId = item.payload?.lead_id || item.payload?.id;
  if (!leadId) return "";
  return `
    <button type="button" class="primary" data-lead-disp="${leadId}" data-disp="acked">Potwierdź</button>
    <button type="button" class="secondary" data-lead-disp="${leadId}" data-disp="snoozed">Odłóż</button>
    <button type="button" class="danger" data-lead-disp="${leadId}" data-disp="closed">Zamknij</button>
  `;
}

function ticketDispositionActions(item) {
  if (item.queue_type !== "cs_followup") return "";
  const ticketId = item.payload?.ticket_id;
  if (!ticketId) return "";
  return `
    <button type="button" class="primary" data-ticket-disp="${ticketId}" data-disp="acked">Potwierdź</button>
    <button type="button" class="secondary" data-ticket-disp="${ticketId}" data-disp="snoozed">Odłóż</button>
    <button type="button" class="danger" data-ticket-disp="${ticketId}" data-disp="closed">Zamknij</button>
  `;
}

function queueItemActions(item) {
  return leadDispositionActions(item) + ticketDispositionActions(item);
}

function bindDispositionButtons(root, selector, idFromBtn, pathPrefix, label) {
  root.querySelectorAll(selector).forEach((btn) => {
    btn.onclick = async () => {
      const entityId = idFromBtn(btn);
      const disp = btn.dataset.disp;
      const siblings = btn.parentElement?.querySelectorAll("button") || [btn];
      siblings.forEach((b) => { b.disabled = true; });
      try {
        await api(`${pathPrefix}/${entityId}/disposition`, {
          method: "POST",
          body: JSON.stringify({ disposition: disp }),
        });
        toast(`${label} ${entityId} → ${disp}`, "ok");
        loadHome().catch((e) => toast(e.message, "err"));
      } catch (e) {
        siblings.forEach((b) => { b.disabled = false; });
        toast(e.message || `Nie udało się zmienić statusu (${label})`, "err");
      }
    };
  });
}

function renderQueue(items) {
  const filtered = items.filter((i) => i.severity !== "INFO");
  const el = document.getElementById("queue-list");
  el.innerHTML = filtered.length
    ? filtered.map((q) => approvalCard(q, queueItemActions(q))).join("")
    : "<p class=\"state-empty\">Kolejka pusta — brak CRITICAL/ACTION. Możesz utworzyć follow-up CS poniżej.</p>";
  bindDispositionButtons(
    el,
    "[data-lead-disp]",
    (btn) => btn.dataset.leadDisp,
    "/api/v1/commander/leads",
    "Lead",
  );
  bindDispositionButtons(
    el,
    "[data-ticket-disp]",
    (btn) => btn.dataset.ticketDisp,
    "/api/v1/commander/tickets",
    "Ticket",
  );
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

function bindSystemMapHops() {
  const root = document.getElementById("system-map-links");
  if (!root || root.dataset.hopsBound === "1") return;
  root.dataset.hopsBound = "1";
  root.querySelectorAll("a.map-link").forEach((link) => {
    link.addEventListener("click", () => {
      const name = link.dataset.hop || link.querySelector(".hop-label")?.textContent || "system";
      link.classList.add("is-opening");
      toast(`Otwieram: ${name} (sesja Commander zostaje)`, "ok");
      setTimeout(() => link.classList.remove("is-opening"), 1200);
    });
  });
}

async function loadHome() {
  const prioEl = document.getElementById("priorities");
  const queueEl = document.getElementById("queue-list");
  const chipsEl = document.getElementById("home-ops-chips");
  const summaryEl = document.getElementById("home-ops-summary");
  prioEl.innerHTML = homeSkeleton(2);
  queueEl.innerHTML = homeSkeleton(2);
  if (summaryEl) summaryEl.textContent = "Ładowanie ops…";
  if (chipsEl) chipsEl.innerHTML = "";

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
    prioEl.innerHTML = `<p class="state-error">Nie udało się pobrać priorytetów. <button type="button" class="primary" id="home-retry">Spróbuj ponownie</button></p>`;
    queueEl.innerHTML = `<p class="state-error">Nie udało się pobrać kolejki.</p>`;
    if (summaryEl) summaryEl.textContent = "Status częściowy — odśwież po naprawie sesji.";
    const retry = document.getElementById("home-retry");
    if (retry) retry.onclick = () => loadHome().catch((err) => toast(err.message, "err"));
    throw e;
  }

  const [agents, snap, settings, opsHealth] = await Promise.all([
    api("/api/v1/agents").catch(() => ({ agents: [] })),
    api("/api/v1/commander/analytics/snapshot").catch(() => null),
    api("/api/v1/commander/settings").catch(() => ({})),
    fetch(`${API_BASE}/worker/health`)
      .then((r) => (r.ok ? r.json() : null))
      .catch(() => null),
  ]);
  const slaBad = (agents.agents || []).filter((a) => !a.sla_ok).length;
  const fresh = snap?.freshness?.ga4?.status || "—";
  const workerFresh = snap?.freshness?.worker?.status || "—";

  const opsSev = !opsHealth
    ? "warn"
    : opsHealth.status === "healthy" && opsHealth.ssh_connection === "ok" && opsHealth.worker_loop_alive
      ? "ok"
      : "critical";
  const sshSev = opsHealth?.ssh_connection === "ok" ? "ok" : opsHealth ? "critical" : "neutral";
  const sqlSev = opsHealth?.sqlite_connection === true ? "ok" : opsHealth ? "critical" : "neutral";
  const loopSev = opsHealth?.worker_loop_alive === true ? "ok" : opsHealth ? "critical" : "neutral";
  const slaSev = slaBad > 0 ? "critical" : "ok";
  const gaSev = fresh === "fresh" || fresh === "ok" ? "ok" : fresh === "stale" ? "warn" : "neutral";

  if (chipsEl) {
    chipsEl.innerHTML = [
      sevChip("Ops", opsHealth?.status || "—", opsSev),
      sevChip("SSH", opsHealth?.ssh_connection || "—", sshSev),
      sevChip("SQLite", opsHealth?.sqlite_connection === true ? "ok" : opsHealth ? "err" : "—", sqlSev),
      sevChip("Loop", opsHealth?.worker_loop_alive === true ? "alive" : opsHealth ? "down" : "—", loopSev),
      sevChip("SLA", String(slaBad), slaSev),
      sevChip("GA4", fresh, gaSev),
    ].join("");
  }
  if (summaryEl) {
    const up = typeof opsHealth?.uptime_seconds === "number"
      ? ` · up ${Math.round(opsHealth.uptime_seconds)}s`
      : "";
    const staleNote = fresh === "stale" || workerFresh === "stale" ? " · dane nieaktualne" : "";
    summaryEl.textContent = `Worker freshness: ${workerFresh}${up}${staleNote}`;
  }
  document.getElementById("delegat-banner").hidden = !!settings.delegat_configured;
  bindSystemMapHops();
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

function setWeeklyDraftMessage(text) {
  const body = document.getElementById("weekly-draft-body");
  if (body) body.textContent = text;
}

function escHtml(s) {
  return String(s ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function sevChip(label, value, sev) {
  const cls = sev && sev !== "neutral" ? `sev-chip sev-chip--${sev}` : "sev-chip sev-chip--neutral";
  return `<span class="${cls}" role="listitem"><span class="sev-chip__label">${escHtml(label)}</span><span class="sev-chip__value">${escHtml(value)}</span></span>`;
}

function preflightSev(verdict) {
  if (verdict === "READY_FOR_GO") return { text: "GO", sev: "ok" };
  if (verdict === "BLOCKED") return { text: "NO", sev: "critical" };
  return { text: verdict || "—", sev: "warn" };
}

function breakersChip(breakers) {
  if (!breakers) return { text: "—", sev: "neutral" };
  const trips = breakers.trips || [];
  const unexpected = trips.filter((t) => t.breaker_id !== "CB_SHADOW");
  if (unexpected.length) {
    return { text: `BLOCK ${unexpected.length}`, sev: "critical" };
  }
  if (breakers.allowed) return { text: "ALLOW", sev: "ok" };
  if (trips.some((t) => t.breaker_id === "CB_SHADOW")) {
    return { text: "SHADOW", sev: "info" };
  }
  return { text: "HOLD", sev: "warn" };
}

function accuracyChip(acc) {
  if (!acc) return { text: "—", sev: "neutral" };
  const pct = acc.accuracy == null ? "n/a" : `${Math.round(Number(acc.accuracy) * 100)}%`;
  const n = acc.n_scored != null ? ` n=${acc.n_scored}` : "";
  if (acc.gate_ready) return { text: `${pct}${n}`, sev: "ok" };
  if (acc.n_scored === 0) return { text: `${pct}${n}`, sev: "warn" };
  return { text: `${pct}${n}`, sev: "warn" };
}

function fbChip(fb) {
  if (!fb) return { text: "—", sev: "neutral" };
  if (fb.ok && fb.has_read_insights) return { text: "OK", sev: "ok" };
  if (fb.ok && !fb.has_read_insights) return { text: "no insights", sev: "warn" };
  if (fb.configured) return { text: "bad", sev: "critical" };
  return { text: "unset", sev: "warn" };
}

function memoryChip(mem) {
  if (!mem) return { text: "—", sev: "neutral" };
  const src = mem.memory_source || mem.backend || "?";
  const n = mem.count != null ? ` ${mem.count}` : "";
  if (mem.ok === false) return { text: `${src}${n}`, sev: "critical" };
  if (src === "chroma") return { text: `${src}${n}`, sev: "ok" };
  return { text: `${src}${n}`, sev: "info" };
}

function renderMarketingDecisionRail({
  preflight,
  breakers,
  accuracy,
  shadow,
  brainBus,
  memory,
  fbHealth,
  heldCount,
  sessionDead,
}) {
  const chipsEl = document.getElementById("mkt-exec-chips");
  const summaryEl = document.getElementById("mkt-rail-summary");
  const forensicEl = document.getElementById("mkt-forensic-body");
  if (!chipsEl || !summaryEl || !forensicEl) return;

  if (sessionDead) {
    summaryEl.textContent = "Sesja wygasła — zaloguj, żeby zobaczyć bramkę MB (soft-fail).";
    chipsEl.innerHTML = [
      sevChip("Preflight", "—", "warn"),
      sevChip("Breakers", "—", "warn"),
      sevChip("Accuracy", "—", "warn"),
      sevChip("FB", "—", "warn"),
      sevChip("Held", "—", "warn"),
      sevChip("Memory", "—", "warn"),
    ].join("");
    forensicEl.innerHTML = `<p class="hint">Brak JWT — forensic niedostępny.</p>`;
    return;
  }

  const pf = preflightSev(preflight?.verdict);
  const br = breakersChip(breakers);
  const ac = accuracyChip(accuracy);
  const fb = fbChip(fbHealth);
  const mem = memoryChip(memory);
  const heldSev = heldCount > 0 ? "warn" : "ok";
  const mode = preflight?.mb_mode || shadow?.mb_mode || "—";

  chipsEl.innerHTML = [
    sevChip("Preflight", pf.text, pf.sev),
    sevChip("Breakers", br.text, br.sev),
    sevChip("Accuracy", ac.text, ac.sev),
    sevChip("FB", fb.text, fb.sev),
    sevChip("Held", String(heldCount ?? 0), heldSev),
    sevChip("Memory", mem.text, mem.sev),
  ].join("");

  const gate = accuracy?.gate_ready ? "gate READY" : `gate ${accuracy?.gate_reason || "not ready"}`;
  const fails = (preflight?.checks || []).filter((c) => !c.ok).map((c) => c.id);
  const failNote = fails.length ? ` · fail: ${fails.slice(0, 4).join(", ")}` : "";
  summaryEl.textContent =
    `MB ${mode} · preflight ${preflight?.verdict || "—"} · ${gate}${failNote}` +
    ` · execute = Telegram/API only (brak UI)`;

  const shadowRows = (shadow?.shadow || []).slice(0, 8);
  const events = (brainBus?.events || []).slice(0, 8);
  const flags = brainBus?.ecosystem_flags || [];
  const shadowHtml = shadowRows.length
    ? `<ul class="forensic-list">${shadowRows.map((r) => {
        const id = r.action_id || r.id || "?";
        const sev = (r.payload && r.payload.severity) || r.severity || "";
        const rule = r.heuristic_rule_id || "";
        return `<li><code>${escHtml(id)}</code> ${escHtml(sev)} ${escHtml(rule)}</li>`;
      }).join("")}</ul>`
    : `<p class="hint">Brak wpisów shadow.</p>`;
  const eventsHtml = events.length
    ? `<ul class="forensic-list">${events.map((e) => {
        const t = e.event_type || e.type || "?";
        const ts = (e.created_at || e.ts || "").toString().slice(0, 19);
        return `<li><code>${escHtml(t)}</code> ${escHtml(ts)}</li>`;
      }).join("")}</ul>`
    : `<p class="hint">Brak eventów brain-bus.</p>`;
  const flagsHtml = flags.length
    ? `<ul class="forensic-list">${flags.map((f) =>
        `<li>${escHtml(f.flag_type || f.source || "?")} · ${escHtml(f.severity || "")}</li>`
      ).join("")}</ul>`
    : `<p class="hint">Brak ecosystem flags.</p>`;
  const memLine = memory
    ? `${memory.memory_source || "?"} · count=${memory.count ?? "—"} · chroma=${memory.chroma_installed ? "yes" : "no"}`
    : "niedostępne";

  forensicEl.innerHTML = `
    <div class="forensic-section"><h4>Shadow (last ${shadowRows.length})</h4>${shadowHtml}</div>
    <div class="forensic-section"><h4>Brain-bus events</h4>${eventsHtml}</div>
    <div class="forensic-section"><h4>Ecosystem flags</h4>${flagsHtml}</div>
    <div class="forensic-section"><h4>Memory</h4><p class="hint">${escHtml(memLine)}</p></div>
  `;
}

async function loadMarketing() {
  const draftBody = document.getElementById("weekly-draft-body");
  if (draftBody) draftBody.textContent = "Ładowanie draftu…";
  const railSummary = document.getElementById("mkt-rail-summary");
  if (railSummary) railSummary.textContent = "Ładowanie bramki MB…";

  let calErr = null;
  const [
    cal,
    agents,
    settings,
    fbHealth,
    preflight,
    breakers,
    accuracy,
    shadow,
    brainBus,
    memory,
  ] = await Promise.all([
    api("/api/v1/content-calendar").catch((e) => {
      calErr = e;
      return { entries: [] };
    }),
    api("/api/v1/agents").catch(() => ({ agents: [] })),
    api("/api/v1/commander/settings").catch(() => ({})),
    api("/api/v1/commander/marketing/fb-health").catch(() => null),
    api("/api/v1/commander/marketing/propose-preflight").catch(() => null),
    api("/api/v1/commander/marketing/breakers").catch(() => null),
    api("/api/v1/commander/marketing/shadow/accuracy").catch(() => null),
    api("/api/v1/commander/marketing/shadow?limit=12").catch(() => null),
    api("/api/v1/commander/marketing/brain-bus?limit=12").catch(() => null),
    api("/api/v1/commander/marketing/memory/status").catch(() => null),
  ]);

  const sessionDead = !getToken()
    || (calErr && String(calErr.message || "").includes("Sesja wygasła"));

  const mktAgent = (agents.agents || []).find((a) => a.agent_id === "marketing");
  const heldCount = mktAgent?.held_count || 0;

  renderMarketingDecisionRail({
    preflight,
    breakers,
    accuracy,
    shadow,
    brainBus,
    memory,
    fbHealth,
    heldCount,
    sessionDead,
  });

  const folderUrl = settings.marketing_gdrive_folder_url;
  const folderHint = document.getElementById("gdrive-folder-hint");
  if (folderUrl) {
    folderHint.hidden = false;
    folderHint.innerHTML = `Folder media: <a href="${folderUrl}" target="_blank" rel="noopener">COI-Marketing (Drive)</a>`;
  } else {
    folderHint.hidden = true;
  }

  const fbStrip = document.getElementById("fb-health-strip");
  if (sessionDead) {
    fbStrip.hidden = false;
    fbStrip.className = "health-strip fb-health-warn";
    fbStrip.textContent = "Facebook: sesja wygasła — zaloguj ponownie (nie sprawdzono tokenu)";
  } else if (fbHealth) {
    fbStrip.hidden = false;
    fbStrip.className = "health-strip";
    const hasInsights = !!fbHealth.has_read_insights;
    if (fbHealth.ok && hasInsights) fbStrip.classList.add("fb-health-ok");
    else if (fbHealth.ok && !hasInsights) fbStrip.classList.add("fb-health-warn");
    else if (fbHealth.configured) fbStrip.classList.add("fb-health-bad");
    else fbStrip.classList.add("fb-health-warn");
    const expiry = fbHealth.days_left != null
      ? ` · ważny jeszcze ${fbHealth.days_left} dni`
      : "";
    const insightsChip = hasInsights ? "insights: OK" : "insights: brak (read_insights)";
    fbStrip.textContent =
      `Facebook: ${fbHealth.message_pl || "—"} · ${insightsChip}${expiry}`;
  } else {
    fbStrip.hidden = true;
  }

  try {
    if (sessionDead) {
      setWeeklyDraftMessage("Sesja wygasła — Telegram /commander lub wklej token (Sesja).");
    } else {
      await renderWeeklyDraft();
    }
  } catch (e) {
    const msg = String(e.message || "");
    setWeeklyDraftMessage(
      msg.includes("Sesja wygasła")
        ? "Sesja wygasła — Telegram /commander lub wklej token (Sesja)."
        : "Draft niedostępny — spróbuj Odśwież.",
    );
  }

  if (calErr) {
    document.getElementById("calendar-entries").innerHTML =
      `<p class="state-error">${sessionDead ? "Sesja wygasła — zaloguj ponownie." : "Nie udało się pobrać kolejki marketingu."}
 <button type="button" id="mkt-retry">Spróbuj ponownie</button></p>`;
    const retry = document.getElementById("mkt-retry");
    if (retry) retry.onclick = () => loadMarketing().catch((err) => toast(err.message));
    document.getElementById("marketing-status-strip").textContent = "—";
    document.getElementById("held-banner").hidden = true;
    if (sessionDead) toast(calErr.message || "Sesja wygasła", "err");
    return;
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

  const mkt = mktAgent;
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

function _fmtDraftVal(v) {
  if (v == null || v === "") return "—";
  if (typeof v === "number") {
    if (Math.abs(v - Math.round(v)) < 1e-9) return String(Math.round(v));
    return v.toFixed(2);
  }
  return String(v);
}

async function renderWeeklyDraft() {
  const body = document.getElementById("weekly-draft-body");
  if (!body) return;
  let draft;
  try {
    draft = await api("/api/v1/commander/marketing/weekly-draft");
  } catch (e) {
    const msg = String(e.message || "");
    body.textContent = msg.includes("Sesja wygasła")
      ? "Sesja wygasła — Telegram /commander lub wklej token (Sesja)."
      : "Nie udało się pobrać draftu.";
    throw e;
  }
  const k = draft.kpis || {};
  body.innerHTML = `
    <p><strong>${draft.iso_week || "—"}</strong> · ${draft.campaign || "—"}</p>
    <ul class="weekly-draft-kpis">
      <li>Leads: ${_fmtDraftVal(k.leads)} (open ${_fmtDraftVal(k.leads_open)})</li>
      <li>Spend / CPL: — <span class="hint">(Ads Manager)</span></li>
      <li>Purchases≈orders: ${_fmtDraftVal(k.purchases)}</li>
      <li>Margin net: ${_fmtDraftVal(k.margin_net_sum)}</li>
      <li>Attr coverage %: ${_fmtDraftVal(k.attribution_coverage_pct)}</li>
      <li>Organic ER baseline: ${_fmtDraftVal(k.organic_er_baseline_30d)}</li>
      <li>Decyzja OS: — <span class="hint">(HITL — nie auto HOLD/KILL)</span></li>
    </ul>`;
}

function renderDataHealth(health) {
  const overallEl = document.getElementById("dtl-overall");
  const freshEl = document.getElementById("dtl-freshness");
  const marginEl = document.getElementById("dtl-margin");
  const flagsEl = document.getElementById("dtl-flags");
  const driversEl = document.getElementById("dtl-drivers");
  const parksEl = document.getElementById("dtl-parks");
  const organicEl = document.getElementById("dtl-organic");
  if (!overallEl || !freshEl || !marginEl || !flagsEl) return;

  const overall = health.overall_status || "—";
  const qs = health.quality_summary || {};
  overallEl.innerHTML = `DTL overall: <span class="badge ${overall}">${overall}</span>
    · flags: ${qs.active_total ?? 0}
    · red/critical: ${qs.critical_or_red ?? 0}
    · info: ${qs.info ?? 0}`;

  if (driversEl) {
    const drivers = health.drivers || [];
    driversEl.innerHTML = drivers.length
      ? drivers.map((d) => {
        const sev = d.severity || "amber";
        const label = d.source || d.kind || "driver";
        const msg = d.message || d.reason || "";
        return `<div><span class="badge ${sev}">${sev}</span> · ${label}: ${msg}</div>`;
      }).join("")
      : "<p class=\"state-empty\">Brak driverów — overall czysty.</p>";
  }

  if (parksEl) {
    const parks = health.conscious_parks || [];
    parksEl.innerHTML = parks.length
      ? parks.map((p) =>
        `<div><span class="badge info">${p.status || "PARK"}</span> · <strong>${p.id || "?"}</strong>: ${p.reason || ""}</div>`
      ).join("")
      : "<p class=\"state-empty\">Brak świadomych parków.</p>";
  }

  if (organicEl) {
    const org = health.facebook_organic || {};
    const insights = org.has_read_insights === true
      ? "OK"
      : org.has_read_insights === false
        ? "brak"
        : "—";
    organicEl.textContent =
      `FB organic: reason=${org.reason || "—"} · read_insights=${insights}` +
      (org.ingest_status ? ` · ingest=${org.ingest_status}` : "");
  }

  const f = health.freshness || {};
  const entries = Object.entries(f);
  freshEl.innerHTML = entries.length
    ? entries.map(([k, v]) => `
    <article class="card">
      <strong>${k}</strong>
      <p>Sync: ${v.last_sync_at || "—"}</p>
      <span class="badge ${v.status}">${v.status}</span>
      ${v.ingest_status ? `<small>ingest=${v.ingest_status}</small>` : ""}
    </article>`).join("")
    : "<p class=\"state-empty\">Brak źródeł DTL — uruchom ingest.</p>";

  const m = health.margin_coverage || {};
  marginEl.textContent =
    `Zamówienia: ${m.orders_total ?? 0} · margin facts: ${m.margin_facts ?? 0} · coverage: ${m.coverage_pct ?? 0}%`;

  const flags = health.quality_flags || [];
  flagsEl.innerHTML = flags.length
    ? flags.map((fl) =>
      `<div><span class="badge ${fl.severity}">${fl.severity}</span> · ${fl.source}/${fl.flag_type}: ${fl.message}</div>`
    ).join("")
    : "<p class=\"state-empty\">Brak aktywnych flag jakości.</p>";
}

function kpiTile(label, value, delta, sev) {
  const border = sev === "ok" ? "decision-card--ok"
    : sev === "warn" ? "decision-card--warn"
      : sev === "critical" ? "decision-card--critical"
        : "";
  return `<article class="kpi-tile ${border}" role="listitem">
    <span class="kpi-tile__value">${escHtml(value)}</span>
    <span class="kpi-tile__label">${escHtml(label)}</span>
    ${delta ? `<span class="kpi-tile__delta">${escHtml(delta)}</span>` : ""}
  </article>`;
}

async function loadAnalytics() {
  const tiles = document.getElementById("analytics-tiles");
  const kpiEl = document.getElementById("analytics-kpi-tiles");
  const ordersEl = document.getElementById("orders-list");
  const leadsEl = document.getElementById("leads-list");
  tiles.innerHTML = "<p class=\"hint\">Ładowanie analityki…</p>";
  if (kpiEl) kpiEl.innerHTML = "<p class=\"hint\">…</p>";
  let snap;
  let orders;
  let leads;
  let health;
  let draft;
  try {
    [snap, orders, leads, health, draft] = await Promise.all([
      api("/api/v1/commander/analytics/snapshot"),
      api("/api/v1/orders"),
      api("/api/v1/leads"),
      api("/api/v1/commander/marketing/data-health"),
      api("/api/v1/commander/marketing/weekly-draft").catch(() => null),
    ]);
  } catch (e) {
    tiles.innerHTML = `<p class="state-error">Nie udało się pobrać analityki. <button type="button" id="analytics-retry">Spróbuj ponownie</button></p>`;
    ordersEl.innerHTML = "";
    leadsEl.innerHTML = "";
    if (kpiEl) kpiEl.innerHTML = "";
    const retry = document.getElementById("analytics-retry");
    if (retry) retry.onclick = () => loadAnalytics().catch((err) => toast(err.message));
    throw e;
  }

  const k = draft?.kpis || {};
  const overall = (health?.overall_status || "—").toLowerCase();
  const overallSev = overall === "green" || overall === "ok" ? "ok"
    : overall === "red" || overall === "critical" ? "critical"
      : overall === "amber" || overall === "yellow" ? "warn" : "neutral";
  const org = health?.facebook_organic || {};
  const margin = health?.margin_coverage || health?.margin || {};
  const marginPct = margin.coverage_pct ?? k.attribution_coverage_pct ?? "—";
  if (kpiEl) {
    kpiEl.innerHTML = [
      kpiTile("Leads", _fmtDraftVal(k.leads), `open ${_fmtDraftVal(k.leads_open)}`, "info"),
      kpiTile("Margin cov.", `${_fmtDraftVal(marginPct)}${typeof marginPct === "number" ? "%" : ""}`, null, "info"),
      kpiTile("Organic", org.reason || org.ingest_status || "—", org.has_read_insights ? "insights OK" : "no insights", org.has_read_insights ? "ok" : "warn"),
      kpiTile("DTL", health?.overall_status || "—", null, overallSev),
    ].join("");
  }

  const f = snap.freshness || {};
  const entries = Object.entries(f);
  tiles.innerHTML = entries.length
    ? entries.map(([key, v]) => `
    <article class="card">
      <strong>${key.toUpperCase()}</strong>
      <p>Ostatnia sync: ${v.last_sync_at || "—"}</p>
      <span class="badge stale-${v.status} ${v.status}">${v.status === "stale" ? "nieaktualne" : v.status}</span>
      ${v.staleness_seconds != null ? `<small>${v.staleness_seconds}s temu</small>` : ""}
    </article>`).join("")
    : "<p class=\"state-empty\">Brak kafelków świeżości — spokój.</p>";

  renderDataHealth(health || {});

  const orderRows = (orders.orders || []).slice(0, 10);
  ordersEl.innerHTML = orderRows.length
    ? orderRows.map((o) =>
      `<tr><td>#${escHtml(o.order_id)}</td><td><span class="badge">${escHtml(o.status)}</span></td><td>€${escHtml(o.total_gross)}</td></tr>`).join("")
    : "<tr><td colspan=\"3\" class=\"hint\">Brak zamówień.</td></tr>";

  const leadRows = (leads.leads || []).slice(0, 10);
  leadsEl.innerHTML = leadRows.length
    ? leadRows.map((l) =>
      `<tr>
        <td>${escHtml(l.email)}</td>
        <td>${escHtml(l.game_score ?? "—")}</td>
        <td><span class="badge">${escHtml(l.disposition || "open")}</span></td>
        <td>
          <button type="button" data-lead-list-disp="${escHtml(l.id)}" data-disp="acked">Potwierdź</button>
          <button type="button" data-lead-list-disp="${escHtml(l.id)}" data-disp="closed">Zamknij</button>
        </td>
      </tr>`).join("")
    : "<tr><td colspan=\"4\" class=\"hint\">Brak leadów.</td></tr>";
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

document.getElementById("dtl-refresh-ingest")?.addEventListener("click", async () => {
  try {
    toast("DTL ingest…");
    await api("/api/v1/commander/marketing/dtl/ingest", { method: "POST", body: {} });
    toast("DTL ingest OK");
    await loadAnalytics();
  } catch (e) {
    toast(e.message || "DTL ingest failed");
  }
});

document.getElementById("weekly-draft-refresh")?.addEventListener("click", async () => {
  try {
    toast("Weekly draft…");
    await renderWeeklyDraft();
    toast("Draft OK");
  } catch (e) {
    toast(e.message || "Draft failed");
  }
});

async function loadAgents() {
  const listEl = document.getElementById("agents-list");
  const mapEl = document.getElementById("ai-os-map");
  listEl.innerHTML = "<p class=\"hint\">Ładowanie agentów…</p>";
  if (mapEl) mapEl.innerHTML = "";
  let data;
  let accuracy;
  let breakers;
  try {
    [data, accuracy, breakers] = await Promise.all([
      api("/api/v1/agents"),
      api("/api/v1/commander/marketing/shadow/accuracy").catch(() => null),
      api("/api/v1/commander/marketing/breakers").catch(() => null),
    ]);
  } catch (e) {
    listEl.innerHTML =
      `<p class="state-error">Nie udało się pobrać agentów. <button type="button" id="agents-retry">Spróbuj ponownie</button></p>`;
    if (mapEl) mapEl.innerHTML = "";
    const retry = document.getElementById("agents-retry");
    if (retry) retry.onclick = () => loadAgents().catch((err) => toast(err.message));
    throw e;
  }
  const agents = data.agents || [];
  const byId = Object.fromEntries(agents.map((a) => [a.agent_id, a]));

  listEl.innerHTML = agents.length
    ? agents.map((a) => {
      const next = a.next_expected_run
        ? formatSchedule(a.next_expected_run)
        : "—";
      const last = a.last_run_at ? formatSchedule(a.last_run_at) : "—";
      return `
    <article class="card decision-card ${a.sla_ok ? "decision-card--ok" : "decision-card--critical"}" role="listitem">
      <strong>${escHtml(a.label)}</strong>
      <p>${sevChip("Status", a.status, a.status === "LIVE" ? "ok" : "warn")}
         ${sevChip("SLA", a.sla_ok ? "ok" : "breach", a.sla_ok ? "ok" : "critical")}</p>
      <p class="hint">Last: ${escHtml(last)} · Next: ${escHtml(next)} · Held: ${a.held_count || 0}</p>
      <p class="links">
        ${a.agent_id === "design" ? '<a href="/api/v1/design-agent/health" target="_blank" rel="noopener noreferrer">INSPIRE health</a>' : ""}
        ${a.agent_id === "marketing" ? "<span class=\"hint\">organic HITL</span>" : ""}
      </p>
      ${a.status === "LIVE"
        ? `<button type="button" data-pause="${escHtml(a.agent_id)}">Pauza</button>`
        : `<button type="button" data-resume="${escHtml(a.agent_id)}">Wznów</button>`}
    </article>`;
    }).join("")
    : "<p class=\"state-empty\">Brak agentów w rejestrze.</p>";

  const mb = byId.marketing_brain || byId.marketing;
  const accPct = accuracy?.accuracy == null ? "n/a" : `${Math.round(Number(accuracy.accuracy) * 100)}%`;
  const br = breakersChip(breakers);
  const sales = byId.sales;
  const ops = byId.operations;
  const analytics = byId.analytics;
  const design = byId.design;

  if (mapEl) {
    mapEl.innerHTML = [
      `<article class="card"><strong>AI Sprzedawca</strong>
        <p>${sevChip("Agent", sales?.status || "—", sales?.status === "LIVE" ? "ok" : "warn")}
           ${sevChip("SLA", sales?.sla_ok ? "ok" : "breach", sales?.sla_ok ? "ok" : "critical")}</p>
        <p class="hint">Widget + sales CTA · next ${escHtml(sales?.next_expected_run ? formatSchedule(sales.next_expected_run) : "—")}</p></article>`,
      `<article class="card"><strong>AI Marketing / MB</strong>
        <p>${sevChip("Agent", mb?.status || "—", mb?.status === "LIVE" ? "ok" : "warn")}
           ${sevChip("Accuracy", accPct, accuracy?.gate_ready ? "ok" : "warn")}
           ${sevChip("Breakers", br.text, br.sev)}</p>
        <p class="hint">Organic HITL w Commander · execute = TG/API only</p></article>`,
      `<article class="card"><strong>AI Project Manager</strong>
        <p>${sevChip("Hop", "Agent OS", "info")}</p>
        <p class="links"><a href="https://os.flexgrafik.nl" target="_blank" rel="noopener">os.flexgrafik.nl</a> · Basic Auth</p></article>`,
      `<article class="card"><strong>AI Customer Success</strong>
        <p>${sevChip("Ops", ops?.status || "—", ops?.status === "LIVE" ? "ok" : "warn")}
           ${sevChip("SLA", ops?.sla_ok ? "ok" : "breach", ops?.sla_ok ? "ok" : "critical")}</p>
        <p class="hint">CS follow-up na Start · next ${escHtml(ops?.next_expected_run ? formatSchedule(ops.next_expected_run) : "—")}</p></article>`,
      `<article class="card"><strong>AI Asystent / Design</strong>
        <p>${sevChip("Analytics", analytics?.status || "—", analytics?.status === "LIVE" ? "ok" : "warn")}
           ${sevChip("Design", design?.status || "—", design?.status === "LIVE" ? "ok" : "warn")}</p>
        <p class="links"><a href="/api/v1/design-agent/health" target="_blank" rel="noopener">DA health</a></p></article>`,
    ].join("");
  }

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

function renderRolesList(map) {
  const el = document.getElementById("roles-list");
  if (!el) return;
  const entries = Object.entries(map || {});
  el.innerHTML = entries.length
    ? entries.map(([uid, role]) => `<li><code>${escHtml(uid)}</code> · ${escHtml(role)}</li>`).join("")
    : "<li class=\"hint\">Brak przypisanych ról.</li>";
}

async function loadAudit() {
  const banner = document.getElementById("audit-verify-banner");
  try {
    const data = await api("/api/v1/commander/audit-log?limit=30");
    document.getElementById("audit-list").innerHTML = (data.entries || []).length
      ? (data.entries || []).map((e) => {
        const hash = (e.hash || e.entry_hash || "").toString();
        const short = hash ? hash.slice(0, 10) : "—";
        return `<div><code>${escHtml((e.ts || "").toString().slice(0, 19))}</code> · ${escHtml(e.action)} · ${escHtml(e.actor_id)} (${escHtml(e.actor_role)}) · <code>${escHtml(short)}</code></div>`;
      }).join("")
      : "<p class=\"state-empty\">Brak wpisów audytu.</p>";
    if (banner && !banner.classList.contains("audit-banner--ok") && !banner.classList.contains("audit-banner--fail")) {
      banner.className = "audit-banner audit-banner--info";
      banner.textContent = "Naciśnij „Weryfikuj łańcuch” aby potwierdzić hash-chain.";
    }
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
  renderRolesList(roleMap);
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
bindSystemMapHops();

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
    toast("Podaj numer zamówienia", "err");
    return;
  }
  const spawnBtn = document.getElementById("cs-spawn-btn");
  if (spawnBtn) spawnBtn.disabled = true;
  try {
    const res = await api("/api/v1/commander/cs/followup", {
      method: "POST",
      body: {
        order_id: orderId,
        customer_hint: document.getElementById("cs-customer").value.trim(),
        note: document.getElementById("cs-note").value.trim(),
      },
    });
    toast(`CS follow-up #${res.ticket_id} utworzony`, "ok");
    document.getElementById("cs-order-id").value = "";
    document.getElementById("cs-customer").value = "";
    document.getElementById("cs-note").value = "";
    loadHome().catch((err) => toast(err.message, "err"));
  } catch (err) {
    toast(err.message || "Nie udało się utworzyć CS follow-up", "err");
  } finally {
    if (spawnBtn) spawnBtn.disabled = false;
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
  renderRolesList(roleMap);
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

function setMoreSheetOpen(open) {
  const sheet = document.getElementById("more-sheet");
  if (!sheet) return;
  sheet.hidden = !open;
  sheet.classList.toggle("is-open", !!open);
}

document.getElementById("open-more-sheet")?.addEventListener("click", () => setMoreSheetOpen(true));
document.getElementById("more-sheet-close")?.addEventListener("click", () => setMoreSheetOpen(false));
document.getElementById("more-to-audit")?.addEventListener("click", async () => {
  setMoreSheetOpen(false);
  showView("audit");
  try {
    await refresh();
  } catch (e) {
    toast(e.message);
  }
});

document.getElementById("audit-verify").onclick = async () => {
  const banner = document.getElementById("audit-verify-banner");
  const raw = document.getElementById("audit-verify-result");
  try {
    const r = await api("/api/v1/commander/audit-log/verify");
    if (raw) raw.textContent = JSON.stringify(r, null, 2);
    const ok = r.ok === true || r.valid === true || r.status === "ok" || r.passed === true;
    const fail = r.ok === false || r.valid === false || r.status === "fail" || r.passed === false;
    if (banner) {
      if (ok) {
        banner.className = "audit-banner audit-banner--ok";
        banner.textContent = `PASS — łańcuch OK${r.entries_checked != null ? ` · ${r.entries_checked} entries` : ""}`;
      } else if (fail) {
        banner.className = "audit-banner audit-banner--fail";
        banner.textContent = `FAIL — ${r.error || r.reason || "hash mismatch / broken chain"}`;
      } else {
        banner.className = "audit-banner audit-banner--info";
        banner.textContent = `Verify done — zobacz forensic JSON`;
      }
    }
    toast(ok ? "Audyt PASS" : fail ? "Audyt FAIL" : "Verify OK");
  } catch (e) {
    if (banner) {
      banner.className = "audit-banner audit-banner--fail";
      banner.textContent = `FAIL — ${e.message || "verify error"}`;
    }
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
