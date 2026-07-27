const _apiOverride = new URLSearchParams(window.location.search).get("api");
const API_BASE = (_apiOverride && /^https:\/\/api\.zzpackage\.flexgrafik\.nl\/?$/.test(_apiOverride))
  ? _apiOverride.replace(/\/$/, "")
  : window.location.origin;
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
  // Only explicit breach (false). null/undefined = untracked n/a — not Start noise.
  const slaBad = (agents.agents || []).filter((a) => a.sla_ok === false).length;
  const fresh = snap?.freshness?.ga4?.status || "—";
  // Pipeline freshness = worst of DTL/health clocks (not Dowódca session activity).
  const pipelineFresh = worstFreshStatus(
    snap?.freshness?.ga4?.status,
    snap?.freshness?.orders?.status,
    snap?.freshness?.leads?.status,
    snap?.freshness?.worker?.status,
  );

  const opsSev = !opsHealth
    ? "warn"
    : opsHealth.status === "healthy" && opsHealth.ssh_connection === "ok" && opsHealth.worker_loop_alive
      ? "ok"
      : "critical";
  const sshSev = opsHealth?.ssh_connection === "ok" ? "ok" : opsHealth ? "critical" : "neutral";
  const sqlSev = opsHealth?.sqlite_connection === true ? "ok" : opsHealth ? "critical" : "neutral";
  const loopSev = opsHealth?.worker_loop_alive === true ? "ok" : opsHealth ? "critical" : "neutral";
  const freshSev = freshnessSev(pipelineFresh);
  const slaSev = slaBad > 0 ? "critical" : "ok";
  const gaSev = fresh === "fresh" || fresh === "ok" ? "ok" : fresh === "stale" ? "warn" : "neutral";

  if (chipsEl) {
    chipsEl.innerHTML = [
      sevChip("Ops", opsHealth?.status || "—", opsSev),
      sevChip("SSH", opsHealth?.ssh_connection || "—", sshSev),
      sevChip("SQLite", opsHealth?.sqlite_connection === true ? "ok" : opsHealth ? "err" : "—", sqlSev),
      sevChip("Loop", opsHealth?.worker_loop_alive === true ? "alive" : opsHealth ? "down" : "—", loopSev),
      sevChip("Freshness", pipelineFresh, freshSev),
      sevChip("SLA", slaBad > 0 ? `bad: ${slaBad}` : "0", slaSev),
      sevChip("GA4", fresh, gaSev),
    ].join("");
  }
  if (summaryEl) {
    const up = typeof opsHealth?.uptime_seconds === "number"
      ? ` · up ${Math.round(opsHealth.uptime_seconds)}s`
      : "";
    const worst = worstSev(opsSev, sshSev, sqlSev, loopSev, freshSev, slaSev, gaSev);
    const attention = [];
    if (freshSev === "critical" || freshSev === "warn") attention.push(`freshness ${pipelineFresh}`);
    if (slaSev === "critical") attention.push(`SLA bad ${slaBad}`);
    if (opsSev === "critical" || opsSev === "warn") attention.push(`ops ${opsHealth?.status || "—"}`);
    if (sshSev === "critical") attention.push("SSH");
    if (sqlSev === "critical") attention.push("SQLite");
    if (loopSev === "critical") attention.push("loop");
    if (gaSev === "warn" || gaSev === "critical") attention.push(`GA4 ${fresh}`);
    summaryEl.textContent = worst === "ok" || worst === "neutral"
      ? `Ops: OK${up}`
      : `Ops: UWAGA — ${attention.slice(0, 3).join(" · ") || worst}${up}`;
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

function sevChip(label, value, sev, title) {
  const cls = sev && sev !== "neutral" ? `sev-chip sev-chip--${sev}` : "sev-chip sev-chip--neutral";
  const tip = title ? ` title="${escHtml(title)}"` : "";
  return `<span class="${cls}" role="listitem"${tip}><span class="sev-chip__label">${escHtml(label)}</span><span class="sev-chip__value">${escHtml(value)}</span></span>`;
}

function sevRank(sev) {
  if (sev === "critical") return 3;
  if (sev === "warn") return 2;
  if (sev === "info") return 1;
  return 0;
}

function worstSev(...sevs) {
  return sevs.reduce((acc, s) => (sevRank(s) > sevRank(acc) ? s : acc), "ok");
}

function freshnessSev(status) {
  const s = String(status || "").toLowerCase();
  if (s === "red" || s === "critical") return "critical";
  if (s === "stale" || s === "amber" || s === "warn" || s === "yellow") return "warn";
  if (s === "ok" || s === "fresh" || s === "green") return "ok";
  return "neutral";
}

function worstFreshStatus(...statuses) {
  const rank = { red: 3, critical: 3, stale: 3, amber: 2, warn: 2, yellow: 2, ok: 1, fresh: 1, green: 1 };
  let worst = "—";
  let worstRank = 0;
  for (const raw of statuses) {
    if (!raw || raw === "—") continue;
    const s = String(raw).toLowerCase();
    const r = rank[s] || 0;
    if (r > worstRank) {
      worstRank = r;
      worst = s;
    }
  }
  return worst;
}

function isProposeMode(mode) {
  const m = String(mode || "").toLowerCase();
  return m === "propose" || m === "shadow";
}

function preflightSev(verdict, mbMode) {
  if (isProposeMode(mbMode)) {
    return {
      text: "N/A",
      sev: "info",
      title: "gate cutover; runtime=propose (execute = Telegram/API only)",
    };
  }
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

  const mode = preflight?.mb_mode || shadow?.mb_mode || "—";
  const pf = preflightSev(preflight?.verdict, mode);
  const br = breakersChip(breakers);
  const ac = accuracyChip(accuracy);
  const fb = fbChip(fbHealth);
  const mem = memoryChip(memory);
  const heldSev = heldCount > 0 ? "warn" : "ok";

  chipsEl.innerHTML = [
    sevChip("Preflight", pf.text, pf.sev, pf.title),
    sevChip("Breakers", br.text, br.sev),
    sevChip("Accuracy", ac.text, ac.sev),
    sevChip("FB", fb.text, fb.sev),
    sevChip("Held", String(heldCount ?? 0), heldSev),
    sevChip("Memory", mem.text, mem.sev),
  ].join("");

  const gate = accuracy?.gate_ready ? "gate READY" : `gate ${accuracy?.gate_reason || "not ready"}`;
  if (isProposeMode(mode)) {
    const cutover = preflight?.verdict || "—";
    summaryEl.textContent =
      `runtime: propose · cutover: ${cutover} (oczekiwane w propose) · ${gate}` +
      ` · execute = Telegram/API only (brak UI)`;
  } else {
    const fails = (preflight?.checks || []).filter((c) => !c.ok).map((c) => c.id);
    const failNote = fails.length ? ` · fail: ${fails.slice(0, 4).join(", ")}` : "";
    summaryEl.textContent =
      `MB ${mode} · preflight ${preflight?.verdict || "—"} · ${gate}${failNote}` +
      ` · execute = Telegram/API only (brak UI)`;
  }

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
  } else {
    // M4: Decision Rail owns FB chip — avoid duplicate strip when rail is live
    fbStrip.hidden = true;
    fbStrip.textContent = "";
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
        const smoke = /smoke|safe to delete|debug/i.test(`${e.title || ""} ${e.body_nl || ""}`);
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
        ${smoke ? '<span class="badge" title="test/smoke entry">smoke</span>' : ""}
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

function renderDataHealth(health, opts = {}) {
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
  const overallLow = String(overall).toLowerCase();
  const pipelineOk = overallLow === "ok" || overallLow === "green";
  if (opts.factsStale && pipelineOk) {
    overallEl.innerHTML = `DTL: <span class="badge amber">pipeline OK · facts STALE</span>
    · flags: ${qs.active_total ?? 0}
    · red/critical: ${qs.critical_or_red ?? 0}
    · info: ${qs.info ?? 0}`;
  } else {
    overallEl.innerHTML = `DTL overall: <span class="badge ${overall}">${overall}</span>
    · flags: ${qs.active_total ?? 0}
    · red/critical: ${qs.critical_or_red ?? 0}
    · info: ${qs.info ?? 0}`;
  }

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

function humanizeOrganicReason(reason) {
  const map = {
    insights_scope_missing: "Brak insights",
    no_published_posts: "Brak postów",
    proxy_er: "Proxy ER",
    ok: "OK",
  };
  const key = String(reason || "");
  return map[key] || (key ? key.replace(/_/g, " ") : "—");
}

function factsStaleFromSnap(snap) {
  const f = snap?.freshness || {};
  return ["orders", "leads"].some((k) => {
    const s = String(f[k]?.status || "").toLowerCase();
    return s === "red" || s === "stale" || s === "critical";
  });
}

function kpiTile(label, value, delta, sev, title) {
  const border = sev === "ok" ? "decision-card--ok"
    : sev === "warn" ? "decision-card--warn"
      : sev === "critical" ? "decision-card--critical"
        : "";
  const tip = title ? ` title="${escHtml(title)}"` : "";
  return `<article class="kpi-tile ${border}" role="listitem"${tip}>
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
  const factsStale = factsStaleFromSnap(snap);
  const orgRaw = org.reason || org.ingest_status || "";
  const orgHuman = humanizeOrganicReason(orgRaw || "—");
  const dtlValue = factsStale && (overall === "ok" || overall === "green")
    ? "pipeline OK · facts STALE"
    : (health?.overall_status || "—");
  const dtlSev = factsStale ? "warn" : overallSev;
  if (kpiEl) {
    kpiEl.innerHTML = [
      kpiTile("Leads", _fmtDraftVal(k.leads), `open ${_fmtDraftVal(k.leads_open)}`, "info"),
      kpiTile("Margin cov.", `${_fmtDraftVal(marginPct)}${typeof marginPct === "number" ? "%" : ""}`, null, "info"),
      kpiTile("Organic", orgHuman, org.has_read_insights ? "insights OK" : "no insights", org.has_read_insights ? "ok" : "warn", orgRaw || undefined),
      kpiTile("DTL", dtlValue, null, dtlSev),
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

  renderDataHealth(health || {}, { factsStale });

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
      const hasLast = !!a.last_run_at;
      const statusLabel = a.status === "LIVE" && !hasLast ? "configured" : a.status;
      const statusSev = statusLabel === "LIVE" ? "ok" : statusLabel === "configured" ? "info" : "warn";
      const slaLabel = a.sla_ok == null ? "n/a" : (a.sla_ok ? "ok" : "breach");
      const slaChipSev = slaLabel === "n/a" ? "neutral" : (a.sla_ok ? "ok" : "critical");
      const cardSev = slaLabel === "n/a"
        ? ""
        : (a.sla_ok ? "decision-card--ok" : "decision-card--critical");
      return `
    <article class="card decision-card ${cardSev}" role="listitem">
      <strong>${escHtml(a.label)}</strong>
      <p>${sevChip("Status", statusLabel, statusSev)}
         ${sevChip("SLA", slaLabel, slaChipSev)}</p>
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

  function mapAgentChips(agent) {
    const hasLast = !!agent?.last_run_at;
    const statusLabel = agent?.status === "LIVE" && !hasLast ? "configured" : (agent?.status || "—");
    const statusSev = statusLabel === "LIVE" ? "ok" : statusLabel === "configured" ? "info" : "warn";
    const slaLabel = !agent || agent.sla_ok == null ? "n/a" : (agent.sla_ok ? "ok" : "breach");
    const slaSev = slaLabel === "n/a" ? "neutral" : (agent.sla_ok ? "ok" : "critical");
    return { statusLabel, statusSev, slaLabel, slaSev };
  }

  if (mapEl) {
    const s = mapAgentChips(sales);
    const o = mapAgentChips(ops);
    mapEl.innerHTML = [
      `<article class="card"><strong>AI Sprzedawca</strong>
        <p>${sevChip("Agent", s.statusLabel, s.statusSev)}
           ${sevChip("SLA", s.slaLabel, s.slaSev)}</p>
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
        <p>${sevChip("Ops", o.statusLabel, o.statusSev)}
           ${sevChip("SLA", o.slaLabel, o.slaSev)}</p>
        <p class="hint">CS follow-up na Start · next ${escHtml(ops?.next_expected_run ? formatSchedule(ops.next_expected_run) : "—")}</p></article>`,
      `<article class="card"><strong>AI Asystent / Design</strong>
        <p>${sevChip("Analytics", analytics?.status === "LIVE" && !analytics?.last_run_at ? "configured" : (analytics?.status || "—"), analytics?.status === "LIVE" && analytics?.last_run_at ? "ok" : "info")}
           ${sevChip("Design", design?.status === "LIVE" && !design?.last_run_at ? "configured" : (design?.status || "—"), design?.status === "LIVE" && design?.last_run_at ? "ok" : "info")}</p>
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

/* ===== VF-VHQ-W1-SHELL (minimal shell state; no new APIs) ===== */
const VHQ_ROOMS = {
  "mission-control": {
    label: "Mission Control",
    floor: "P3",
    purpose: "Company-wide priorities, alerts, approvals and system health",
    status: "LIVE",
    evidence: "EV-W2-001",
    lastVerified: "2026-07-27T14:22:43Z",
    owner: "Ops/COI",
    sotLabel: "Commander Home priorities / queue",
    sotHref: "#priorities",
    limitation: "Queue payload needs Commander session JWT.",
    mvp: true,
    action: { type: "goto-home", target: "#priorities", label: "Open priorities / queue" },
  },
  "approval-vault": {
    label: "Approval Vault",
    floor: "P3",
    purpose: "Pending human approvals and audit trail",
    status: "PARTIAL",
    evidence: "EV-W2-009",
    lastVerified: "2026-07-27T14:24:30Z",
    owner: "Dowódca / Ops",
    sotLabel: "Commander Audyt (secondary)",
    sotHref: null,
    limitation:
      "Path Settings→Audyt verified PARTIAL; hash-chain detail needs authenticated session. No autonomous finance.",
    mvp: true,
    action: { type: "view", target: "audit", label: "Open Audyt" },
    extraHtml:
      '<p class="hint">L0–L4 policy applies. L3/L4 require explicit Founder GO. No Mollie/Ads from this room.</p>',
  },
  "ai-agent-health": {
    label: "Agent Operations",
    floor: "P3",
    purpose: "Agent / worker health overview (System Health / AI Health sub-area)",
    status: "DEGRADED",
    evidence: "EV-W2-011",
    lastVerified: "2026-07-27T14:22:43Z",
    owner: "Ops/COI",
    sotLabel: "Worker health · Design Agent health · Agent OS · VCMS",
    sotHref: null,
    limitation:
      "SSH DEGRADED is pre-existing (INC-SSH-RECOVERY-00). OS/VCMS post-auth remain PARTIAL.",
    mvp: true,
    action: { type: "view", target: "agents", label: "Open Agenci tab" },
    extraHtml:
      "<p><strong>Sub-area: System Health / AI Health</strong></p>" +
      "<ul>" +
      "<li>[DEGRADED] Worker SSH · ssh_connection=error · EV-W2-011 · INC-SSH-RECOVERY-00</li>" +
      '<li>[LIVE] Design Agent technical probe · EV-W2-006 — NOT a Production desk · <a href="/api/v1/design-agent/health" target="_blank" rel="noopener noreferrer">/api/v1/design-agent/health</a></li>' +
      '<li>[PARTIAL] Agent OS · <a href="https://os.flexgrafik.nl" target="_blank" rel="noopener noreferrer">os.flexgrafik.nl</a></li>' +
      '<li>[PARTIAL] VCMS · <a href="https://cmd.flexgrafik.nl" target="_blank" rel="noopener noreferrer">cmd.flexgrafik.nl</a></li>' +
      "</ul>",
  },
  boardroom: {
    label: "Boardroom",
    floor: "P3",
    purpose: "Strategy alignment to master-plan / scorecard",
    status: "PARTIAL",
    evidence: null,
    lastVerified: null,
    owner: "Dowódca",
    sotLabel: "flexgrafik-meta master-plan (docs)",
    sotHref: null,
    limitation: "Docs LIVE; no interactive board UI in W1.",
    mvp: false,
  },
  "analytics-finance": {
    label: "Finance / Analytics",
    floor: "P2",
    purpose: "Revenue / margin visibility via existing Analityka tab",
    status: "UNVERIFIED",
    evidence: "EV-W2-008",
    lastVerified: "2026-07-27T14:24:00Z",
    owner: "Finance/Ops",
    sotLabel: "Commander Analityka tab",
    sotHref: null,
    limitation: "Finance data UNVERIFIED. No numeric KPI in VHQ. Mollie/Purchase = L4 separate GO.",
    mvp: false,
    action: { type: "view", target: "analytics", label: "Open Analityka tab" },
  },
  "compliance-audit": {
    label: "Compliance / Audit",
    floor: "P2",
    purpose: "Hard STOP list, parks, audit chain",
    status: "PARTIAL",
    evidence: "EV-W2-009",
    lastVerified: "2026-07-27T14:24:30Z",
    owner: "Ops/Security",
    sotLabel: "Audyt / parks",
    sotHref: null,
    limitation: "Path OK; chain body needs session.",
    mvp: false,
    action: { type: "view", target: "audit", label: "Open Audyt" },
  },
  "knowledge-library": {
    label: "Knowledge Library",
    floor: "P2",
    purpose: "Canonical docs index",
    status: "UNVERIFIED",
    evidence: null,
    lastVerified: null,
    owner: "Govern",
    sotLabel: "VCMS docs (Basic Auth)",
    sotHref: "https://cmd.flexgrafik.nl/docs/",
    limitation: "Docs body unseen in W2 window (Basic Auth).",
    mvp: false,
    action: {
      type: "external",
      href: "https://cmd.flexgrafik.nl/docs/",
      label: "Open Knowledge docs hop",
    },
  },
  "data-ai-lab": {
    label: "Data & AI Lab",
    floor: "P2",
    purpose: "MB propose / experiments — no Ads execute",
    status: "PARTIAL",
    evidence: null,
    lastVerified: null,
    owner: "Marketing/Ops",
    sotLabel: "Marketing Decision Rail",
    sotHref: null,
    limitation: "Propose-only. Campaign state UNVERIFIED. No Ads from VHQ.",
    mvp: false,
    action: { type: "view", target: "marketing", label: "Open Marketing tab" },
  },
  "vcms-os-zone": {
    label: "VCMS / Agent OS zone",
    floor: "P2",
    purpose: "Govern + Build control hops (separate apps)",
    status: "PARTIAL",
    evidence: null,
    lastVerified: null,
    owner: "Govern / Build",
    sotLabel: "cmd.flexgrafik.nl · os.flexgrafik.nl",
    sotHref: "https://cmd.flexgrafik.nl",
    limitation: "Auth challenge OK; post-auth destination PARTIAL.",
    mvp: false,
    extraHtml:
      '<p><a class="buttonish" href="https://cmd.flexgrafik.nl" target="_blank" rel="noopener noreferrer">Open VCMS</a> ' +
      '<a class="buttonish" href="https://os.flexgrafik.nl" target="_blank" rel="noopener noreferrer">Open Agent OS</a></p>',
  },
  reception: {
    label: "Reception",
    floor: "P1",
    purpose: "First contact — widget / Telegram",
    status: "PLANNED",
    evidence: null,
    lastVerified: null,
    owner: "Ops/Sales",
    sotLabel: "none in VHQ shell",
    sotHref: null,
    limitation: "Capability exists in Jadzia; HQ Work View not built in W1.",
    mvp: false,
  },
  "sales-room": {
    label: "Sales Room",
    floor: "P1",
    purpose: "Hot leads and sales CTAs",
    status: "LIVE",
    evidence: "EV-W2-007",
    lastVerified: "2026-07-27T14:23:30Z",
    owner: "Sales/Ops",
    sotLabel: "Commander queue #queue-list",
    sotHref: "#queue-list",
    limitation: "No invented CRM pipeline. JWT session required for live tickets.",
    mvp: true,
    action: { type: "goto-home", target: "#queue-list", label: "Open Sales queue" },
  },
  "wizard-quote": {
    label: "Wizard / Quote Room",
    floor: "P1",
    purpose: "Cash path — ZZP branding Wizard (min EUR 199)",
    status: "LIVE",
    evidence: "EV-W2-005",
    lastVerified: "2026-07-27T14:22:45Z",
    owner: "Sales/Ops",
    sotLabel: "https://zzpackage.flexgrafik.nl/wizard/",
    sotHref: "https://zzpackage.flexgrafik.nl/wizard/",
    limitation:
      "No fake conversion KPI. Order Desk handoff PARKED. Mollie LIVE = L4 separate GO.",
    mvp: true,
    action: {
      type: "external",
      href: "https://zzpackage.flexgrafik.nl/wizard/",
      label: "Open Wizard",
    },
    extraHtml:
      '<p class="hint">Future handoff → Order Desk [PARKED]: operational desk not implemented (EV-W2-010).</p>',
  },
  "marketing-studio": {
    label: "Marketing Studio",
    floor: "P1",
    purpose: "Organic HITL surface; paid Ads frozen",
    status: "UNVERIFIED",
    evidence: "EV-W3-001",
    lastVerified: "2026-07-27T15:13:35Z",
    owner: "Marketing/Ops",
    sotLabel: "Marketing tab (observe)",
    sotHref: null,
    limitation: "Campaign state not verified. No Ads execute from VHQ.",
    mvp: false,
    action: { type: "view", target: "marketing", label: "Open Marketing tab (observe)" },
  },
  "client-support": {
    label: "Client Support",
    floor: "P1",
    purpose: "Post-sale CS follow-up",
    status: "PLANNED",
    evidence: null,
    lastVerified: null,
    owner: "Ops/CS",
    sotLabel: "Home CS form (outside VHQ Work View)",
    sotHref: null,
    limitation: "HQ room shell PLANNED in W1.",
    mvp: false,
  },
  "design-studio": {
    label: "Design Studio",
    floor: "P1",
    purpose: "Mockups / briefs before price",
    status: "PLANNED",
    evidence: "EV-W2-006",
    lastVerified: "2026-07-27T14:22:45Z",
    owner: "Design/Ops",
    sotLabel: "DA health / Wizard DA",
    sotHref: "/api/v1/design-agent/health",
    limitation: "Technical probe LIVE ≠ Production desk. Room Work View PLANNED.",
    mvp: false,
  },
  "order-desk": {
    label: "Order Desk",
    floor: "P0",
    purpose: "Orders operational desk",
    status: "PARKED",
    evidence: "EV-W2-010",
    lastVerified: "2026-07-27T14:26:00Z",
    owner: "Ops",
    sotLabel: "none — desk not implemented",
    sotHref: null,
    limitation:
      "Order operational desk is not implemented. Historical INT-002 #3149 ≠ live desk. Dependency: future ops SoT + VF-VHQ-W4.",
    mvp: false,
    parkedHeadline: "Order operational desk is not implemented.",
  },
  "production-control": {
    label: "Production Control",
    floor: "P0",
    purpose: "Partner production status",
    status: "PARKED",
    evidence: null,
    lastVerified: null,
    owner: "Ops",
    sotLabel: "none",
    sotHref: null,
    limitation: "No production dashboard in Commander. External Erka HITL only.",
    mvp: false,
  },
  "preflight-quality": {
    label: "Preflight / Quality",
    floor: "P0",
    purpose: "Media/design quality gate",
    status: "PLANNED",
    evidence: null,
    lastVerified: null,
    owner: "Ops/Design",
    sotLabel: "none in VHQ",
    sotHref: null,
    limitation: "PLANNED shell only in W1.",
    mvp: false,
  },
  "dispatch-returns": {
    label: "Dispatch / Returns",
    floor: "P0",
    purpose: "Fulfilment / returns tracking",
    status: "PARKED",
    evidence: null,
    lastVerified: null,
    owner: "Ops",
    sotLabel: "none",
    sotHref: null,
    limitation: "VF-PARK-DISPATCH — no tracker SoT.",
    mvp: false,
  },
  "supplier-dock": {
    label: "Supplier Dock",
    floor: "MAG",
    purpose: "Procurement / RFQ",
    status: "PARKED",
    evidence: null,
    lastVerified: null,
    owner: "Dowódca",
    sotLabel: "none",
    sotHref: null,
    limitation: "VF-PARK-PROCUREMENT — ROADMAP.",
    mvp: false,
  },
  "asset-warehouse": {
    label: "Asset Warehouse",
    floor: "MAG",
    purpose: "Marketing asset inventory",
    status: "PLANNED",
    evidence: null,
    lastVerified: null,
    owner: "Marketing/Dowódca",
    sotLabel: "GDrive MKT WW (HITL)",
    sotHref: null,
    limitation: "MKT-ASSET-00 parked by Founder. No MKT edits from VHQ.",
    mvp: false,
  },
  "partner-production-network": {
    label: "Partner Production Network",
    floor: "MAG",
    purpose: "External production partners",
    status: "PLANNED",
    evidence: null,
    lastVerified: null,
    owner: "Ops",
    sotLabel: "none",
    sotHref: null,
    limitation: "PLANNED — no partner SoT in Jadzia UI.",
    mvp: false,
  },
};

let vhqOpen = false;
let vhqLastFocus = null;
let vhqCurrentRoom = "mission-control";
let vhqCurrentFloor = "P3";
let vhqFocusinGuard = null;

function vhqEscHtml(s) {
  return String(s == null ? "" : s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function vhqSetFloor(floor) {
  vhqCurrentFloor = floor;
  document.querySelectorAll(".vhq-floor-band").forEach((band) => {
    band.hidden = band.dataset.floor !== floor;
  });
  document.querySelectorAll(".vhq-floor-btn").forEach((btn) => {
    const on = btn.dataset.floor === floor;
    btn.classList.toggle("active", on);
    btn.setAttribute("aria-selected", on ? "true" : "false");
  });
}

function vhqClearRoomHighlights() {
  document.querySelectorAll(".vhq-room").forEach((btn) => {
    btn.removeAttribute("aria-current");
  });
}

function vhqShowFloorBrowse(floor) {
  vhqSetFloor(floor);
  vhqCurrentRoom = null;
  vhqClearRoomHighlights();

  const loc = document.getElementById("vhq-location");
  if (loc) loc.textContent = `HQ › ${floor} › select a room`;

  const teleport = document.getElementById("vhq-teleport");
  if (teleport) teleport.value = "";

  const title = document.getElementById("vhq-panel-title");
  const purpose = document.getElementById("vhq-panel-purpose");
  const statusEl = document.getElementById("vhq-panel-status");
  const evidence = document.getElementById("vhq-panel-evidence");
  const owner = document.getElementById("vhq-panel-owner");
  const sot = document.getElementById("vhq-panel-sot");
  const limit = document.getElementById("vhq-panel-limit");
  const extra = document.getElementById("vhq-panel-extra");
  const actions = document.getElementById("vhq-panel-actions");

  if (title) title.textContent = `Floor ${floor}`;
  if (purpose) purpose.textContent = "Select a room on this floor.";
  if (statusEl) statusEl.textContent = "";
  if (evidence) evidence.textContent = "";
  if (owner) owner.textContent = "";
  if (sot) sot.textContent = "";
  if (limit) limit.textContent = "";
  if (extra) extra.innerHTML = "";
  if (actions) actions.innerHTML = "";
}

/** Floor filter only — never auto-opens a room. */
function vhqSelectFloor(floor) {
  const current = vhqCurrentRoom ? VHQ_ROOMS[vhqCurrentRoom] : null;
  if (current && current.floor === floor) {
    vhqSetFloor(floor);
    return;
  }
  vhqShowFloorBrowse(floor);
}

function vhqRenderRoom(roomId) {
  const room = VHQ_ROOMS[roomId];
  if (!room) return;
  vhqCurrentRoom = roomId;
  vhqSetFloor(room.floor);

  const loc = document.getElementById("vhq-location");
  if (loc) loc.textContent = `HQ › ${room.floor} › ${room.label}`;

  const teleport = document.getElementById("vhq-teleport");
  if (teleport && teleport.value !== roomId) teleport.value = roomId;

  document.querySelectorAll(".vhq-room").forEach((btn) => {
    if (btn.dataset.room === roomId) btn.setAttribute("aria-current", "true");
    else btn.removeAttribute("aria-current");
  });

  const title = document.getElementById("vhq-panel-title");
  const purpose = document.getElementById("vhq-panel-purpose");
  const statusEl = document.getElementById("vhq-panel-status");
  const evidence = document.getElementById("vhq-panel-evidence");
  const owner = document.getElementById("vhq-panel-owner");
  const sot = document.getElementById("vhq-panel-sot");
  const limit = document.getElementById("vhq-panel-limit");
  const extra = document.getElementById("vhq-panel-extra");
  const actions = document.getElementById("vhq-panel-actions");

  if (title) title.textContent = room.label;
  if (purpose) purpose.textContent = room.purpose || "";
  if (statusEl) {
    const parkedNote = room.parkedHeadline ? ` — ${room.parkedHeadline}` : "";
    statusEl.textContent = `[${room.status}]${parkedNote}`;
  }
  if (evidence) {
    const ev = room.evidence ? `Evidence: ${room.evidence}` : "Evidence: —";
    const lv = room.lastVerified
      ? ` · last_verified: ${room.lastVerified}`
      : " · last_verified: insufficient_data";
    evidence.textContent = ev + lv;
  }
  if (owner) owner.textContent = `Owner: ${room.owner || "—"}`;
  if (sot) {
    if (room.sotHref && (/^https?:/i.test(room.sotHref) || room.sotHref.startsWith("/"))) {
      sot.innerHTML = `SoT: <a href="${vhqEscHtml(room.sotHref)}" target="_blank" rel="noopener noreferrer">${vhqEscHtml(
        room.sotLabel || room.sotHref
      )}</a>`;
    } else if (room.sotHref && room.sotHref.startsWith("#")) {
      sot.textContent = `SoT: ${room.sotLabel || room.sotHref} (in Commander)`;
    } else {
      sot.textContent = `SoT: ${room.sotLabel || "none"}`;
    }
  }
  if (limit) limit.textContent = `Limitation: ${room.limitation || "—"}`;
  if (extra) extra.innerHTML = room.extraHtml || "";

  if (actions) {
    actions.innerHTML = "";
    if (room.action) {
      if (room.action.type === "external") {
        const a = document.createElement("a");
        a.className = "buttonish primary";
        a.href = room.action.href;
        a.target = "_blank";
        a.rel = "noopener noreferrer";
        a.textContent = room.action.label;
        actions.appendChild(a);
      } else if (room.action.type === "view" || room.action.type === "goto-home") {
        const b = document.createElement("button");
        b.type = "button";
        b.className = "primary";
        b.textContent = room.action.label;
        b.addEventListener("click", () => vhqRunAction(room.action));
        actions.appendChild(b);
      }
    } else if (room.status === "PARKED" || room.status === "PLANNED" || room.status === "UNVERIFIED") {
      const p = document.createElement("p");
      p.className = "hint";
      p.textContent =
        room.status === "PARKED"
          ? "No primary action — room intentionally PARKED."
          : room.status === "PLANNED"
            ? "No primary action — room PLANNED (shell only)."
            : "No verified primary action — status UNVERIFIED.";
      actions.appendChild(p);
    }
  }
}

function vhqFocusableNodes() {
  const shell = document.getElementById("vhq-shell");
  if (!shell || shell.hidden) return [];
  const selector =
    'a[href], button:not([disabled]), select:not([disabled]), textarea:not([disabled]), input:not([disabled]):not([type="hidden"]), [tabindex]:not([tabindex="-1"])';
  return Array.from(shell.querySelectorAll(selector)).filter((el) => {
    if (el.closest("[hidden]")) return false;
    if (el.getAttribute("aria-hidden") === "true") return false;
    const style = window.getComputedStyle(el);
    if (style.visibility === "hidden" || style.display === "none") return false;
    return true;
  });
}

function vhqSetBackdropInert(on) {
  document.querySelectorAll("body > *:not(#vhq-shell):not(#toast)").forEach((el) => {
    if (on) {
      el.setAttribute("inert", "");
      el.setAttribute("aria-hidden", "true");
      el.classList.add("vhq-backdrop-inert");
    } else {
      el.removeAttribute("inert");
      el.removeAttribute("aria-hidden");
      el.classList.remove("vhq-backdrop-inert");
    }
  });
}

function vhqDetachFocusGuard() {
  if (vhqFocusinGuard) {
    document.removeEventListener("focusin", vhqFocusinGuard, true);
    vhqFocusinGuard = null;
  }
}

function vhqAttachFocusGuard() {
  vhqDetachFocusGuard();
  vhqFocusinGuard = (e) => {
    if (!vhqOpen) return;
    const shell = document.getElementById("vhq-shell");
    if (!shell || shell.hidden) return;
    if (shell.contains(e.target)) return;
    e.preventDefault();
    const nodes = vhqFocusableNodes();
    const fallback = document.getElementById("vhq-close") || nodes[0];
    if (fallback) fallback.focus();
  };
  document.addEventListener("focusin", vhqFocusinGuard, true);
}

function vhqTrapTab(e) {
  if (e.key !== "Tab" || !vhqOpen) return;
  const shell = document.getElementById("vhq-shell");
  if (!shell || shell.hidden) return;
  const nodes = vhqFocusableNodes();
  if (!nodes.length) {
    e.preventDefault();
    return;
  }
  const first = nodes[0];
  const last = nodes[nodes.length - 1];
  const active = document.activeElement;
  if (e.shiftKey) {
    if (active === first || !shell.contains(active)) {
      e.preventDefault();
      last.focus();
    }
  } else if (active === last || !shell.contains(active)) {
    e.preventDefault();
    first.focus();
  }
}

function vhqClose() {
  const shell = document.getElementById("vhq-shell");
  if (!shell || shell.hidden) return;
  shell.hidden = true;
  document.body.classList.remove("vhq-open");
  vhqOpen = false;
  vhqDetachFocusGuard();
  vhqSetBackdropInert(false);
  showView("home");
  const enterBtn = document.getElementById("vhq-enter");
  if (enterBtn && typeof enterBtn.focus === "function") {
    enterBtn.focus();
  } else if (vhqLastFocus && typeof vhqLastFocus.focus === "function") {
    vhqLastFocus.focus();
  }
}

function vhqOpenShell(roomId) {
  const shell = document.getElementById("vhq-shell");
  if (!shell) return;
  vhqLastFocus = document.getElementById("vhq-enter") || document.activeElement;
  shell.hidden = false;
  document.body.classList.add("vhq-open");
  vhqOpen = true;
  vhqSetBackdropInert(true);
  vhqRenderRoom(roomId || "mission-control");
  vhqAttachFocusGuard();
  const closeBtn = document.getElementById("vhq-close");
  if (closeBtn) closeBtn.focus();
}

function vhqRunAction(action) {
  if (!action) return;
  if (action.type === "external") {
    window.open(action.href, "_blank", "noopener,noreferrer");
    return;
  }
  if (action.type === "view") {
    vhqClose();
    showView(action.target);
    return;
  }
  if (action.type === "goto-home") {
    vhqClose();
    showView("home");
    const el = document.querySelector(action.target);
    if (el) {
      el.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }
}

function bindVhqShell() {
  const enter = document.getElementById("vhq-enter");
  const shell = document.getElementById("vhq-shell");
  if (!enter || !shell) return;

  enter.addEventListener("click", () => vhqOpenShell("mission-control"));
  document.getElementById("vhq-close")?.addEventListener("click", vhqClose);
  document.getElementById("vhq-to-mc")?.addEventListener("click", () => {
    vhqRenderRoom("mission-control");
  });
  document.getElementById("vhq-teleport")?.addEventListener("change", (e) => {
    if (!e.target.value) return;
    vhqRenderRoom(e.target.value);
  });
  document.querySelectorAll(".vhq-floor-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      vhqSelectFloor(btn.dataset.floor);
    });
  });
  document.querySelectorAll(".vhq-room").forEach((btn) => {
    btn.addEventListener("click", () => vhqRenderRoom(btn.dataset.room));
  });
  document.addEventListener("keydown", (e) => {
    if (!vhqOpen) return;
    if (e.key === "Escape") {
      e.preventDefault();
      vhqClose();
      return;
    }
    vhqTrapTab(e);
  });
}

bindVhqShell();

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
