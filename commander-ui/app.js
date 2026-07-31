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

function isCeoStubItem(item) {
  return item?.queue_type === "ceo_stub" || item?.source === "brain_bus_ceo";
}

function approvalCard(item, actionsHtml = "") {
  const stub = isCeoStubItem(item);
  const stubClass = stub ? " approval-card--stub" : "";
  const stubBadge = stub ? `<span class="badge badge-stub">STUB</span>` : "";
  return `
    <article class="card approval-card severity-${item.severity}${stubClass}" role="listitem">
      <header class="card-header">
        <strong>${item.title}</strong>
        ${stubBadge}
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

function renderMoneyRisk(n) {
  const el = document.getElementById("vhq-money-risk");
  if (!el) return;
  if (!n) {
    el.innerHTML =
      "<p class=\"state-empty\">Money/risk narrative unavailable — refresh after sign-in.</p>";
    return;
  }
  const pipe = n.pipeline || {};
  const desk = pipe.order_desk || {};
  const risk = n.top_risk;
  const cta = n.cta || {};
  const status = n.status || "insufficient_data";
  let ctaHtml = "";
  if (cta.action === "open_wizard" && cta.target) {
    ctaHtml = `<a class="buttonish primary" href="${escHtml(cta.target)}" target="_blank" rel="noopener noreferrer">${escHtml(cta.label || "Open Wizard")}</a>`;
  } else {
    ctaHtml = `<button type="button" class="primary" id="vhq-money-cta-queue">${escHtml(cta.label || "Focus queue")}</button>`;
  }
  const riskHtml = risk
    ? `<p class="vhq-money-risk__blocker"><span class="muted">Top risk</span> ${escHtml(risk.title || "")} · <strong>${escHtml(risk.owner || "")}</strong> · ${escHtml(risk.approval_class || "")}</p>`
    : `<p class="vhq-money-risk__blocker muted">No ranked commercial risk blocker.</p>`;
  const events = (n.event_ids || []).map((e) => escHtml(e)).join(" · ");
  el.innerHTML = `
    <article class="vhq-money-risk status-${escHtml(status)}" aria-label="Money and risk narrative">
      <header class="vhq-money-risk__head">
        <span class="badge">${escHtml(status)}</span>
        <span class="badge">${escHtml(desk.status || "PARKED")}</span>
        <span class="badge">${escHtml(desk.evidence || "EV-W2-010")}</span>
      </header>
      <p class="vhq-money-risk__q1">${escHtml(n.q1 || "")}</p>
      <dl class="meta vhq-money-risk__meta">
        <dt>Open leads</dt><dd>${escHtml(String(pipe.open_leads ?? "—"))}</dd>
        <dt>Hot</dt><dd>${escHtml(String(pipe.hot_leads ?? "—"))}</dd>
        <dt>CTA-band</dt><dd>${escHtml(String(pipe.cta_band_leads ?? "—"))}</dd>
        <dt>Wizard sessions</dt><dd>${pipe.wizard_sessions == null ? "insufficient_data" : escHtml(String(pipe.wizard_sessions))}</dd>
        <dt>GA4 freshness</dt><dd>${escHtml((n.freshness && n.freshness.ga4) || "—")}</dd>
      </dl>
      ${riskHtml}
      <p class="hint vhq-money-risk__honesty">${escHtml((n.honesty || []).join(" · "))}</p>
      <p class="hint">Events: ${events || "—"}</p>
      <div class="actions">${ctaHtml}</div>
    </article>`;
  const qBtn = document.getElementById("vhq-money-cta-queue");
  if (qBtn) {
    qBtn.onclick = () => {
      document.getElementById("queue-list")?.scrollIntoView({ behavior: "smooth", block: "start" });
    };
  }
}

function renderNba(nba) {
  const el = document.getElementById("vhq-nba");
  if (!el) return;
  if (!nba) {
    el.innerHTML =
      "<p class=\"state-empty\">No ranked Director action — queue calm or only hygiene. Check secondary / queue.</p>";
    return;
  }
  const cta = nba.cta || {};
  const cls = `vhq-nba severity-${escHtml(nba.severity || "ACTION")}`;
  let ctaHtml = "";
  if (cta.action === "lead_ack" && cta.target) {
    ctaHtml = `<button type="button" class="primary" data-lead-disp="${escHtml(cta.target)}" data-disp="acked">${escHtml(cta.label || "Potwierdź lead")}</button>`;
  } else if (cta.action === "ticket_ack" && cta.target) {
    ctaHtml = `<button type="button" class="primary" data-ticket-disp="${escHtml(cta.target)}" data-disp="acked">${escHtml(cta.label || "Potwierdź ticket")}</button>`;
  } else {
    ctaHtml = `<button type="button" class="primary" id="vhq-nba-cta-queue">${escHtml(cta.label || "Focus queue")}</button>`;
  }
  el.innerHTML = `
    <article class="${cls}" aria-label="Director: do this now">
      <header class="vhq-nba__head">
        <strong>${escHtml(nba.title || "")}</strong>
        <span class="badge badge-nba">NBA</span>
        <span class="badge">${escHtml(nba.severity || "")}</span>
        <span class="badge ${escHtml(nba.sla_status || "")}">${escHtml(nba.sla_status || "")}</span>
        <span class="badge">${escHtml(nba.approval_class || "L2")}</span>
      </header>
      <p class="vhq-nba__why"><span class="muted">Why now</span> ${escHtml(nba.why_now || "")}</p>
      <dl class="meta vhq-nba__meta">
        <dt>Owner</dt><dd>${escHtml(nba.owner || "")}</dd>
        <dt>Evidence</dt><dd>${escHtml(nba.evidence_ts || "")}</dd>
        <dt>Cost of inaction</dt><dd>${escHtml(nba.cost_of_inaction || "")}</dd>
        <dt>Score</dt><dd>${escHtml(String(nba.nba_score ?? ""))}</dd>
      </dl>
      <div class="actions vhq-nba__cta">${ctaHtml}</div>
    </article>`;
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
  const qBtn = document.getElementById("vhq-nba-cta-queue");
  if (qBtn) {
    qBtn.onclick = () => {
      document.getElementById("queue-list")?.scrollIntoView({ behavior: "smooth", block: "start" });
    };
  }
}

function renderPriorities(items) {
  const el = document.getElementById("priorities");
  if (!el) return;
  const secondary = (items || []).filter((p) => !p.nba_primary);
  el.innerHTML = secondary.length
    ? secondary.map((p) => approvalCard(p)).join("")
    : "<p class=\"state-empty\">Brak secondary — primary NBA powyżej lub spokój. Sprawdź kolejkę.</p>";
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
  const list = items || [];
  const stubs = list.filter((i) => isCeoStubItem(i));
  const actionable = list.filter((i) => i.severity !== "INFO" && !isCeoStubItem(i));
  const el = document.getElementById("queue-list");
  const parts = [];
  if (actionable.length) {
    parts.push(...actionable.map((q) => approvalCard(q, queueItemActions(q))));
  }
  if (stubs.length) {
    parts.push(
      `<p class="queue-hygiene-label hint">Hygiene · ${stubs.length} CEO stub(s) — not Decide-now</p>`,
    );
    parts.push(...stubs.map((q) => approvalCard(q, "")));
  }
  if (!parts.length) {
    el.innerHTML =
      "<p class=\"state-empty\">Kolejka pusta — brak CRITICAL/ACTION. Możesz utworzyć follow-up CS poniżej.</p>";
  } else if (!actionable.length && stubs.length) {
    el.innerHTML =
      `<p class="state-empty">Brak CRITICAL/ACTION · ${stubs.length} stub hygiene poniżej.</p>` +
      parts.join("");
  } else {
    el.innerHTML = parts.join("");
  }
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
  if (!root) return;
  if (root.dataset.hopsBound === "1") return;
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
  let prioEl = document.getElementById("priorities");
  let queueEl = document.getElementById("queue-list");
  let chipsEl = document.getElementById("home-ops-chips");
  let summaryEl = document.getElementById("home-ops-summary");
  if (!prioEl || !queueEl) return;
  prioEl.setAttribute("aria-busy", "true");
  queueEl.setAttribute("aria-busy", "true");
  prioEl.innerHTML = homeSkeleton(2);
  queueEl.innerHTML = homeSkeleton(2);
  if (summaryEl) summaryEl.textContent = "Ładowanie ops…";
  if (chipsEl) chipsEl.innerHTML = "";
  if (typeof vhqUpdateSessionBanner === "function") vhqUpdateSessionBanner();

  let prio;
  let queue;
  try {
    let money;
    [prio, queue, money] = await Promise.all([
      api("/api/v1/commander/priorities/today"),
      api("/api/v1/commander/queue"),
      api("/api/v1/commander/money-risk").catch(() => null),
    ]);
    // Re-query after await — VHQ cold-open may remount slot nodes mid-flight.
    prioEl = document.getElementById("priorities");
    queueEl = document.getElementById("queue-list");
    chipsEl = document.getElementById("home-ops-chips");
    summaryEl = document.getElementById("home-ops-summary");
    if (!prioEl || !queueEl) return;
    const nba =
      prio.nba ||
      (prio.priorities || []).find((p) => p.nba_primary) ||
      null;
    renderMoneyRisk(money);
    renderNba(nba);
    renderPriorities(prio.secondary || prio.priorities || []);
    renderQueue(queue.items || []);
    prioEl.removeAttribute("aria-busy");
    queueEl.removeAttribute("aria-busy");
    if (typeof vhqUpdateSessionBanner === "function") vhqUpdateSessionBanner();
  } catch (e) {
    prioEl = document.getElementById("priorities");
    queueEl = document.getElementById("queue-list");
    summaryEl = document.getElementById("home-ops-summary");
    const nbaEl = document.getElementById("vhq-nba");
    if (prioEl) prioEl.removeAttribute("aria-busy");
    if (queueEl) queueEl.removeAttribute("aria-busy");
    if (typeof vhqUpdateSessionBanner === "function") vhqUpdateSessionBanner();
    if (nbaEl) {
      nbaEl.innerHTML = `<p class="state-error">Nie udało się pobrać NBA.</p>`;
    }
    if (prioEl) {
      prioEl.innerHTML = `<p class="state-error">Nie udało się pobrać priorytetów. <button type="button" class="primary" id="home-retry">Spróbuj ponownie</button></p>`;
    }
    if (queueEl) {
      queueEl.innerHTML = `<p class="state-error">Nie udało się pobrać kolejki.</p>`;
    }
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
    // P2-SNR-00: freshness/GA4 are confidence chips — not Ops fire headline.
    const worstOps = worstSev(opsSev, sshSev, sqlSev, loopSev, slaSev);
    const attention = [];
    if (slaSev === "critical") attention.push(`SLA bad ${slaBad}`);
    if (opsSev === "critical" || opsSev === "warn") attention.push(`ops ${opsHealth?.status || "—"}`);
    if (sshSev === "critical") attention.push("SSH");
    if (sqlSev === "critical") attention.push("SQLite");
    if (loopSev === "critical") attention.push("loop");
    const confBits = [];
    if (freshSev === "critical" || freshSev === "warn") confBits.push(`freshness ${pipelineFresh}`);
    if (gaSev === "warn" || gaSev === "critical") confBits.push(`GA4 ${fresh}`);
    const confNote = confBits.length
      ? ` · data confidence degraded (${confBits.slice(0, 2).join(" · ")})`
      : "";
    summaryEl.textContent = worstOps === "ok" || worstOps === "neutral"
      ? `Ops: OK${up}${confNote}`
      : `Ops: UWAGA — ${attention.slice(0, 3).join(" · ") || worstOps}${up}${confNote}`;
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

function vhqNeedsHomeData() {
  const active = document.querySelector(".view:not([hidden])")?.id?.replace("view-", "") || "home";
  if (active === "home") return true;
  if (active !== "hq") return false;
  const command = document.getElementById("vhq-command");
  const workSales = document.getElementById("vhq-work-sales");
  if (command && !command.hidden) return true;
  if (workSales && !workSales.hidden) return true;
  return false;
}

async function refresh() {
  if (!getToken()) return;
  const active = document.querySelector(".view:not([hidden])")?.id?.replace("view-", "") || "home";
  if (active === "home" || vhqNeedsHomeData()) await loadHome();
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
      if (view === "hq") {
        if (typeof vhqGoMissionControl === "function") {
          vhqGoMissionControl({ historyMode: "push" });
        } else {
          showView("hq");
        }
        try {
          await refresh();
        } catch (e) {
          toast(e.message);
        }
        return;
      }
      if (typeof vhqIsPrimary === "function" && vhqIsPrimary() && typeof vhqParkPrimaryShell === "function") {
        vhqParkPrimaryShell();
      }
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

/* ===== VF-VHQ-W1-SHELL + W3.2 Room Manifest (sole SoT) ===== */
/** @type {Record<string, object>} */
const VHQ_ROOMS = {
  "mission-control": {
    id: "mission-control",
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
    action: { type: "goto-home", target: "#priorities", label: "Open priorities / queue" },
    mvp: true,
    pulse: true,
    truthPilot: true,
    floorCard: true,
    mapHop: {
      href: null,
      interactive: false,
      label: "Mission Control",
      meta: "P3 · Mission Control · priorities, alerts, approvals, system health",
    },
    kpi: [
      { id: "KPI-CEO-COLD-OPEN", value: "insufficient_data", note: "no timed dogfood in this window" },
      {
        id: "Worker health",
        value: "healthy · ssh_connection=ok · INC-SSH-RECOVERY-00 CLOSED 2026-07-31",
      },
    ],
  },
  "approval-vault": {
    id: "approval-vault",
    label: "Approval Vault",
    floor: "P3",
    purpose: "Pending human approvals and audit trail",
    status: "PARTIAL",
    evidence: "EV-W6-001",
    lastVerified: "2026-07-31T08:45:00Z",
    owner: "Dowódca / Ops",
    sotLabel: "ops_bus_events · approval_needed pending",
    sotHref: null,
    limitation:
      "L2 Approve/Reject flips state only (no deploy/publish/charge). L3/L4 STOP display — Founder GO required. No Mollie/Ads.",
    action: { type: "room", target: "approval-vault", label: "Open Approval Vault" },
    mvp: true,
    pulse: false,
    truthPilot: false,
    floorCard: true,
    briefVault: true,
    links: [
      {
        text: "L0–L4 policy applies. L3/L4 require explicit Founder GO. No Mollie/Ads from this room.",
        href: null,
      },
    ],
  },
  "ai-agent-health": {
    id: "ai-agent-health",
    label: "Agent Operations",
    floor: "P3",
    purpose: "Agent / worker health overview (System Health / AI Health sub-area)",
    status: "PARTIAL",
    evidence: "EV-W2-011",
    lastVerified: "2026-07-31T06:00:00Z",
    owner: "Ops/COI",
    sotLabel: "Worker health · Design Agent health · Agent OS · VCMS",
    sotHref: null,
    limitation:
      "Worker SSH recovered (INC-SSH-RECOVERY-00 CLOSED 2026-07-31 · ssh_connection=ok). OS/VCMS post-auth remain PARTIAL.",
    action: { type: "view", target: "agents", label: "Open Agenci tab" },
    mvp: true,
    pulse: true,
    truthPilot: false,
    floorCard: true,
    criticalPin: false,
    links: [
      { text: "Sub-area: System Health / AI Health", href: null },
      {
        text: "[LIVE] Worker SSH · ssh_connection=ok · INC-SSH-RECOVERY-00 CLOSED",
        href: null,
      },
      {
        text: "[LIVE] Design Agent technical probe · EV-W2-006 — NOT a Production desk",
        href: "/api/v1/design-agent/health",
      },
      { text: "[PARTIAL] Agent OS", href: "https://os.flexgrafik.nl" },
      { text: "[PARTIAL] VCMS", href: "https://cmd.flexgrafik.nl" },
    ],
  },
  boardroom: {
    id: "boardroom",
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
    pulse: false,
    truthPilot: false,
    floorCard: true,
  },
  "analytics-finance": {
    id: "analytics-finance",
    aliases: ["analytics", "finance-analytics"],
    label: "Finance / Analytics",
    floor: "P2",
    purpose: "Revenue / margin visibility via existing Analityka tab — not a Finance Room agent",
    status: "UNVERIFIED",
    evidence: "EV-W2-008",
    lastVerified: "2026-07-27T14:24:00Z",
    owner: "Finance/Ops",
    sotLabel: "Existing Analytics surface (Commander tab Analityka) — Finance data UNVERIFIED",
    sotHref: null,
    limitation: "Path-only evidence EV-W2-008. Purchase/Mollie PARK. No fake revenue numbers.",
    action: { type: "view", target: "analytics", label: "Open Analityka tab" },
    mvp: false,
    pulse: true,
    truthPilot: true,
    floorCard: true,
    mapHop: {
      href: null,
      interactive: false,
      label: "Analytics",
      meta: "P2 · Analytics · Finance data UNVERIFIED — use tab Analityka (existing)",
    },
    kpi: [{ id: "Finance KPI", value: "insufficient_data", note: "no finance KPI without authenticated freshness" }],
  },
  "compliance-audit": {
    id: "compliance-audit",
    aliases: ["compliance"],
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
    action: { type: "view", target: "audit", label: "Open Audyt" },
    mvp: false,
    pulse: true,
    truthPilot: false,
    floorCard: true,
    mapHop: {
      href: null,
      interactive: false,
      label: "Compliance / Approvals",
      meta: "P3 · Compliance / Approvals · Ustawienia → Audyt path verified",
      mapFloor: "P3",
    },
  },
  "knowledge-library": {
    id: "knowledge-library",
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
    action: {
      type: "external",
      href: "https://cmd.flexgrafik.nl/docs/",
      label: "Open Knowledge docs hop",
    },
    mvp: false,
    pulse: false,
    truthPilot: false,
    floorCard: true,
    mapHop: {
      href: "https://cmd.flexgrafik.nl/docs/",
      interactive: true,
      label: "Knowledge",
      meta: "P2 · Knowledge · ecosystem docs",
    },
  },
  "data-ai-lab": {
    id: "data-ai-lab",
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
    action: { type: "view", target: "marketing", label: "Open Marketing tab" },
    mvp: false,
    pulse: false,
    truthPilot: false,
    floorCard: true,
  },
  "vcms-os-zone": {
    id: "vcms-os-zone",
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
    pulse: false,
    truthPilot: false,
    floorCard: true,
    mapHops: [
      {
        id: "agent-os",
        label: "Agent OS",
        href: "https://os.flexgrafik.nl",
        interactive: true,
        status: "PARTIAL",
        evidence: null,
        lastVerified: null,
        meta: "P3 · Agent OS · build HITL / task approve",
        stateText: "PARTIAL · auth OK · destination HITL",
        mapFloor: "P3",
      },
      {
        id: "vcms",
        label: "VCMS",
        href: "https://cmd.flexgrafik.nl",
        interactive: true,
        status: "PARTIAL",
        evidence: null,
        lastVerified: null,
        meta: "P3 · VCMS · governance / conflicts",
        stateText: "PARTIAL · auth OK · destination HITL",
        mapFloor: "P3",
      },
    ],
    links: [
      { text: "Open VCMS", href: "https://cmd.flexgrafik.nl" },
      { text: "Open Agent OS", href: "https://os.flexgrafik.nl" },
    ],
  },
  reception: {
    id: "reception",
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
    pulse: false,
    truthPilot: false,
    floorCard: true,
  },
  "sales-room": {
    id: "sales-room",
    aliases: ["sales-queue"],
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
    action: { type: "focus-queue", label: "Focus Sales queue" },
    mvp: true,
    pulse: true,
    truthPilot: false,
    floorCard: true,
    flowOrder: 1,
    pulseLabel: "Sales",
    mapHop: {
      href: "#queue-list",
      interactive: true,
      label: "Sales · leads queue",
      meta: "P1 · Sales · CRITICAL / ACTION queue on this page",
    },
  },
  "wizard-quote": {
    id: "wizard-quote",
    aliases: ["showroom-wizard"],
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
    action: {
      type: "external",
      href: "https://zzpackage.flexgrafik.nl/wizard/",
      label: "Open Wizard",
    },
    mvp: true,
    pulse: true,
    truthPilot: true,
    floorCard: true,
    flowOrder: 2,
    pulseLabel: "Wizard",
    mapHop: {
      href: "https://zzpackage.flexgrafik.nl/wizard/",
      interactive: true,
      label: "Wizard / Quote",
      meta: "P1 · Wizard / Quote · cash path",
    },
    kpi: [
      {
        id: "KPI-MKT-WIZARD-STARTS",
        value: "insufficient_data",
        note: "no fresh GA4/INT-009 snapshot",
      },
      { id: "Hop destination", value: "LIVE · no login wall · EV-W2-005" },
    ],
    honesty: [
      {
        status: "PARKED",
        text: "Future handoff → Order Desk [PARKED] — operational desk not implemented (EV-W2-010).",
      },
    ],
  },
  "marketing-studio": {
    id: "marketing-studio",
    label: "Marketing Studio",
    floor: "P1",
    purpose: "Organic HITL surface — paid Ads out of scope in freeze",
    status: "UNVERIFIED",
    evidence: "EV-W3-001",
    lastVerified: "2026-07-27T15:13:35Z",
    owner: "Marketing/Ops",
    sotLabel: "Campaign SoT requires MKT / Ads Manager verification and is outside current Virtual HQ scope.",
    sotHref: null,
    limitation:
      "EV-W3-001 — do not invent campaign LIVE or campaign-absence claims. Paid Ads PARKED to 2026-08-06. No Ads execute from VHQ.",
    action: { type: "view", target: "marketing", label: "Open Marketing tab (observe)" },
    mvp: true,
    pulse: true,
    truthPilot: true,
    floorCard: true,
    pulseLabel: "Marketing",
    mapHop: {
      href: null,
      interactive: false,
      label: "Marketing Studio",
      meta: "P1 · Marketing Studio · UNVERIFIED — campaign state not verified",
    },
    honesty: [
      { status: "UNVERIFIED", text: "UNVERIFIED — campaign state not verified · EV-W3-001" },
      {
        status: "PARKED",
        text: "[PARKED] Paid Ads frozen until 2026-08-06 · €0 spend · no Ads execute from VHQ",
      },
    ],
    kpi: [
      { id: "Campaign state", value: "insufficient_data" },
      { id: "wizard_starts (UTM)", value: "insufficient_data" },
      { id: "KPI-CPA-WIZARD", value: "PARKED (freeze · €0 paid) · not a measured value" },
    ],
  },
  "client-support": {
    id: "client-support",
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
    pulse: false,
    truthPilot: false,
    floorCard: true,
  },
  "design-studio": {
    id: "design-studio",
    label: "Design Studio",
    floor: "P1",
    purpose: "Mockups / briefs before price",
    status: "PLANNED",
    evidence: null,
    lastVerified: null,
    owner: "Design/Ops",
    sotLabel: "DA health / Wizard DA",
    sotHref: null,
    limitation: "Technical probe LIVE ≠ Production desk. Room Work View PLANNED. See design-agent-probe.",
    mvp: false,
    pulse: false,
    truthPilot: false,
    floorCard: true,
  },
  "design-agent-probe": {
    id: "design-agent-probe",
    label: "System Health / Design Agent",
    floor: "P3",
    purpose: "Technical readiness probe — NOT a Production desk / workflow",
    status: "LIVE",
    evidence: "EV-W2-006",
    lastVerified: "2026-07-27T14:22:45Z",
    owner: "Ops/COI",
    sotLabel: "/api/v1/design-agent/health",
    sotHref: "/api/v1/design-agent/health",
    limitation: "LIVE technical probe ≠ Production desk.",
    action: {
      type: "external",
      href: "/api/v1/design-agent/health",
      label: "Open Design Agent health",
    },
    mvp: false,
    pulse: false,
    truthPilot: false,
    floorCard: false,
    technicalProbe: true,
    mapHop: {
      href: "/api/v1/design-agent/health",
      interactive: true,
      label: "System Health / Design Agent",
      meta: "P3 · System Health / Design Agent · readiness probe — NOT a Production desk / workflow",
    },
  },
  "order-desk": {
    id: "order-desk",
    aliases: ["orders-production"],
    label: "Order Desk",
    floor: "P0",
    purpose: "Orders & production operational desk",
    status: "PARKED",
    evidence: "EV-W2-010",
    lastVerified: "2026-07-27T14:26:00Z",
    owner: "Ops",
    sotLabel: "No live source-of-truth / operational desk not implemented",
    sotHref: null,
    limitation:
      "EV-W2-010 = PARKED shell only. No order dashboard invented. Historical #3149 ≠ live desk. INT-002 rows ≠ operational desk SoT.",
    action: null,
    mvp: false,
    pulse: true,
    truthPilot: true,
    floorCard: true,
    flowOrder: 3,
    pulseLabel: "Order Desk",
    parkedHeadline: "Order operational desk is not implemented.",
    directorQ: "Is there an operational order desk we can trust today?",
    mapHop: {
      href: null,
      interactive: false,
      label: "Orders & Production",
      meta: "P0 · Orders & Production · PARKED — operational desk not implemented",
    },
    honesty: [
      {
        status: "PARKED",
        text: "PARKED — operational desk not implemented · EV-W2-010",
      },
      {
        status: "PARKED",
        text: "No LIVE order KPIs. Historical #3149 / INT-002 rows ≠ desk SoT.",
      },
    ],
    kpi: [
      { id: "Open orders", value: "insufficient_data" },
      { id: "Production SLA", value: "insufficient_data" },
    ],
  },
  "production-control": {
    id: "production-control",
    label: "Production Control",
    floor: "P0",
    purpose: "Partner production status",
    status: "PARKED",
    evidence: "EV-W4-001",
    lastVerified: "2026-07-31T05:30:00Z",
    owner: "Ops",
    sotLabel: "No production SoT in Commander — external Erka HITL only",
    sotHref: null,
    limitation:
      "EV-W4-001 = PARKED shell honesty. No production dashboard invented. External Erka HITL only.",
    action: null,
    mvp: false,
    pulse: false,
    truthPilot: false,
    floorCard: true,
    directorQ: "Can we see partner production status without inventing a board?",
    honesty: [
      {
        status: "PARKED",
        text: "PARKED — no production dashboard in Commander · EV-W4-001",
      },
      {
        status: "PARKED",
        text: "External Erka HITL only — no invented SLA / WIP board.",
      },
    ],
    kpi: [
      { id: "Jobs in production", value: "insufficient_data" },
      { id: "Partner SLA", value: "insufficient_data" },
    ],
  },
  "preflight-quality": {
    id: "preflight-quality",
    label: "Preflight / Quality",
    floor: "P0",
    purpose: "Media/design quality gate",
    status: "PLANNED",
    evidence: "EV-W4-002",
    lastVerified: "2026-07-31T05:30:00Z",
    owner: "Ops/Design",
    sotLabel: "No preflight SoT in VHQ yet",
    sotHref: null,
    limitation:
      "EV-W4-002 = PLANNED shell only. Quality gate UI not implemented. No fake pass/fail queue.",
    action: null,
    mvp: false,
    pulse: false,
    truthPilot: false,
    floorCard: true,
    directorQ: "Is a quality preflight gate available in HQ today?",
    honesty: [
      {
        status: "PLANNED",
        text: "PLANNED — preflight / quality Work View shell only · EV-W4-002",
      },
      {
        status: "PLANNED",
        text: "No fake pass/fail queue or invented quality KPIs.",
      },
    ],
    kpi: [
      { id: "Files awaiting preflight", value: "insufficient_data" },
      { id: "Fail rate", value: "insufficient_data" },
    ],
  },
  "dispatch-returns": {
    id: "dispatch-returns",
    label: "Dispatch / Returns",
    floor: "P0",
    purpose: "Fulfilment / returns tracking",
    status: "PARKED",
    evidence: "EV-W4-003",
    lastVerified: "2026-07-31T05:30:00Z",
    owner: "Ops",
    sotLabel: "No dispatch tracker SoT — VF-PARK-DISPATCH",
    sotHref: null,
    limitation: "EV-W4-003 = PARKED shell. VF-PARK-DISPATCH — no tracker SoT. No invented shipments.",
    action: null,
    mvp: false,
    pulse: false,
    truthPilot: false,
    floorCard: true,
    directorQ: "Can we track dispatch / returns from HQ today?",
    honesty: [
      {
        status: "PARKED",
        text: "PARKED — no dispatch / returns tracker · EV-W4-003 · VF-PARK-DISPATCH",
      },
      {
        status: "PARKED",
        text: "No invented shipment counts or delivery KPIs.",
      },
    ],
    kpi: [
      { id: "Shipments open", value: "insufficient_data" },
      { id: "Returns open", value: "insufficient_data" },
    ],
  },
  "supplier-dock": {
    id: "supplier-dock",
    aliases: ["supplier-warehouse"],
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
    pulse: false,
    truthPilot: false,
    floorCard: true,
    mapHop: {
      href: null,
      interactive: false,
      label: "Supplier / Warehouse",
      meta: "MAG · Supplier / Warehouse · PARKED — desk not implemented",
    },
  },
  "asset-warehouse": {
    id: "asset-warehouse",
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
    pulse: false,
    truthPilot: false,
    floorCard: true,
  },
  "partner-production-network": {
    id: "partner-production-network",
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
    pulse: false,
    truthPilot: false,
    floorCard: true,
  },
};

const VHQ_ROOM_ALIASES = (() => {
  const map = Object.create(null);
  Object.keys(VHQ_ROOMS).forEach((id) => {
    map[id] = id;
    const room = VHQ_ROOMS[id];
    (room.aliases || []).forEach((a) => {
      map[a] = id;
    });
  });
  return map;
})();

function vhqResolveRoomId(idOrAlias) {
  if (!idOrAlias) return null;
  return VHQ_ROOM_ALIASES[idOrAlias] || null;
}

function vhqGetRoom(idOrAlias) {
  const id = vhqResolveRoomId(idOrAlias);
  return id ? VHQ_ROOMS[id] : null;
}

function vhqRoomsList() {
  return Object.keys(VHQ_ROOMS).map((id) => VHQ_ROOMS[id]);
}

function vhqStatusLine(room) {
  const parts = [room.status];
  if (room.evidence) parts.push(room.evidence);
  if (room.lastVerified) parts.push(room.lastVerified);
  return parts.join(" · ");
}

function vhqAppendText(el, text) {
  el.appendChild(document.createTextNode(text == null ? "" : String(text)));
}

function vhqClear(el) {
  if (!el) return;
  while (el.firstChild) el.removeChild(el.firstChild);
}

function vhqEl(tag, className, text) {
  const n = document.createElement(tag);
  if (className) n.className = className;
  if (text != null) n.textContent = text;
  return n;
}

function vhqSafeLink(href, label, className) {
  const a = document.createElement("a");
  if (className) a.className = className;
  a.href = href;
  if (/^https?:/i.test(href) || href.startsWith("/")) {
    a.target = "_blank";
    a.rel = "noopener noreferrer";
  }
  a.textContent = label;
  return a;
}

let vhqOpen = false;
let vhqLastFocus = null;
let vhqCurrentRoom = "mission-control";
let vhqCurrentFloor = "P3";
let vhqFocusinGuard = null;
let vhqNavState = "mc";
let vhqApplyingHistory = false;

/** W3.1 primary shell flag. Override: ?vhq_shell=legacy|primary */
function vhqIsPrimary() {
  const override = new URLSearchParams(window.location.search).get("vhq_shell");
  if (override === "legacy") return false;
  if (override === "primary") return true;
  return document.body.dataset.vhqPrimary === "1";
}

function vhqStateFromRoom(roomId) {
  if (!roomId || roomId === "mission-control") return "mc";
  return roomId;
}

function vhqWriteHistory(state, { replace = false } = {}) {
  if (!vhqIsPrimary() || vhqApplyingHistory) return;
  const url = new URL(window.location.href);
  if (state) url.searchParams.set("vhq", state);
  else url.searchParams.delete("vhq");
  const qs = url.searchParams.toString();
  const path = `${url.pathname}${qs ? `?${qs}` : ""}${url.hash}`;
  const data = { vhq: state || "" };
  if (replace) window.history.replaceState(data, "", path);
  else window.history.pushState(data, "", path);
  vhqNavState = state || "";
}

/**
 * Legacy modal portal: move #vhq-shell to body so inert/visibility can safely
 * target .coi-shell without hiding an ancestor of the dialog.
 * Primary mode always keeps the shell inside #view-hq.
 */
function vhqPortalShellForLegacy(open) {
  const shell = document.getElementById("vhq-shell");
  const host = document.getElementById("view-hq");
  if (!shell || !host) return;
  if (open) {
    if (shell.parentElement !== document.body) {
      document.body.appendChild(shell);
    }
    return;
  }
  if (shell.parentElement !== host) {
    host.insertBefore(shell, host.firstChild);
  }
}

function vhqApplyLegacyShellAttrs(on) {
  const shell = document.getElementById("vhq-shell");
  if (!shell) return;
  if (on) {
    shell.setAttribute("role", "dialog");
    shell.setAttribute("aria-modal", "true");
    document.body.classList.add("vhq-legacy");
  } else {
    shell.removeAttribute("role");
    shell.removeAttribute("aria-modal");
    document.body.classList.remove("vhq-legacy");
    vhqPortalShellForLegacy(false);
  }
}

function vhqParkPrimaryShell() {
  if (!vhqIsPrimary()) return;
  try {
    vhqRestoreAllSlots();
  } catch (err) {
    console.warn("vhqRestoreAllSlots failed", err);
  }
  document.body.classList.remove("vhq-open", "vhq-mode-command", "vhq-mode-work", "vhq-mode-world");
  vhqOpen = false;
}

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
    btn.classList.remove("vhq-room--focal");
  });
}

function vhqShowFloorBrowse(floor, opts = {}) {
  const historyMode = opts.historyMode || "push";
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
  vhqClear(extra);
  vhqClear(actions);
  vhqSetMode("world");
  vhqRestoreAllSlots();
  vhqShowWorkPanel(null);
  if (vhqIsPrimary() && historyMode !== "none") {
    vhqWriteHistory("world", { replace: historyMode === "replace" });
  }
}

/** Floor filter only — never auto-opens a room. */
function vhqSelectFloor(floor) {
  const current = vhqCurrentRoom ? VHQ_ROOMS[vhqCurrentRoom] : null;
  if (current && current.floor === floor) {
    vhqSetFloor(floor);
    return;
  }
  vhqShowFloorBrowse(floor, { historyMode: "push" });
}

function vhqFillRoomExtra(extra, room) {
  vhqClear(extra);
  if (!room || !extra) return;
  if (room.links && room.links.length) {
    const list = vhqEl("ul", "vhq-room-links");
    room.links.forEach((lnk) => {
      const li = document.createElement("li");
      if (lnk.href) li.appendChild(vhqSafeLink(lnk.href, lnk.text, "buttonish"));
      else vhqAppendText(li, lnk.text);
      list.appendChild(li);
    });
    extra.appendChild(list);
  }
}

function vhqRenderRoom(roomId, opts = {}) {
  const historyMode = opts.historyMode || "push";
  const resolved = vhqResolveRoomId(roomId) || roomId;
  const room = VHQ_ROOMS[resolved];
  if (!room) return;
  vhqCurrentRoom = resolved;
  vhqSetFloor(room.floor);

  const loc = document.getElementById("vhq-location");
  if (loc) loc.textContent = `HQ › ${room.floor} › ${room.label}`;

  const teleport = document.getElementById("vhq-teleport");
  if (teleport && teleport.value !== resolved) teleport.value = resolved;

  document.querySelectorAll(".vhq-room").forEach((btn) => {
    const on = btn.dataset.room === resolved;
    if (on) {
      btn.setAttribute("aria-current", "true");
      btn.classList.add("vhq-room--focal");
    } else {
      btn.removeAttribute("aria-current");
      btn.classList.remove("vhq-room--focal");
    }
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
    vhqClear(sot);
    vhqAppendText(sot, "SoT: ");
    if (room.sotHref && (/^https?:/i.test(room.sotHref) || room.sotHref.startsWith("/"))) {
      sot.appendChild(vhqSafeLink(room.sotHref, room.sotLabel || room.sotHref));
    } else if (room.sotHref && room.sotHref.startsWith("#")) {
      vhqAppendText(sot, `${room.sotLabel || room.sotHref} (in Commander)`);
    } else {
      vhqAppendText(sot, room.sotLabel || "none");
    }
  }
  if (limit) limit.textContent = `Limitation: ${room.limitation || "—"}`;
  vhqFillRoomExtra(extra, room);

  if (actions) {
    vhqClear(actions);
    if (room.action) {
      if (room.action.type === "external") {
        actions.appendChild(vhqSafeLink(room.action.href, room.action.label, "buttonish primary"));
      } else {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "primary";
        btn.textContent = room.action.label;
        btn.addEventListener("click", () => vhqRunAction(room.action));
        actions.appendChild(btn);
      }
    }
  }

  vhqApplyRoomChrome(resolved);
  if (vhqIsPrimary() && historyMode !== "none") {
    vhqWriteHistory(vhqStateFromRoom(resolved), { replace: historyMode === "replace" });
  }
}

/* ===== VF-VHQ-W2/W3.2 Mission Control mounts + manifest renderers ===== */
const VHQ_SLOT_HOME = {
  ops: "vhq-home-slot-ops",
  priorities: "vhq-home-slot-priorities",
  queue: "vhq-home-slot-queue",
  cs: "vhq-home-slot-cs",
};

const VHQ_SLOT_MOUNTS = {
  "mission-control": {
    ops: "vhq-mount-ops",
    priorities: "vhq-mount-priorities",
    queue: "vhq-mount-queue",
  },
  "sales-room": {
    queue: "vhq-mount-work-queue",
    cs: "vhq-mount-work-cs",
  },
};

function vhqRestoreAllSlots() {
  Object.keys(VHQ_SLOT_HOME).forEach((key) => {
    const home = document.getElementById(VHQ_SLOT_HOME[key]);
    if (!home) return;
    document.querySelectorAll(`[data-vhq-mount="${key}"]`).forEach((mount) => {
      while (mount.firstChild) home.appendChild(mount.firstChild);
    });
  });
}

function vhqMountSlotsForRoom(roomId) {
  vhqRestoreAllSlots();
  const map = VHQ_SLOT_MOUNTS[roomId];
  if (!map) return;
  Object.entries(map).forEach(([key, mountId]) => {
    const home = document.getElementById(VHQ_SLOT_HOME[key]);
    const mount = document.getElementById(mountId);
    if (!home || !mount) return;
    if (!home.firstChild) return;
    while (home.firstChild) mount.appendChild(home.firstChild);
  });
}

function vhqSetMode(mode) {
  document.body.classList.remove("vhq-mode-command", "vhq-mode-work", "vhq-mode-world");
  const command = document.getElementById("vhq-command");
  const work = document.getElementById("vhq-work");
  if (command) command.hidden = mode !== "command";
  if (work) work.hidden = mode !== "work";
  if (mode === "command") document.body.classList.add("vhq-mode-command");
  else if (mode === "work") document.body.classList.add("vhq-mode-work");
  else document.body.classList.add("vhq-mode-world");
}

function vhqUpdateSessionBanner() {
  const banner = document.getElementById("vhq-session-banner");
  const signIn = document.getElementById("vhq-sign-in");
  if (!banner) return;
  const hasToken = typeof getToken === "function" && !!getToken();
  if (!hasToken) {
    banner.hidden = false;
    banner.dataset.state = "nosession";
    banner.textContent =
      "Session required — Sign in / Open Operations Console to load priorities and queue. No fake KPI.";
    if (signIn) signIn.hidden = false;
    return;
  }
  const prio = document.getElementById("priorities");
  const loading = prio && prio.getAttribute("aria-busy") === "true";
  if (loading) {
    banner.hidden = false;
    banner.dataset.state = "loading";
    banner.textContent = "Loading company data…";
  } else {
    banner.hidden = true;
    banner.textContent = "";
    banner.removeAttribute("data-state");
  }
  if (signIn) signIn.hidden = true;
}

function vhqRenderPulse() {
  const grid = document.getElementById("vhq-pulse-grid");
  if (!grid) return;
  vhqClear(grid);
  vhqRoomsList()
    .filter((r) => r.pulse)
    .forEach((item) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "vhq-pulse-item";
      btn.setAttribute("role", "listitem");
      btn.dataset.room = item.id;
      const name = vhqEl("span", "vhq-pulse-item__name", item.pulseLabel || item.label);
      const badge = vhqEl("span", "vhq-pulse-item__badge", `[${item.status}]`);
      badge.dataset.status = item.status;
      const meta = vhqEl(
        "span",
        "vhq-pulse-item__meta",
        `${item.evidence || "—"} · Go to room`
      );
      btn.appendChild(name);
      btn.appendChild(badge);
      btn.appendChild(meta);
      btn.addEventListener("click", () => vhqRenderRoom(item.id, { historyMode: "push" }));
      grid.appendChild(btn);
    });
}

function vhqRenderFloorCards() {
  const floors = ["P3", "P2", "P1", "P0", "MAG"];
  floors.forEach((floor) => {
    const grid =
      document.querySelector(`[data-vhq-floor-grid="${floor}"]`) ||
      document.querySelector(`.vhq-floor-band[data-floor="${floor}"] .vhq-room-grid`);
    if (!grid) return;
    vhqClear(grid);
    vhqRoomsList()
      .filter((r) => r.floor === floor && r.floorCard !== false)
      .forEach((room) => {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "vhq-room" + (room.mvp ? " vhq-room--mvp" : "");
        btn.dataset.room = room.id;
        btn.dataset.status = room.status;
        const name = vhqEl("span", "vhq-room__name", room.label);
        const badge = vhqEl("span", "vhq-room__badge", `[${room.status}]`);
        badge.dataset.status = room.status;
        btn.appendChild(name);
        btn.appendChild(badge);
        grid.appendChild(btn);
      });
  });
}

let _vhqOpsBusCache = { events: [], fetchedAt: 0 };

async function vhqFetchOpsBusEvents(limit = 40) {
  if (!getToken()) {
    _vhqOpsBusCache = { events: [], fetchedAt: Date.now() };
    return [];
  }
  try {
    const data = await api(`/api/v1/commander/ops-bus/events?limit=${limit}`);
    const events = Array.isArray(data.events) ? data.events : [];
    _vhqOpsBusCache = { events, fetchedAt: Date.now() };
    return events;
  } catch {
    return _vhqOpsBusCache.events || [];
  }
}

function vhqRenderBusHandoffCards(root, events) {
  if (!root) return;
  vhqClear(root);
  if (!events || !events.length) {
    root.hidden = true;
    return;
  }
  root.hidden = false;
  root.appendChild(vhqEl("h4", null, "Operations Bus (typed)"));
  const list = document.createElement("ul");
  list.className = "vhq-bus-handoff-list";
  events.slice(0, 8).forEach((ev) => {
    const li = document.createElement("li");
    li.className = "vhq-bus-handoff-card";
    li.dataset.state = ev.approval_state || "none";
    const type = ev.event_type || "?";
    const from = ev.source_room || "?";
    const to = ev.dest_room || "?";
    const level = ev.approval_level || "L0";
    const state = ev.approval_state || "none";
    const evid = ev.evidence_id ? ` · ${ev.evidence_id}` : "";
    li.textContent = `${type}: ${from} → ${to} [${level}/${state}]${evid}`;
    list.appendChild(li);
  });
  root.appendChild(list);
  root.appendChild(
    vhqEl("p", "hint", "Typed handoffs only — no agent chat as workflow.")
  );
}

function vhqBindWizardCtaBeacon() {
  document.querySelectorAll(".vhq-cta-wizard").forEach((el) => {
    if (el.dataset.vhqBusBound === "1") return;
    el.dataset.vhqBusBound = "1";
    el.addEventListener("click", () => {
      if (!getToken()) return;
      api("/api/v1/commander/ops-bus/ingest", {
        method: "POST",
        body: {
          event_type: "wizard_started",
          source_room: "wizard-quote",
          dest_room: "sales-room",
          wizard_deeplink: el.getAttribute("href") || "https://zzpackage.flexgrafik.nl/wizard/",
          payload: { beacon: "commander_ui" },
        },
      }).catch(() => {
        /* best-effort beacon */
      });
    });
  });
}

function vhqRenderOpsFlow() {
  const line = document.getElementById("vhq-flow-line");
  if (!line) return;
  vhqClear(line);
  const flow = vhqRoomsList()
    .filter((r) => r.flowOrder != null)
    .sort((a, b) => a.flowOrder - b.flowOrder);
  flow.forEach((room, idx) => {
    if (idx > 0) {
      const arrow = vhqEl("li", "vhq-flow-arrow", "→");
      arrow.setAttribute("aria-hidden", "true");
      line.appendChild(arrow);
    }
    const li = document.createElement("li");
    li.dataset.status = room.status;
    li.appendChild(vhqEl("span", "vhq-flow-name", room.pulseLabel || room.label));
    li.appendChild(document.createTextNode(" "));
    li.appendChild(vhqEl("span", "vhq-flow-badge", room.status));
    li.appendChild(document.createTextNode(" "));
    if (room.evidence) li.appendChild(vhqEl("span", "ev", room.evidence));
    line.appendChild(li);
  });
  const breakHint = document.getElementById("vhq-flow-break");
  const order = VHQ_ROOMS["order-desk"];
  if (breakHint && order) {
    const breakText = order.parkedHeadline || order.limitation || "";
    breakHint.textContent = order.evidence
      ? `Break visible: ${breakText} · ${order.evidence}`
      : `Break visible: ${breakText}`;
    const hops = (_vhqOpsBusCache.events || []).filter((e) =>
      ["lead_qualified", "wizard_started", "order_created"].includes(e.event_type)
    );
    if (hops.length) {
      const last = hops[0];
      breakHint.textContent += ` · last bus: ${last.event_type} (${last.approval_level}/${last.approval_state})`;
    }
  }
}

function vhqRenderCriticalPin() {
  const aside = document.getElementById("vhq-critical-risk");
  if (!aside) return;
  const room = vhqRoomsList().find((r) => r.criticalPin);
  if (!room) {
    aside.hidden = true;
    return;
  }
  aside.hidden = false;
  const status = aside.querySelector(".vhq-critical-risk__status");
  const hint = aside.querySelector(".vhq-critical-risk__hint");
  if (status) {
    status.textContent = `${room.status} · SSH connection error · evidence ${room.evidence || "—"}`;
  }
  if (hint) hint.textContent = room.criticalDetail || room.limitation || "";
  const btn = aside.querySelector("[data-vhq-room]");
  if (btn) btn.setAttribute("data-vhq-room", room.id);
}

async function vhqFetchPendingApprovals() {
  if (!getToken()) return { events: [], total: 0, enabled: true, authed: false };
  try {
    const data = await api(
      "/api/v1/commander/ops-bus/events?approval_state=pending&type=approval_needed&limit=40"
    );
    const events = Array.isArray(data.events) ? data.events : [];
    return {
      events,
      total: typeof data.total === "number" ? data.total : events.length,
      enabled: data.enabled !== false,
      authed: true,
    };
  } catch {
    return { events: [], total: 0, enabled: true, authed: true, error: true };
  }
}

function vhqRenderVaultStrip() {
  const strip = document.querySelector(".vhq-vault-strip .hint[data-vhq-vault-status]");
  const vault = vhqRoomsList().find((r) => r.briefVault) || VHQ_ROOMS["approval-vault"];
  if (!strip || !vault) return;
  strip.textContent = `[${vault.status}] · ${vault.evidence || "—"} · pending — · Real path only.`;
  vhqFetchPendingApprovals().then((res) => {
    if (!strip.isConnected) return;
    if (!res.authed) {
      strip.textContent = `[${vault.status}] · ${vault.evidence || "—"} · pending — (sign in) · No invented count.`;
      return;
    }
    if (res.enabled === false) {
      strip.textContent = `[${vault.status}] · ops_bus off · pending —`;
      return;
    }
    if (res.error) {
      strip.textContent = `[${vault.status}] · ${vault.evidence || "—"} · pending — (load failed)`;
      return;
    }
    const n = res.total;
    strip.textContent = `[${vault.status}] · ${vault.evidence || "—"} · pending ${n} · EV-W6-001 · Open Vault for L2 stamps.`;
  });
}

function vhqBindVaultWorkView() {
  const room = VHQ_ROOMS["approval-vault"];
  const eyebrow = document.getElementById("vhq-work-vault-eyebrow");
  if (eyebrow && room) {
    eyebrow.textContent = `${room.label} · [${room.status}] · ${room.evidence || "EV-W6-001"}`;
  }
  const banners = document.getElementById("vhq-work-vault-banners");
  if (banners) {
    vhqClear(banners);
    banners.appendChild(
      vhqEl(
        "p",
        "vhq-honesty-banner",
        "Policy: L2 state flip only · L3/L4 Founder GO required · Hard STOP Ads/Mollie/Gate D · EV-W6-004"
      )
    );
  }
  const auditBtn = document.getElementById("vhq-vault-open-audit");
  if (auditBtn && auditBtn.dataset.bound !== "1") {
    auditBtn.dataset.bound = "1";
    auditBtn.addEventListener("click", () => {
      vhqRunAction({ type: "view", target: "audit" });
    });
  }
  vhqRenderVaultPending().catch((e) => toast(e.message || "Vault load failed", "err"));
}

async function vhqRenderVaultPending() {
  const root = document.getElementById("vhq-work-vault-pending");
  const sessionHint = document.getElementById("vhq-work-vault-session");
  if (!root) return;
  vhqClear(root);
  if (sessionHint) {
    sessionHint.hidden = true;
    sessionHint.textContent = "";
  }
  if (!getToken()) {
    if (sessionHint) {
      sessionHint.hidden = false;
      sessionHint.textContent =
        "Session required — Sign in to load pending Ops Bus approvals. No invented pending board.";
    }
    root.appendChild(vhqEl("p", "hint", "Brak sesji · insufficient_data for pending list."));
    return;
  }
  const res = await vhqFetchPendingApprovals();
  if (res.enabled === false) {
    root.appendChild(vhqEl("p", "hint", "Ops Bus disabled · pending list empty."));
    return;
  }
  if (res.error) {
    root.appendChild(vhqEl("p", "hint", "Could not load pending approvals · retry after Sign in."));
    return;
  }
  if (!res.events.length) {
    root.appendChild(
      vhqEl("p", "hint", "Brak pending · insufficient_data · EV-W6-001 (honest empty).")
    );
    return;
  }
  const list = document.createElement("ul");
  list.className = "vhq-vault-card-list";
  res.events.forEach((ev) => {
    list.appendChild(vhqBuildApprovalCard(ev));
  });
  root.appendChild(list);
}

function vhqBuildApprovalCard(ev) {
  const li = document.createElement("li");
  li.className = "vhq-vault-card";
  const level = ev.approval_level || "L0";
  const isL2 = level === "L2";
  const isStop = level === "L3" || level === "L4";
  li.dataset.level = level;
  if (isStop) li.dataset.stop = "1";

  const payload = ev.payload || {};
  const parentType = payload.parent_type || "—";
  const from = ev.source_room || "?";
  const to = ev.dest_room || "approval-vault";
  const evid = ev.evidence_id || "—";
  const corr = ev.correlation_id || "—";

  li.appendChild(
    vhqEl(
      "p",
      "vhq-vault-card__title",
      `${ev.event_type || "approval_needed"} · ${level}/${ev.approval_state || "pending"}`
    )
  );
  li.appendChild(
    vhqEl("p", "hint", `${from} → ${to} · parent ${parentType} · ${evid} · corr ${corr}`)
  );

  if (isStop) {
    li.appendChild(
      vhqEl(
        "p",
        "vhq-vault-card__stop",
        `${level} STOP · Founder GO required · silent approve forbidden · Ads/Mollie/Gate D/deploy class · EV-W6-004`
      )
    );
  }

  const actions = document.createElement("div");
  actions.className = "vhq-vault-card__actions";

  if (isL2 && (ev.approval_state || "pending") === "pending") {
    const approveBtn = document.createElement("button");
    approveBtn.type = "button";
    approveBtn.className = "primary";
    approveBtn.textContent = "Approve (L2)";
    approveBtn.addEventListener("click", () => {
      vhqVaultDecide(ev.event_id, "approved").catch((e) => toast(e.message, "err"));
    });
    const rejectBtn = document.createElement("button");
    rejectBtn.type = "button";
    rejectBtn.className = "secondary";
    rejectBtn.textContent = "Reject (L2)";
    rejectBtn.addEventListener("click", () => {
      vhqVaultDecide(ev.event_id, "rejected").catch((e) => toast(e.message, "err"));
    });
    actions.appendChild(approveBtn);
    actions.appendChild(rejectBtn);
  }

  if (from && VHQ_ROOMS[from]) {
    const srcBtn = document.createElement("button");
    srcBtn.type = "button";
    srcBtn.className = "secondary";
    srcBtn.textContent = `Open source · ${from}`;
    srcBtn.setAttribute("data-vhq-room", from);
    actions.appendChild(srcBtn);
  }

  li.appendChild(actions);
  return li;
}

async function vhqVaultDecide(eventId, state) {
  const label = state === "approved" ? "Approve" : "Reject";
  const confirmed = await confirmAction(
    `${label} this L2 Ops Bus approval? State flip only — no deploy, publish, Ads, or Mollie.`
  );
  if (!confirmed || !confirmed.ok) return;
  const res = await api(`/api/v1/commander/ops-bus/events/${encodeURIComponent(eventId)}/approval`, {
    method: "POST",
    body: { state },
  });
  const synced = (res && res.synced_event_ids) || [];
  const syncNote = synced.length ? ` · peer sync ${synced.length}` : "";
  toast(
    `L2 ${state}${syncNote} · EV-S3-001 · no side effects`,
    "ok",
  );
  await vhqRenderVaultPending();
  vhqRenderVaultStrip();
}

function vhqRenderHandoffStrip(root) {
  if (!root) return;
  vhqClear(root);
  const flow = vhqRoomsList()
    .filter((r) => r.flowOrder != null)
    .sort((a, b) => a.flowOrder - b.flowOrder);
  flow.forEach((room, idx) => {
    if (idx > 0) {
      const arrow = vhqEl("span", "vhq-flow-arrow", "→");
      arrow.setAttribute("aria-hidden", "true");
      root.appendChild(arrow);
    }
    const span = document.createElement("span");
    span.dataset.status = room.status;
    span.textContent = `${room.pulseLabel || room.label} ${room.status}`;
    root.appendChild(span);
  });
}

function vhqBindWorkViews() {
  const sales = VHQ_ROOMS["sales-room"];
  const wizard = VHQ_ROOMS["wizard-quote"];
  const mkt = VHQ_ROOMS["marketing-studio"];
  const order = VHQ_ROOMS["order-desk"];

  const salesEyebrow = document.querySelector('[data-vhq-work="sales-room"] .vhq-work-eyebrow');
  if (salesEyebrow && sales) {
    salesEyebrow.textContent = `${sales.label} · [${sales.status}] · ${sales.evidence || "—"}`;
  }
  vhqRenderHandoffStrip(document.querySelector('[data-vhq-work="sales-room"] .vhq-handoff-strip'));

  const wizEyebrow = document.querySelector('[data-vhq-work="wizard-quote"] .vhq-work-eyebrow');
  if (wizEyebrow && wizard) {
    wizEyebrow.textContent = `${wizard.label} · [${wizard.status}] · ${wizard.evidence || "—"}`;
  }
  const wizMeta = document.getElementById("vhq-work-wizard-meta");
  if (wizMeta && wizard) {
    vhqClear(wizMeta);
    const rows = [
      ["Status", `[${wizard.status}] · Wizard SPA Stap 1–9`],
      ["SoT", wizard.sotLabel || wizard.sotHref || "—"],
      [
        "Evidence",
        `${wizard.evidence || "—"} · last_verified ${wizard.lastVerified || "insufficient_data"}`,
      ],
      [
        "KPI",
        (wizard.kpi || [])
          .map((k) => `${k.id} → ${k.value}${k.note ? ` (${k.note})` : ""}`)
          .join("; ") || "insufficient_data",
      ],
    ];
    rows.forEach(([dt, dd]) => {
      const wrap = document.createElement("div");
      wrap.appendChild(vhqEl("dt", null, dt));
      const ddEl = document.createElement("dd");
      if (dt === "SoT" && wizard.sotHref && /^https?:/i.test(wizard.sotHref)) {
        ddEl.appendChild(vhqSafeLink(wizard.sotHref, wizard.sotHref));
      } else {
        ddEl.textContent = dd;
      }
      wrap.appendChild(ddEl);
      wizMeta.appendChild(wrap);
    });
  }
  const wizChild = document.getElementById("vhq-work-wizard-handoff");
  if (wizChild && order) {
    vhqClear(wizChild);
    const p1 = document.createElement("p");
    const strong = document.createElement("strong");
    const handoffLabel = order.evidence
      ? `Future handoff → ${order.label} [${order.status}] · ${order.evidence}`
      : `Future handoff → ${order.label} [${order.status}]`;
    strong.textContent = handoffLabel;
    p1.appendChild(strong);
    wizChild.appendChild(p1);
    const parkedLine = order.evidence
      ? `${order.parkedHeadline || order.limitation || ""} · ${order.evidence}`
      : order.parkedHeadline || order.limitation || "";
    wizChild.appendChild(vhqEl("p", "hint", parkedLine));
    wizChild.appendChild(
      vhqEl(
        "p",
        "hint",
        "Limitation: Mollie LIVE / Purchase = L4 separate Founder GO — not from this room."
      )
    );
  }
  const wizBusEvents = (_vhqOpsBusCache.events || []).filter((e) =>
    ["lead_qualified", "wizard_started", "order_created", "approval_needed"].includes(
      e.event_type
    )
  );
  vhqRenderBusHandoffCards(document.getElementById("vhq-work-wizard-bus"), wizBusEvents);
  vhqBindWizardCtaBeacon();
  const wizOrderBtn = document.getElementById("vhq-wizard-order-parked");
  if (wizOrderBtn && order) {
    wizOrderBtn.textContent = order.evidence
      ? `${order.label} handoff [${order.status}] · ${order.evidence}`
      : `${order.label} handoff [${order.status}]`;
    wizOrderBtn.setAttribute("data-vhq-room", order.id);
  }

  const mktEyebrow = document.querySelector('[data-vhq-work="marketing-studio"] .vhq-work-eyebrow');
  if (mktEyebrow && mkt) mktEyebrow.textContent = `${mkt.label} · honest pin`;
  const banners = document.getElementById("vhq-work-marketing-banners");
  if (banners && mkt) {
    vhqClear(banners);
    (mkt.honesty || []).forEach((h) => {
      const p = vhqEl("p", "vhq-honesty-banner", h.text);
      p.dataset.status = h.status;
      p.setAttribute("role", "status");
      banners.appendChild(p);
    });
  }
  const mktMeta = document.getElementById("vhq-work-marketing-meta");
  if (mktMeta && mkt) {
    vhqClear(mktMeta);
    const rows = [
      ["Status", `${mkt.status} — campaign state not verified`],
      ["Evidence", mkt.evidence || "—"],
      ["Explanation", mkt.sotLabel || ""],
      ["Campaign KPIs", "insufficient_data"],
      ["Primary action", "Observe Marketing tab only — no publish / Ads from HQ"],
    ];
    rows.forEach(([dt, dd]) => {
      const wrap = document.createElement("div");
      wrap.appendChild(vhqEl("dt", null, dt));
      wrap.appendChild(vhqEl("dd", null, dd));
      mktMeta.appendChild(wrap);
    });
  }

  const opsWorkDom = {
    "order-desk": "order",
    "production-control": "production",
    "preflight-quality": "preflight",
    "dispatch-returns": "dispatch",
  };
  Object.keys(opsWorkDom).forEach((id) => {
    const room = VHQ_ROOMS[id];
    if (!room) return;
    const short = opsWorkDom[id];
    const eyebrow = document.querySelector(`[data-vhq-work="${id}"] .vhq-work-eyebrow`);
    if (eyebrow) {
      eyebrow.textContent = `${room.label} · [${room.status}] · ${room.evidence || "—"}`;
    }
    const title = document.querySelector(`[data-vhq-work="${id}"] .vhq-work-head h3`);
    if (title && room.directorQ) title.textContent = room.directorQ;
    const banners = document.getElementById(`vhq-work-${short}-banners`);
    if (banners) {
      vhqClear(banners);
      (room.honesty || []).forEach((h) => {
        const p = vhqEl("p", "vhq-honesty-banner", h.text);
        p.dataset.status = h.status;
        p.setAttribute("role", "status");
        banners.appendChild(p);
      });
    }
    const meta = document.getElementById(`vhq-work-${short}-meta`);
    if (meta) {
      vhqClear(meta);
      const kpiText =
        (room.kpi || [])
          .map((k) => `${k.id} → ${k.value}${k.note ? ` (${k.note})` : ""}`)
          .join("; ") || "insufficient_data";
      const rows = [
        ["Status", `[${room.status}] · ${room.purpose || ""}`],
        ["Evidence", `${room.evidence || "—"} · last_verified ${room.lastVerified || "insufficient_data"}`],
        ["SoT", room.sotLabel || "—"],
        ["Limitation", room.limitation || "—"],
        ["KPI", kpiText],
        ["Primary action", "None — shell only (no LIVE desk)"],
      ];
      rows.forEach(([dt, dd]) => {
        const wrap = document.createElement("div");
        wrap.appendChild(vhqEl("dt", null, dt));
        wrap.appendChild(vhqEl("dd", null, dd));
        meta.appendChild(wrap);
      });
    }
    document.querySelectorAll(`[data-vhq-work="${id}"] [data-vhq-room="order-desk"]`).forEach((btn) => {
      if (!order || btn.id === "vhq-wizard-order-parked") return;
      btn.textContent = order.evidence
        ? `${order.label} [${order.status}] · ${order.evidence}`
        : `${order.label} [${order.status}]`;
    });
  });
}

function vhqMapStateText(room, hop) {
  if (hop && hop.stateText) return hop.stateText;
  if (room.technicalProbe) {
    return `${room.status} · technical readiness probe · ${room.evidence || ""}`.trim();
  }
  return vhqStatusLine(room);
}

function vhqRenderSystemMap() {
  const root = document.getElementById("system-map-links");
  if (!root) return;
  vhqClear(root);
  root.dataset.hopsBound = "0";

  const appendHop = (room, hop) => {
    const floor = hop.mapFloor || room.floor;
    const interactive = !!(hop.interactive && hop.href);
    const el = interactive ? document.createElement("a") : document.createElement("div");
    el.className = "map-link" + (interactive ? "" : " map-status");
    if (room.status === "PARKED") el.classList.add("is-parked");
    if (room.status === "UNVERIFIED") el.classList.add("is-unverified");
    if (interactive) {
      el.href = hop.href;
      if (/^https?:/i.test(hop.href) || hop.href.startsWith("/")) {
        el.target = "_blank";
        el.rel = "noopener noreferrer";
      }
      el.dataset.hop = hop.label || room.label;
    } else {
      el.setAttribute("role", "status");
      el.tabIndex = -1;
    }
    el.dataset.roomId = room.id;
    el.dataset.floor = floor;
    el.dataset.campusState = hop.status || room.status;
    el.appendChild(vhqEl("span", "hop-label", hop.label || room.label));
    el.appendChild(vhqEl("span", "hop-meta", hop.meta || `${floor} · ${room.label}`));
    el.appendChild(
      vhqEl("span", "hop-state", vhqMapStateText({ ...room, status: hop.status || room.status }, hop))
    );
    root.appendChild(el);
  };

  // Stable Director-first order for map
  const order = [
    "mission-control",
    "vcms-os-zone",
    "knowledge-library",
    "wizard-quote",
    "design-agent-probe",
    "sales-room",
    "analytics-finance",
    "order-desk",
    "marketing-studio",
    "compliance-audit",
    "supplier-dock",
  ];
  order.forEach((id) => {
    const room = VHQ_ROOMS[id];
    if (!room) return;
    if (room.mapHops && room.mapHops.length) {
      room.mapHops.forEach((h) => appendHop(room, h));
      return;
    }
    if (room.mapHop) appendHop(room, room.mapHop);
  });

  if (typeof bindSystemMapHops === "function") bindSystemMapHops();
}

function vhqRenderSettingsMap() {
  const ul = document.getElementById("settings-system-map");
  if (!ul) return;
  vhqClear(ul);
  const ids = [
    "mission-control",
    "vcms-os-zone",
    "knowledge-library",
    "wizard-quote",
    "design-agent-probe",
    "sales-room",
    "compliance-audit",
    "analytics-finance",
    "order-desk",
    "marketing-studio",
    "supplier-dock",
  ];
  ids.forEach((id) => {
    const room = VHQ_ROOMS[id];
    if (!room) return;
    if (room.mapHops) {
      room.mapHops.forEach((h) => {
        const li = document.createElement("li");
        li.textContent = `${h.mapFloor || room.floor} ${h.label} ${h.status || room.status}${
          room.evidence ? ` · ${room.evidence}` : ""
        }: ${h.href || "HITL"}`;
        ul.appendChild(li);
      });
      return;
    }
    const li = document.createElement("li");
    const href = (room.mapHop && room.mapHop.href) || room.sotHref || "";
    li.textContent = `${room.floor} ${room.label} ${vhqStatusLine(room)}${href ? `: ${href}` : ""}`;
    ul.appendChild(li);
  });
  const pilot = vhqRoomsList()
    .filter((r) => r.truthPilot)
    .map((r) => r.label)
    .join(" · ");
  const foot = document.createElement("li");
  foot.textContent = `W3 Truth Cards pilot (Console appendix): ${pilot} — read-only · manifest VHQ_ROOMS`;
  ul.appendChild(foot);
}

function vhqRenderTruthCards() {
  const grid = document.querySelector("#truth-cards-pilot .truth-card-grid");
  if (!grid) return;
  vhqClear(grid);
  vhqRoomsList()
    .filter((r) => r.truthPilot)
    .forEach((room) => {
      const art = document.createElement("article");
      art.className = "truth-card";
      art.dataset.roomId = room.id;
      art.dataset.truthStatus = room.status;

      const head = vhqEl("header", "truth-card__head");
      head.appendChild(vhqEl("h4", "truth-card__name", room.label));
      head.appendChild(vhqEl("p", "truth-card__purpose", room.purpose || ""));
      art.appendChild(head);

      const status = vhqEl("p", "truth-card__status");
      status.appendChild(document.createTextNode(`${room.status} · `));
      if (room.evidence) {
        const ev = vhqEl("span", "ev", room.evidence);
        status.appendChild(ev);
      }
      if (room.id === "wizard-quote") {
        status.appendChild(document.createTextNode(" · Wizard SPA Stap 1–9"));
      }
      if (room.id === "order-desk") {
        status.appendChild(document.createTextNode(" · no operational desk"));
      }
      if (room.id === "marketing-studio") {
        status.appendChild(document.createTextNode(" — campaign state not verified"));
      }
      art.appendChild(status);

      const action = vhqEl("p", "truth-card__action");
      const ak = vhqEl("span", "k", "Primary action:");
      action.appendChild(ak);
      action.appendChild(document.createTextNode(" "));
      if (room.action && room.action.type === "external") {
        action.appendChild(vhqSafeLink(room.action.href, room.action.label, "truth-card__cta"));
      } else if (room.action) {
        action.appendChild(vhqEl("span", "muted", room.action.label));
      } else if (room.id === "marketing-studio") {
        action.appendChild(vhqEl("span", "muted", "Observe only — no execution in Campus sessions"));
      } else if (room.id === "order-desk") {
        action.appendChild(vhqEl("span", "muted", "None — desk not implemented (EV-W2-010)"));
      } else {
        action.appendChild(vhqEl("span", "muted", "—"));
      }
      art.appendChild(action);

      const sot = vhqEl("p", "truth-card__sot");
      sot.appendChild(vhqEl("span", "k", "SoT:"));
      sot.appendChild(document.createTextNode(" "));
      if (room.sotHref && (/^https?:/i.test(room.sotHref) || room.sotHref.startsWith("/"))) {
        sot.appendChild(vhqSafeLink(room.sotHref, room.sotLabel || room.sotHref, "truth-card__cta"));
      } else {
        sot.appendChild(document.createTextNode(room.sotLabel || "—"));
      }
      art.appendChild(sot);

      if (room.kpi && room.kpi.length) {
        const ul = document.createElement("ul");
        ul.className = "truth-card__kpi";
        ul.setAttribute("aria-label", `KPI ${room.label}`);
        room.kpi.forEach((k) => {
          const li = document.createElement("li");
          li.appendChild(vhqEl("span", "k", `${k.id}:`));
          li.appendChild(document.createTextNode(` ${k.value}`));
          if (k.note) {
            li.appendChild(document.createTextNode(" "));
            li.appendChild(vhqEl("span", "muted", `(${k.note})`));
          }
          ul.appendChild(li);
        });
        art.appendChild(ul);
      }

      const meta = vhqEl("p", "truth-card__meta");
      meta.appendChild(vhqEl("span", "k", "Owner:"));
      meta.appendChild(document.createTextNode(` ${room.owner || "—"} · `));
      meta.appendChild(vhqEl("span", "k", "last_verified:"));
      meta.appendChild(document.createTextNode(` ${room.lastVerified || "insufficient_data"}`));
      art.appendChild(meta);

      art.appendChild(
        (() => {
          const p = vhqEl("p", "truth-card__limit");
          p.appendChild(vhqEl("span", "k", "Limitation:"));
          p.appendChild(document.createTextNode(` ${room.limitation || "—"}`));
          return p;
        })()
      );

      grid.appendChild(art);
    });
}

function vhqRenderTeleportOptions() {
  const sel = document.getElementById("vhq-teleport");
  if (!sel) return;
  const current = sel.value;
  vhqClear(sel);
  const opt0 = document.createElement("option");
  opt0.value = "";
  opt0.textContent = "Select room…";
  sel.appendChild(opt0);
  const floors = ["P3", "P2", "P1", "P0", "MAG"];
  floors.forEach((floor) => {
    vhqRoomsList()
      .filter((r) => r.floor === floor && r.floorCard !== false)
      .forEach((room) => {
        const opt = document.createElement("option");
        opt.value = room.id;
        opt.textContent = `${floor} · ${room.label}`;
        sel.appendChild(opt);
      });
  });
  if (current && VHQ_ROOMS[current]) sel.value = current;
}

function vhqRenderAllManifestSurfaces() {
  vhqRenderFloorCards();
  vhqRenderPulse();
  vhqRenderOpsFlow();
  vhqRenderCriticalPin();
  vhqRenderVaultStrip();
  vhqBindWorkViews();
  vhqRenderSystemMap();
  vhqRenderSettingsMap();
  vhqRenderTruthCards();
  vhqRenderTeleportOptions();
  vhqRefreshOpsBusSurfaces();
}

async function vhqRefreshOpsBusSurfaces() {
  await vhqFetchOpsBusEvents(40);
  vhqRenderOpsFlow();
  const wizBusEvents = (_vhqOpsBusCache.events || []).filter((e) =>
    ["lead_qualified", "wizard_started", "order_created", "approval_needed"].includes(
      e.event_type
    )
  );
  vhqRenderBusHandoffCards(document.getElementById("vhq-work-wizard-bus"), wizBusEvents);
  const orderEvents = (_vhqOpsBusCache.events || []).filter(
    (e) => e.event_type === "order_created"
  );
  const orderBus = document.getElementById("vhq-work-order-bus");
  if (orderBus) {
    vhqClear(orderBus);
    if (!orderEvents.length) {
      orderBus.hidden = true;
    } else {
      orderBus.hidden = false;
      orderBus.appendChild(vhqEl("h4", null, "Bus trail (INT-002 ingest)"));
      orderBus.appendChild(
        vhqEl(
          "p",
          "hint",
          "Events below are WooCommerce mirrors — not an operational Order Desk. Desk remains PARKED · EV-W2-010."
        )
      );
      const ul = document.createElement("ul");
      ul.className = "vhq-bus-handoff-list";
      orderEvents.slice(0, 10).forEach((ev) => {
        const li = document.createElement("li");
        li.className = "vhq-bus-handoff-card";
        li.textContent = `order_created · ${ev.payload_ref} · ${ev.approval_level}/${ev.approval_state} · ${ev.evidence_id || "EV-W5-003"}`;
        ul.appendChild(li);
      });
      orderBus.appendChild(ul);
    }
  }
  vhqBindWizardCtaBeacon();
}

/**
 * Local-only propagation fixture. Temporarily mutates one field, proves renderers
 * read VHQ_ROOMS, then restores. Safe for dogfood — does not persist.
 */
function vhqManifestPropagationTest() {
  const room = VHQ_ROOMS["marketing-studio"];
  if (!room) return { pass: false, error: "missing marketing-studio" };
  const orig = room.status;
  const token = "TEST_PROP_W32";
  room.status = token;
  try {
    vhqRenderAllManifestSurfaces();
    const hay = [
      document.getElementById("vhq-pulse-grid")?.textContent || "",
      document.querySelector('[data-room="marketing-studio"]')?.textContent || "",
      document.getElementById("system-map-links")?.textContent || "",
      document.getElementById("settings-system-map")?.textContent || "",
      document.querySelector("#truth-cards-pilot .truth-card-grid")?.textContent || "",
    ];
    const hits = hay.map((t) => t.includes(token));
    const pass = hits.every(Boolean);
    return { pass, hits, surfaces: ["pulse", "floor", "system-map", "settings", "truth"] };
  } finally {
    room.status = orig;
    vhqRenderAllManifestSurfaces();
  }
}

window.vhqManifestPropagationTest = vhqManifestPropagationTest;

function vhqGoMissionControl(opts = {}) {
  const historyMode = opts.historyMode || "push";
  if (vhqIsPrimary()) {
    vhqApplyLegacyShellAttrs(false);
    const shell = document.getElementById("vhq-shell");
    if (shell) shell.hidden = false;
    showView("hq");
    document.body.classList.add("vhq-open");
    vhqOpen = true;
    vhqDetachFocusGuard();
    vhqSetBackdropInert(false);
    vhqRenderRoom("mission-control", { historyMode });
    return;
  }
  vhqOpenShell("mission-control");
}

function vhqGoConsole(opts = {}) {
  const focusAuth = !!opts.focusAuth;
  const historyMode = opts.historyMode || "push";
  if (vhqIsPrimary()) {
    try {
      vhqRestoreAllSlots();
    } catch (err) {
      console.warn("vhqRestoreAllSlots failed", err);
    }
    document.body.classList.remove("vhq-open", "vhq-mode-command", "vhq-mode-work", "vhq-mode-world");
    vhqOpen = false;
    vhqDetachFocusGuard();
    vhqSetBackdropInert(false);
    showView("home");
    if (historyMode !== "none") {
      vhqWriteHistory("console", { replace: historyMode === "replace" });
    }
    if (focusAuth || !(typeof getToken === "function" && getToken())) {
      setAuthExpanded(true);
      const jwt = document.getElementById("jwt-input");
      if (jwt) {
        jwt.focus();
        return;
      }
    }
    const enter = document.getElementById("vhq-enter");
    if (enter) enter.focus();
    return;
  }
  vhqOpenOperationsConsole({ focusAuth });
}

/** Legacy: close modal overlay and land on Operations Console (home). */
function vhqOpenOperationsConsole(opts = {}) {
  const focusAuth = !!opts.focusAuth;
  vhqClose({ restoreFocus: false });
  showView("home");
  if (focusAuth || !(typeof getToken === "function" && getToken())) {
    setAuthExpanded(true);
    const jwt = document.getElementById("jwt-input");
    if (jwt) {
      jwt.focus();
      return;
    }
  }
  const enter = document.getElementById("vhq-enter");
  if (enter) enter.focus();
}

function vhqShowWorkPanel(roomId) {
  document.querySelectorAll(".vhq-work-panel").forEach((panel) => {
    const match = panel.getAttribute("data-vhq-work") === roomId;
    panel.hidden = !match;
  });
}

function vhqUpdateWorkSessionBanner() {
  const banner = document.getElementById("vhq-work-session-banner");
  if (!banner) return;
  const hasToken = typeof getToken === "function" && !!getToken();
  if (!hasToken) {
    banner.hidden = false;
    banner.dataset.state = "nosession";
    banner.textContent =
      "Session required — Sign in / Open Operations Console to load Sales queue. No fake leads.";
    return;
  }
  banner.hidden = true;
  banner.textContent = "";
  banner.removeAttribute("data-state");
}

function vhqApplyRoomChrome(roomId) {
  const room = VHQ_ROOMS[roomId];
  if (roomId === "mission-control") {
    vhqSetMode("command");
    vhqShowWorkPanel(null);
    vhqMountSlotsForRoom("mission-control");
    vhqRenderPulse();
    vhqRenderOpsFlow();
    vhqRenderCriticalPin();
    vhqRenderVaultStrip();
    vhqUpdateSessionBanner();
    if (typeof getToken === "function" && getToken()) {
      loadHome().catch((e) => toast(e.message, "err"));
    }
  } else if (roomId === "sales-room") {
    vhqSetMode("work");
    vhqShowWorkPanel("sales-room");
    vhqMountSlotsForRoom("sales-room");
    vhqBindWorkViews();
    vhqUpdateWorkSessionBanner();
    if (typeof getToken === "function" && getToken()) {
      loadHome().catch((e) => toast(e.message, "err"));
    }
  } else if (roomId === "wizard-quote") {
    vhqSetMode("work");
    vhqRestoreAllSlots();
    vhqShowWorkPanel("wizard-quote");
    vhqBindWorkViews();
  } else if (roomId === "marketing-studio") {
    vhqSetMode("work");
    vhqRestoreAllSlots();
    vhqShowWorkPanel("marketing-studio");
    vhqBindWorkViews();
  } else if (
    roomId === "order-desk" ||
    roomId === "production-control" ||
    roomId === "preflight-quality" ||
    roomId === "dispatch-returns"
  ) {
    vhqSetMode("work");
    vhqRestoreAllSlots();
    vhqShowWorkPanel(roomId);
    vhqBindWorkViews();
    const workTitle = document.querySelector(`[data-vhq-work="${roomId}"] .vhq-work-head h3`);
    if (workTitle) {
      workTitle.setAttribute("tabindex", "-1");
      try {
        workTitle.focus({ preventScroll: true });
      } catch (_) {
        workTitle.focus();
      }
    }
  } else if (roomId === "approval-vault") {
    vhqSetMode("work");
    vhqRestoreAllSlots();
    vhqShowWorkPanel("approval-vault");
    vhqBindVaultWorkView();
    vhqUpdateWorkSessionBanner();
    const workTitle = document.getElementById("vhq-work-vault-title");
    if (workTitle) {
      workTitle.setAttribute("tabindex", "-1");
      try {
        workTitle.focus({ preventScroll: true });
      } catch (_) {
        workTitle.focus();
      }
    }
  } else {
    vhqSetMode("world");
    vhqRestoreAllSlots();
    vhqShowWorkPanel(null);
  }
  if (!room) return;
}


function vhqFocusableNodes() {
  const shell = document.getElementById("vhq-shell");
  if (!shell) return [];
  if (!vhqIsPrimary() && shell.hidden) return [];
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

function vhqClearBackdropInert() {
  document.querySelectorAll(".vhq-backdrop-inert").forEach((el) => {
    el.removeAttribute("inert");
    el.removeAttribute("aria-hidden");
    el.classList.remove("vhq-backdrop-inert");
  });
}

function vhqSetBackdropInert(on) {
  if (vhqIsPrimary() || !on) {
    // Primary shell is a normal view — never inert the app chrome.
    // Legacy close also clears fully before restoring shell to #view-hq.
    vhqClearBackdropInert();
    return;
  }
  // Legacy open: shell must already be portaled to body (sibling of .coi-shell).
  // Never inert #vhq-shell or any ancestor that contains it.
  const shell = document.getElementById("vhq-shell");
  document.querySelectorAll("body > *:not(#toast)").forEach((el) => {
    if (el === shell || el.id === "vhq-shell") return;
    if (shell && el.contains(shell)) return;
    el.setAttribute("inert", "");
    el.setAttribute("aria-hidden", "true");
    el.classList.add("vhq-backdrop-inert");
  });
}

function vhqDetachFocusGuard() {
  if (vhqFocusinGuard) {
    document.removeEventListener("focusin", vhqFocusinGuard, true);
    vhqFocusinGuard = null;
  }
}

function vhqAttachFocusGuard() {
  if (vhqIsPrimary()) return; // no modal focus trap in primary shell
  vhqDetachFocusGuard();
  vhqFocusinGuard = (e) => {
    if (!vhqOpen) return;
    const shell = document.getElementById("vhq-shell");
    if (!shell) return;
    if (shell.contains(e.target)) return;
    e.preventDefault();
    const nodes = vhqFocusableNodes();
    const hasToken = typeof getToken === "function" && !!getToken();
    const fallback =
      (!hasToken && document.getElementById("vhq-sign-in")) ||
      document.getElementById("vhq-to-console") ||
      document.getElementById("vhq-close") ||
      nodes[0];
    if (fallback) fallback.focus();
  };
  document.addEventListener("focusin", vhqFocusinGuard, true);
}

function vhqTrapTab(e) {
  if (vhqIsPrimary()) return;
  if (e.key !== "Tab" || !vhqOpen) return;
  const shell = document.getElementById("vhq-shell");
  if (!shell) return;
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

function vhqClose(opts = {}) {
  if (vhqIsPrimary()) {
    // Esc ladder B handled by vhqEscLadder; Close button → Console
    vhqGoConsole({ focusAuth: false, historyMode: opts.historyMode || "push" });
    return;
  }
  const shell = document.getElementById("vhq-shell");
  if (!shell) return;
  try {
    vhqRestoreAllSlots();
  } catch (err) {
    console.warn("vhqRestoreAllSlots failed", err);
  }
  shell.hidden = true;
  document.body.classList.remove("vhq-open", "vhq-mode-command", "vhq-mode-work", "vhq-mode-world");
  vhqOpen = false;
  vhqDetachFocusGuard();
  vhqSetBackdropInert(false);
  vhqPortalShellForLegacy(false);
  // Keep body.vhq-legacy + dialog attrs while ?vhq_shell=legacy for next open.
  showView("home");
  if (opts.restoreFocus === false) return;
  const enterBtn = document.getElementById("vhq-enter");
  if (enterBtn && typeof enterBtn.focus === "function") {
    enterBtn.focus();
  } else if (vhqLastFocus && typeof vhqLastFocus.focus === "function") {
    vhqLastFocus.focus();
  }
}

function vhqEscLadder() {
  if (!vhqIsPrimary()) {
    vhqClose();
    return;
  }
  // B: room → Mission Control → Operations Console
  const onHq = document.getElementById("view-hq") && !document.getElementById("view-hq").hidden;
  if (!onHq || !vhqOpen) {
    return;
  }
  if (vhqCurrentRoom && vhqCurrentRoom !== "mission-control") {
    vhqGoMissionControl({ historyMode: "push" });
    return;
  }
  if (document.body.classList.contains("vhq-mode-world")) {
    vhqGoMissionControl({ historyMode: "push" });
    return;
  }
  vhqGoConsole({ focusAuth: false, historyMode: "push" });
}

function vhqOpenShell(roomId) {
  const shell = document.getElementById("vhq-shell");
  if (!shell) return;
  if (vhqIsPrimary()) {
    vhqGoMissionControl({ historyMode: "push" });
    if (roomId && roomId !== "mission-control") {
      vhqRenderRoom(roomId, { historyMode: "push" });
    }
    return;
  }
  vhqApplyLegacyShellAttrs(true);
  vhqPortalShellForLegacy(true);
  vhqLastFocus = document.getElementById("vhq-enter") || document.activeElement;
  shell.hidden = false;
  showView("hq");
  document.body.classList.add("vhq-open");
  vhqOpen = true;
  vhqSetBackdropInert(true);
  vhqRenderRoom(roomId || "mission-control", { historyMode: "none" });
  vhqAttachFocusGuard();
  const hasToken = typeof getToken === "function" && !!getToken();
  const focusBtn = !hasToken
    ? document.getElementById("vhq-sign-in") || document.getElementById("vhq-to-console")
    : document.getElementById("vhq-to-console") || document.getElementById("vhq-close");
  if (focusBtn) focusBtn.focus();
}

function vhqRunAction(action) {
  if (!action) return;
  if (action.type === "external") {
    window.open(action.href, "_blank", "noopener,noreferrer");
    return;
  }
  if (action.type === "room" && action.target) {
    vhqRenderRoom(action.target, { historyMode: "push" });
    return;
  }
  if (action.type === "view") {
    if (vhqIsPrimary()) {
      vhqParkPrimaryShell();
      showView(action.target);
      vhqWriteHistory("", { replace: false });
    } else {
      vhqClose({ restoreFocus: false });
      showView(action.target);
    }
    return;
  }
  if (action.type === "focus-queue") {
    if (vhqCurrentRoom !== "sales-room") {
      vhqRenderRoom("sales-room", { historyMode: "push" });
    }
    const el = document.getElementById("queue-list");
    if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
    return;
  }
  if (action.type === "goto-home") {
    vhqGoConsole({ focusAuth: false, historyMode: "push" });
    const el = document.querySelector(action.target);
    if (el) {
      el.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }
}

function vhqApplyUrlState(raw, opts = {}) {
  const historyMode = opts.historyMode || "none";
  const state = (raw || "mc").toLowerCase();
  vhqApplyingHistory = true;
  try {
    if (state === "console") {
      vhqGoConsole({ focusAuth: false, historyMode: "none" });
      vhqNavState = "console";
      return;
    }
    if (state === "world") {
      if (vhqIsPrimary()) {
        vhqApplyLegacyShellAttrs(false);
        showView("hq");
        document.body.classList.add("vhq-open");
        vhqOpen = true;
      } else {
        vhqOpenShell("mission-control");
      }
      vhqShowFloorBrowse(vhqCurrentFloor || "P3", { historyMode: "none" });
      vhqNavState = "world";
      return;
    }
    if (state === "mc" || state === "mission-control") {
      vhqGoMissionControl({ historyMode: "none" });
      vhqNavState = "mc";
      return;
    }
    const resolved = vhqResolveRoomId(state);
    if (resolved && VHQ_ROOMS[resolved]) {
      if (vhqIsPrimary()) {
        vhqApplyLegacyShellAttrs(false);
        showView("hq");
        document.body.classList.add("vhq-open");
        vhqOpen = true;
        vhqRenderRoom(resolved, { historyMode: "none" });
      } else {
        vhqOpenShell(resolved);
      }
      vhqNavState = state;
      return;
    }
    vhqGoMissionControl({ historyMode: "none" });
    vhqNavState = "mc";
  } finally {
    vhqApplyingHistory = false;
    if (historyMode === "replace" && vhqIsPrimary()) {
      vhqWriteHistory(vhqNavState || "mc", { replace: true });
    }
  }
}

function bindVhqShell() {
  const enter = document.getElementById("vhq-enter");
  const shell = document.getElementById("vhq-shell");
  if (!enter || !shell) return;

  enter.addEventListener("click", () => vhqGoMissionControl({ historyMode: "push" }));
  document.getElementById("vhq-close")?.addEventListener("click", () => {
    vhqGoConsole({ focusAuth: false, historyMode: "push" });
  });
  document.getElementById("vhq-to-console")?.addEventListener("click", () => {
    vhqGoConsole({ focusAuth: false, historyMode: "push" });
  });
  document.getElementById("vhq-sign-in")?.addEventListener("click", () => {
    vhqGoConsole({ focusAuth: true, historyMode: "push" });
  });
  document.getElementById("vhq-to-mc")?.addEventListener("click", () => {
    vhqGoMissionControl({ historyMode: "push" });
  });
  document.getElementById("vhq-open-vault")?.addEventListener("click", () => {
    vhqRenderRoom("approval-vault", { historyMode: "push" });
  });
  document.getElementById("vhq-open-audit")?.addEventListener("click", () => {
    vhqRunAction({ type: "view", target: "audit" });
  });
  document.getElementById("vhq-action-audit")?.addEventListener("click", () => {
    vhqRunAction({ type: "view", target: "audit" });
  });
  document.getElementById("vhq-sales-focus-queue")?.addEventListener("click", () => {
    vhqRunAction({ type: "focus-queue" });
  });
  document.getElementById("vhq-marketing-observe")?.addEventListener("click", () => {
    vhqRunAction({ type: "view", target: "marketing" });
  });
  document.querySelectorAll("[data-vhq-jump]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const jump = btn.getAttribute("data-vhq-jump");
      if (jump === "priorities") {
        vhqGoMissionControl({ historyMode: "push" });
        document.getElementById("priorities")?.scrollIntoView({ behavior: "smooth", block: "start" });
      } else if (jump === "queue") {
        vhqGoMissionControl({ historyMode: "push" });
        document.getElementById("queue-list")?.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    });
  });
  document.addEventListener("click", (e) => {
    const roomBtn = e.target.closest("[data-vhq-room]");
    if (roomBtn && document.getElementById("vhq-shell")?.contains(roomBtn)) {
      e.preventDefault();
      vhqRenderRoom(roomBtn.getAttribute("data-vhq-room"), { historyMode: "push" });
      return;
    }
    const floorRoom = e.target.closest(".vhq-room[data-room]");
    if (floorRoom && document.getElementById("vhq-building")?.contains(floorRoom)) {
      e.preventDefault();
      vhqRenderRoom(floorRoom.dataset.room, { historyMode: "push" });
    }
  });
  document.getElementById("vhq-teleport")?.addEventListener("change", (e) => {
    if (!e.target.value) return;
    vhqRenderRoom(e.target.value, { historyMode: "push" });
  });
  document.querySelectorAll(".vhq-floor-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      vhqSelectFloor(btn.dataset.floor);
    });
  });
  if (typeof vhqRenderAllManifestSurfaces === "function") {
    vhqRenderAllManifestSurfaces();
  }
  document.querySelectorAll(".console-tech-links [data-view]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const view = btn.getAttribute("data-view");
      if (!view) return;
      vhqRunAction({ type: "view", target: view });
    });
  });
  document.addEventListener("keydown", (e) => {
    if (!vhqOpen && vhqIsPrimary()) {
      // allow Esc only when HQ view is active
      const hq = document.getElementById("view-hq");
      if (!(hq && !hq.hidden)) return;
    } else if (!vhqOpen) {
      return;
    }
    if (e.key === "Escape") {
      e.preventDefault();
      vhqEscLadder();
      return;
    }
    vhqTrapTab(e);
  });
  window.addEventListener("popstate", (e) => {
    if (!vhqIsPrimary()) return;
    const st = (e.state && e.state.vhq) || new URLSearchParams(window.location.search).get("vhq") || "mc";
    vhqApplyUrlState(st, { historyMode: "none" });
  });
}

bindVhqShell();

function vhqColdOpenMissionControl() {
  if (document.body.dataset.vhqW2 !== "1") return;
  const params = new URLSearchParams(window.location.search);
  if (params.get("ticket")) {
    if (vhqIsPrimary()) {
      vhqApplyingHistory = true;
      try {
        showView("home");
        vhqParkPrimaryShell();
      } finally {
        vhqApplyingHistory = false;
      }
      vhqWriteHistory("console", { replace: true });
    }
    return;
  }
  if (!vhqIsPrimary()) {
    try {
      vhqOpenShell("mission-control");
    } catch (err) {
      console.warn("vhq cold-open failed", err);
      vhqRestoreAllSlots();
    }
    return;
  }
  try {
    const raw = params.get("vhq") || "mc";
    vhqApplyUrlState(raw, { historyMode: "replace" });
  } catch (err) {
    console.warn("vhq cold-open failed", err);
    vhqRestoreAllSlots();
  }
}


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
  refresh()
    .then(() => {
      if (vhqOpen || (vhqIsPrimary() && document.getElementById("view-hq") && !document.getElementById("view-hq").hidden)) {
        vhqUpdateSessionBanner();
        vhqGoMissionControl({ historyMode: "push" });
      }
    })
    .catch((e) => toast(e.message));
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
async function vhqBoot() {
  try {
    await bootstrapAuth();
  } finally {
    vhqColdOpenMissionControl();
  }
}
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => {
    vhqBoot();
  });
} else {
  vhqBoot();
}
