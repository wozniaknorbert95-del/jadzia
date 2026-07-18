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

function showView(name) {
  document.querySelectorAll(".view").forEach((v) => {
    const active = v.id === `view-${name}`;
    v.hidden = !active;
    v.classList.toggle("active", active);
  });
  document.querySelectorAll(".nav-btn").forEach((b) => {
    b.classList.toggle("active", b.dataset.view === name);
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
  if (item.queue_type !== "hot_lead") return "";
  const leadId = item.payload?.id;
  if (!leadId) return "";
  return `
    <button type="button" data-lead-disp="${leadId}" data-disp="acked">Ack</button>
    <button type="button" data-lead-disp="${leadId}" data-disp="snoozed">Snooze</button>
    <button type="button" data-lead-disp="${leadId}" data-disp="closed">Close</button>
  `;
}

function renderQueue(items) {
  const filtered = items.filter((i) => i.severity !== "INFO");
  const el = document.getElementById("queue-list");
  el.innerHTML = filtered.length
    ? filtered.map((q) => approvalCard(q, leadDispositionActions(q))).join("")
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
        toast(e.message || "Disposition failed");
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
  const [prio, queue, agents, snap, settings] = await Promise.all([
    api("/api/v1/commander/priorities/today"),
    api("/api/v1/commander/queue"),
    api("/api/v1/agents"),
    api("/api/v1/commander/analytics/snapshot").catch(() => null),
    api("/api/v1/commander/settings").catch(() => ({})),
  ]);
  renderPriorities(prio.priorities || []);
  renderQueue(queue.items || []);
  const slaBad = (agents.agents || []).filter((a) => !a.sla_ok).length;
  const fresh = snap?.freshness?.ga4?.status || "—";
  document.getElementById("health-strip").textContent =
    `Agenci SLA breach: ${slaBad} · GA4: ${fresh} · Worker: ${snap?.freshness?.worker?.status || "—"}`;
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
  const [cal, agents, settings, fbHealth] = await Promise.all([
    api("/api/v1/content-calendar"),
    api("/api/v1/agents"),
    api("/api/v1/commander/settings").catch(() => ({})),
    api("/api/v1/commander/marketing/fb-health").catch(() => null),
  ]);

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
      <span class="badge stale-${v.status} ${v.status}">${v.status}</span>
      ${v.staleness_seconds != null ? `<small>${v.staleness_seconds}s temu</small>` : ""}
    </article>`).join("");
  document.getElementById("orders-list").innerHTML =
    (orders.orders || []).slice(0, 10).map((o) =>
      `<div>#${o.order_id} · ${o.status} · €${o.total_gross}</div>`).join("") || "Brak";
  document.getElementById("leads-list").innerHTML =
    (leads.leads || []).slice(0, 10).map((l) =>
      `<div>${l.email} · score ${l.game_score ?? "—"} · ${l.disposition || "open"}
        <button type="button" data-lead-list-disp="${l.id}" data-disp="acked">Ack</button>
        <button type="button" data-lead-list-disp="${l.id}" data-disp="closed">Close</button>
      </div>`).join("") || "Brak";
  document.querySelectorAll("[data-lead-list-disp]").forEach((btn) => {
    btn.onclick = async () => {
      try {
        await api(`/api/v1/commander/leads/${btn.dataset.leadListDisp}/disposition`, {
          method: "POST",
          body: JSON.stringify({ disposition: btn.dataset.disp }),
        });
        loadAnalytics().catch((e) => toast(e.message));
      } catch (e) {
        toast(e.message || "Disposition failed");
      }
    };
  });
}

async function loadAgents() {
  const data = await api("/api/v1/agents");
  document.getElementById("agents-list").innerHTML = (data.agents || []).map((a) => `
    <article class="card">
      <strong>${a.label}</strong>
      <p>Status: ${a.status} · SLA: <span class="badge ${a.sla_ok ? "ok" : "red"}">${a.sla_ok ? "ok" : "breach"}</span></p>
      <p>Held: ${a.held_count || 0}</p>
      <p class="links">
        ${a.agent_id === "design" ? '<a href="/api/v1/design-agent/health" target="_blank" rel="noopener">INSPIRE</a>' : ""}
        ${a.agent_id === "engineering" ? '<a href="https://os.flexgrafik.nl" target="_blank" rel="noopener">Agent OS</a>' : ""}
      </p>
      ${a.status === "LIVE"
        ? `<button type="button" data-pause="${a.agent_id}">Pauza</button>`
        : `<button type="button" data-resume="${a.agent_id}">Wznów</button>`}
    </article>`).join("");

  document.getElementById("phase-c-cards").innerHTML = `
    <article class="card placeholder"><strong>Procurement</strong><p>Phase C</p></article>
    <article class="card placeholder"><strong>Finance</strong><p>Phase C</p></article>
    <article class="card placeholder"><strong>Support</strong><p>Phase C</p></article>
    <article class="card placeholder"><strong>Negotiation</strong><p>Phase C</p></article>`;

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
  const data = await api("/api/v1/commander/audit-log?limit=30");
  document.getElementById("audit-list").innerHTML = (data.entries || []).map((e) =>
    `<div><code>${e.ts}</code> · ${e.action} · ${e.actor_id} (${e.actor_role})</div>`).join("") || "Brak";
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

document.querySelectorAll(".nav-btn").forEach((btn, idx, all) => {
  btn.addEventListener("click", async () => {
    showView(btn.dataset.view);
    try { await refresh(); } catch (e) { toast(e.message); }
  });
  btn.addEventListener("keydown", (e) => {
    if (e.key !== "ArrowRight" && e.key !== "ArrowLeft") return;
    e.preventDefault();
    const i = [...all].indexOf(btn);
    const next = e.key === "ArrowRight" ? all[i + 1] || all[0] : all[i - 1] || all[all.length - 1];
    next.focus();
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

const params = new URLSearchParams(window.location.search);
const ticketParam = params.get("ticket");
const tokenParam = params.get("token");
if (ticketParam && tokenParam) {
  openTicketFromDeeplink(ticketParam, tokenParam);
} else if (ticketParam) {
  showView("home");
  toast(`Ticket #${ticketParam} — zaloguj JWT lub użyj linku z tokenem`);
}

if (getToken()) {
  document.getElementById("jwt-input").value = getToken();
  refresh().catch((e) => toast(e.message));
}
