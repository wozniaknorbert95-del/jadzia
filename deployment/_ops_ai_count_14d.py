"""Read-only OPS-AI window counts from jadzia.db (VPS).

Prints v1 (baseline) and v1.1 (widget created_at + cs_followup tickets).
"""
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
    "TICKETS_AI_V1",
    cur.execute(
        "SELECT COUNT(*) FROM commander_tickets "
        "WHERE created_at >= datetime('now','-14 days') "
        "AND source IN ('brief_sales_cta','brief_hitl')"
    ).fetchone()[0],
)
print(
    "TICKETS_AI_V11",
    cur.execute(
        "SELECT COUNT(*) FROM commander_tickets "
        "WHERE created_at >= datetime('now','-14 days') "
        "AND source IN ('brief_sales_cta','brief_hitl','cs_followup')"
    ).fetchone()[0],
)
print(
    "TICKETS_OTHER",
    cur.execute(
        "SELECT COUNT(*) FROM commander_tickets "
        "WHERE created_at >= datetime('now','-14 days') "
        "AND source NOT IN ('brief_sales_cta','brief_hitl','cs_followup')"
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
has_created = "created_at" in wcols
if has_created:
    print(
        "WIDGET_CREATED_14D",
        cur.execute(
            "SELECT COUNT(*) FROM widget_chat_sessions "
            "WHERE created_at >= datetime('now','-14 days')"
        ).fetchone()[0],
    )
else:
    print("WIDGET_CREATED_14D", "N/A (no created_at — deploy instrumentation)")
print(
    "WIDGET_TOTAL",
    cur.execute("SELECT COUNT(*) FROM widget_chat_sessions").fetchone()[0],
)
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

tickets_ai_v1 = cur.execute(
    "SELECT COUNT(*) FROM commander_tickets "
    "WHERE created_at >= datetime('now','-14 days') "
    "AND source IN ('brief_sales_cta','brief_hitl')"
).fetchone()[0]
tickets_ai_v11 = cur.execute(
    "SELECT COUNT(*) FROM commander_tickets "
    "WHERE created_at >= datetime('now','-14 days') "
    "AND source IN ('brief_sales_cta','brief_hitl','cs_followup')"
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
widget_ai = 0
if has_created:
    widget_ai = cur.execute(
        "SELECT COUNT(*) FROM widget_chat_sessions "
        "WHERE created_at >= datetime('now','-14 days')"
    ).fetchone()[0]

human = publish + leads_closed
ai_v1 = tickets_ai_v1 + leads_created
pct_v1 = round(100.0 * ai_v1 / (ai_v1 + human), 1) if (ai_v1 + human) else 0.0
print("RATIO_V1_AI", ai_v1, "HUMAN", human, "PCT", pct_v1)

ai_v11 = tickets_ai_v11 + leads_created + widget_ai
pct_v11 = round(100.0 * ai_v11 / (ai_v11 + human), 1) if (ai_v11 + human) else 0.0
print(
    "RATIO_V11_AI",
    ai_v11,
    "HUMAN",
    human,
    "PCT",
    pct_v11,
    "WIDGET_AI",
    widget_ai,
    "PASS_GE_60",
    "YES" if pct_v11 >= 60.0 else "NO",
)
if not has_created:
    # Projection: treat updated_at window as created_at after backfill migration
    widget_proj = cur.execute(
        "SELECT COUNT(*) FROM widget_chat_sessions "
        "WHERE updated_at >= datetime('now','-14 days')"
    ).fetchone()[0]
    ai_proj = tickets_ai_v11 + leads_created + widget_proj
    pct_proj = (
        round(100.0 * ai_proj / (ai_proj + human), 1) if (ai_proj + human) else 0.0
    )
    print(
        "RATIO_V11_PROJECTED_AFTER_MIGRATE_AI",
        ai_proj,
        "HUMAN",
        human,
        "PCT",
        pct_proj,
        "WIDGET_PROJ",
        widget_proj,
        "PASS_GE_60",
        "YES" if pct_proj >= 60.0 else "NO",
    )
