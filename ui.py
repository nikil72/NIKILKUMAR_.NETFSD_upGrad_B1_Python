"""
ui.py - Rich Terminal UI helpers for Smart IT Service Desk
Pure Python ANSI - no extra libraries needed.
"""

import os
import shutil

# ── ANSI colour codes ──────────────────────────────────────────────────────────
RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"

# Foreground
BLACK   = "\033[30m"
RED     = "\033[31m"
GREEN   = "\033[32m"
YELLOW  = "\033[33m"
BLUE    = "\033[34m"
MAGENTA = "\033[35m"
CYAN    = "\033[36m"
WHITE   = "\033[37m"

# Bright foreground
BRED    = "\033[91m"
BGREEN  = "\033[92m"
BYELLOW = "\033[93m"
BBLUE   = "\033[94m"
BMAGENTA= "\033[95m"
BCYAN   = "\033[96m"
BWHITE  = "\033[97m"

# Background
BG_BLACK   = "\033[40m"
BG_RED     = "\033[41m"
BG_GREEN   = "\033[42m"
BG_YELLOW  = "\033[43m"
BG_BLUE    = "\033[44m"
BG_MAGENTA = "\033[45m"
BG_CYAN    = "\033[46m"
BG_WHITE   = "\033[47m"
BG_BBLUE   = "\033[104m"
BG_BGREEN  = "\033[102m"

# ── Terminal width ─────────────────────────────────────────────────────────────
def tw(fallback: int = 80) -> int:
    return shutil.get_terminal_size((fallback, 24)).columns

def _w(): return min(tw(), 90)

# ── Colour helpers ─────────────────────────────────────────────────────────────
def c(text, *codes): return "".join(codes) + str(text) + RESET
def bold(t): return c(t, BOLD)
def dim(t):  return c(t, DIM)

def priority_color(p: str) -> str:
    return {
        "P1": c(f" {p} ", BOLD, BG_RED,    BWHITE),
        "P2": c(f" {p} ", BOLD, BG_YELLOW, BLACK),
        "P3": c(f" {p} ", BOLD, BG_BLUE,   BWHITE),
        "P4": c(f" {p} ", BOLD, BG_GREEN,  BLACK),
    }.get(p, c(f" {p} ", DIM))

def status_color(s: str) -> str:
    return {
        "Open":        c(s, BGREEN),
        "In Progress": c(s, BYELLOW),
        "Escalated":   c(s, BRED),
        "Resolved":    c(s, CYAN),
        "Closed":      c(s, DIM),
    }.get(s, s)

def ticket_type_icon(t: str) -> str:
    return {
        "Incident":      c("● INC", BOLD, RED),
        "ServiceRequest":c("● SRQ", BOLD, YELLOW),
        "Problem":       c("● PRB", BOLD, BLUE),
        "Change":        c("● CHG", BOLD, GREEN),
    }.get(t, c("● GEN", DIM))

# ── Box drawing ────────────────────────────────────────────────────────────────
def hline(w=None, ch="─"): return ch * (w or _w())

def box_top(title: str = "", w=None, color=CYAN):
    w = w or _w()
    if title:
        pad  = w - len(title) - 4
        left = pad // 2
        right= pad - left
        print(c("╔" + "═"*left + "╡ ", color) + c(title, BOLD, BWHITE) + c(" ╞" + "═"*right + "╗", color))
    else:
        print(c("╔" + "═"*(w-2) + "╗", color))

def box_bot(w=None, color=CYAN):
    w = w or _w()
    print(c("╚" + "═"*(w-2) + "╝", color))

def box_row(text: str, w=None, color=CYAN):
    w = w or _w()
    # strip ANSI for length calc
    import re
    plain = re.sub(r'\033\[[0-9;]*m', '', text)
    pad = max(0, w - 2 - len(plain) - 2)
    print(c("║ ", color) + text + " " * pad + c(" ║", color))

def box_sep(w=None, color=CYAN):
    w = w or _w()
    print(c("╠" + "═"*(w-2) + "╣", color))

def thin_sep(w=None):
    w = w or _w()
    print(c("  " + "─"*(w-4), DIM))

# ── Header / Banner ───────────────────────────────────────────────────────────
def print_banner():
    os.system("cls" if os.name == "nt" else "clear")
    w = _w()
    print()
    box_top("SMART IT SERVICE DESK", w, CYAN)
    box_row(c("  Automated Helpdesk · ITIL Workflows · Real-time Monitoring  ", DIM, CYAN), w, CYAN)
    box_bot(w, CYAN)
    print()

# ── Menu ──────────────────────────────────────────────────────────────────────
def print_menu(title: str, options: list, color=BBLUE):
    """options = list of (key, label) tuples"""
    w = _w()
    box_top(title, w, color)
    box_row("", w, color)
    for key, label in options:
        key_str = c(f" [{key}]", BOLD, BYELLOW)
        box_row(f"  {key_str}  {label}", w, color)
    box_row("", w, color)
    box_bot(w, color)
    return input(c("  ▶  Select: ", BOLD, BCYAN)).strip()

