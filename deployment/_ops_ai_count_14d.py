"""Read-only OPS-AI window counts from jadzia.db (VPS)."""
import sqlite3

c = sqlite3.connect("/opt/jadzia/data/jadzia.db")
cur = c.cursor()


def cols(table):
    return [r[1] for r in cur.execute(f"PRAGMA table_info({table})")]


print("AUDIT")
for row in cur.execute(
    "SELECT action, actor_role, COUNT(*) FROM commander_audit_log "
    "WHERE ts >= datetime('now','-14 days') GROUP BY 1,2 ORDER BY 3 DESC"
):
    print(row)

print("TICKET_COLS", cols("commander_tickets"))
print(
    "TICKETS_BY_SOURCE",
    cur.execute(
        "SELECT source, COUNT(*) FROM commander_tickets "
        "WHERE created_at >= datetime('now','-14 days') GROUP BY 1"
    ).fetchall(),
)
print(
    "TICKETS_AI",
    cur.execute(
        "SELECT COUNT(*) FROM commander_tickets "
        "WHERE created_at >= datetime('now','-14 days') "
        "AND source IN ('brief_sales_cta','brief_hitl')"
    ).fetchone()[0],
)
print(
    "TICKETS_OTHER",
    cur.execute(
        "SELECT COUNT(*) FROM commander_tickets "
        "WHERE created_at >= datetime('now','-14 days') "
        "AND source NOT IN ('brief_sales_cta','brief_hitl')"
    ).fetchone()[0],
)
print(
    "LEAD_DISP",
    cur.execute(
        "SELECT disposition, COUNT(*) FROM leads "
        "WHERE updated_at >= datetime('now','-14 days') GROUP BY 1"
    ).fetchall(),
)
print(
    "PUBLISH_AUDIT",
    cur.execute(
        "SELECT COUNT(*) FROM commander_audit_log "
        "WHERE ts >= datetime('now','-14 days') AND action='publish'"
    ).fetchone()[0],
)
print(
    "DISP_AUDIT",
    cur.execute(
        "SELECT COUNT(*) FROM commander_audit_log "
        "WHERE ts >= datetime('now','-14 days') AND action='lead_disposition'"
    ).fetchone()[0],
)

wcols = cols("widget_chat_sessions")
print("WIDGET_COLS", wcols)
ts_col = "created_at" if "created_at" in wcols else ("started_at" if "started_at" in wcols else None)
if ts_col:
    print(
        "WIDGET",
        cur.execute(
            f"SELECT COUNT(*) FROM widget_chat_sessions WHERE {ts_col} >= datetime('now','-14 days')"
        ).fetchone()[0],
    )
else:
    print("WIDGET_TOTAL", cur.execute("SELECT COUNT(*) FROM widget_chat_sessions").fetchone()[0])

print(
    "LEADS_CREATED",
    cur.execute(
        "SELECT COUNT(*) FROM leads WHERE created_at >= datetime('now','-14 days')"
    ).fetchone()[0],
)
print(
    "WIDGET_UPDATED_14D",
    cur.execute(
        "SELECT COUNT(*) FROM widget_chat_sessions "
        "WHERE updated_at >= datetime('now','-14 days')"
    ).fetchone()[0],
)
tickets_ai = cur.execute(
    "SELECT COUNT(*) FROM commander_tickets "
    "WHERE created_at >= datetime('now','-14 days') "
    "AND source IN ('brief_sales_cta','brief_hitl')"
).fetchone()[0]
leads_created = cur.execute(
    "SELECT COUNT(*) FROM leads WHERE created_at >= datetime('now','-14 days')"
).fetchone()[0]
publish = cur.execute(
    "SELECT COUNT(*) FROM commander_audit_log "
    "WHERE ts >= datetime('now','-14 days') AND action='publish'"
).fetchone()[0]
leads_closed = cur.execute(
    "SELECT COUNT(*) FROM leads "
    "WHERE updated_at >= datetime('now','-14 days') AND disposition='closed'"
).fetchone()[0]
ai = tickets_ai + leads_created
human = publish + leads_closed
pct = round(100.0 * ai / (ai + human), 1) if (ai + human) else 0.0
print("RATIO_V1_AI", ai, "HUMAN", human, "PCT", pct)