# ── Ticket card ───────────────────────────────────────────────────────────────
def print_ticket_card(t: dict):
    w = _w()
    ttype = t.get("ticket_type", "General")
    prio  = t.get("priority", "P4")
    color = {
        "P1": RED, "P2": YELLOW, "P3": BLUE, "P4": GREEN
    }.get(prio, CYAN)

    box_top(t.get("ticket_id", ""), w, color)
    box_row(f"  {ticket_type_icon(ttype)}   {c(t.get('employee_name',''), BOLD, BWHITE)}  ·  {c(t.get('department',''), DIM)}", w, color)
    box_sep(w, color)
    box_row(f"  {c('Priority :', DIM)}  {priority_color(prio)}   {c('Status :', DIM)}  {status_color(t.get('status',''))}", w, color)
    box_row(f"  {c('Category :', DIM)}  {c(t.get('category',''), BYELLOW)}", w, color)
    box_row(f"  {c('Created  :', DIM)}  {t.get('created_at','')}", w, color)
    if t.get("resolved_at"):
        box_row(f"  {c('Resolved :', DIM)}  {t.get('resolved_at')}", w, color)
    box_sep(w, color)
    desc = t.get("description", "")
    # word-wrap description
    max_len = w - 6
    words = desc.split()
    line = ""
    for word in words:
        if len(line) + len(word) + 1 > max_len:
            box_row(f"  {c(line, WHITE)}", w, color)
            line = word
        else:
            line = (line + " " + word).strip()
    if line:
        box_row(f"  {c(line, WHITE)}", w, color)
    if t.get("sla_breached"):
        box_sep(w, color)
        box_row(f"  {c('⚠  SLA BREACHED', BOLD, BRED)}", w, color)
    box_bot(w, color)
    print()

# ── Stat cards row ────────────────────────────────────────────────────────────
def print_stat_row(stats: list):
    """stats = [(label, value, color), ...]"""
    w    = _w()
    cols = len(stats)
    cw   = (w - cols - 1) // cols

    tops  = ["┌" + "─"*(cw-2) + "┐" for _ in stats]
    bots  = ["└" + "─"*(cw-2) + "┘" for _ in stats]
    mids  = []
    vals  = []
    for label, value, col in stats:
        val_str = str(value)
        lbl_pad = max(0, cw - 2 - len(label))
        val_pad = max(0, cw - 2 - len(val_str))
        mids.append("│" + c(f" {label}" + " "*lbl_pad, DIM) + "│")
        vals.append("│" + c(f" {val_str}" + " "*val_pad, BOLD, col) + "│")

    print("  " + " ".join(tops))
    print("  " + " ".join(mids))
    print("  " + " ".join(vals))
    print("  " + " ".join(bots))
    print()

# ── Horizontal bar chart ──────────────────────────────────────────────────────
def print_bar_chart(title: str, data: list, color=BBLUE, bar_char="█", max_bar=40):
    """data = [(label, value), ...]  sorted descending"""
    if not data:
        return
    w       = _w()
    max_val = max(v for _, v in data) or 1
    label_w = min(max(len(l) for l, _ in data), 25)

    print()
    print(c(f"  {title}", BOLD, BWHITE))
    thin_sep(w)
    for label, value in data:
        bar_len  = int((value / max_val) * max_bar)
        bar      = c(bar_char * bar_len, color)
        lbl      = label[:label_w].ljust(label_w)
        val_str  = c(f" {value}", BOLD, BWHITE)
        print(f"  {c(lbl, DIM)}  {bar}{val_str}")
    print()

# ── Table ─────────────────────────────────────────────────────────────────────
def print_table(headers: list, rows: list, col_colors: list = None):
    """Simple fixed-width table."""
    if not rows:
        print(c("  (no data)", DIM))
        return
    # compute column widths
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            import re
            plain = re.sub(r'\033\[[0-9;]*m', '', str(cell))
            widths[i] = max(widths[i], len(plain))

    def fmtrow(cells, bold_=False, colors=None):
        parts = []
        for i, cell in enumerate(cells):
            import re
            plain = re.sub(r'\033\[[0-9;]*m', '', str(cell))
            pad   = widths[i] - len(plain)
            col   = (colors[i] if colors and i < len(colors) else "")
            txt   = (c(str(cell), BOLD, col) if bold_ else c(str(cell), col)) if col else str(cell)
            parts.append(txt + " " * pad)
        return "  │ " + " │ ".join(parts) + " │"

    sep = "  ├─" + "─┼─".join("─"*w for w in widths) + "─┤"
    top = "  ┌─" + "─┬─".join("─"*w for w in widths) + "─┐"
    bot = "  └─" + "─┴─".join("─"*w for w in widths) + "─┘"

    print(top)
    print(fmtrow(headers, bold_=True, colors=[BCYAN]*len(headers)))
    print(sep)
    for row in rows:
        print(fmtrow(row, colors=col_colors))
    print(bot)
    print()

# ── Success / error / info banners ────────────────────────────────────────────
def success(msg: str): print(f"\n  {c('✔', BOLD, BGREEN)}  {c(msg, BGREEN)}\n")
def error(msg: str):   print(f"\n  {c('✘', BOLD, BRED)}  {c(msg, BRED)}\n")
def info(msg: str):    print(f"\n  {c('ℹ', BOLD, BCYAN)}  {c(msg, BCYAN)}\n")
def warn(msg: str):    print(f"\n  {c('⚠', BOLD, BYELLOW)}  {c(msg, BYELLOW)}\n")

def pause():
    print()
    input(c("  Press ENTER to continue... ", DIM))
    print()

def prompt(msg: str) -> str:
    return input(c(f"  {msg}: ", BCYAN)).strip()
