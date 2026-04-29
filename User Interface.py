import requests
import tkinter as tk
from tkinter import font as tkfont
import threading
import matplotlib

matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np

# ──────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────
HEADERS = {
    "Accept": "application/json",
    "Host": "oracleapex.com",
    "User-Agent": "Mozilla/5.0 Firefox/149.0"
}
BASE = "https://oracleapex.com/ords/zahraa_individual_assignment/myapi"
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "gemma2:2b"

BG = "#212121"
BG2 = "#1a1a1a"
INPUT_BG = "#2f2f2f"
BORDER = "#3f3f3f"
ACCENT = "#ab68ff"
FG = "#ececec"
MUTED = "#888888"
SEND_BG = "#676767"
SEND_HOV = "#888888"
BTN_HOV = "#3a3a3a"
GREEN = "#4caf50"
ORANGE = "#ff9800"


# ──────────────────────────────────────────────
# DATA FETCHERS (with raw data for charts)
# ──────────────────────────────────────────────

def fetch_average_order_value():
    try:
        res = requests.get(f"{BASE}/average_order_value", headers=HEADERS, timeout=30)
        if res.status_code != 200:
            return "", f"Average Order Value (HTTP {res.status_code})", None
        items = res.json().get("items", [])
        if not items:
            return "", "Average Order Value (empty)", None
        ctx = "Average Order Value per Month (2017):\n"
        chart_data = {"months": [], "values": []}
        for i in items:
            m, v = i.get("month_name"), i.get("avg_order_value")
            if m and v is not None:
                val = float(v)
                ctx += f"  {m}: ${val:,.2f}\n"
                chart_data["months"].append(m)
                chart_data["values"].append(val)
        return ctx, None, chart_data
    except Exception as e:
        return "", f"Average Order Value (error: {e})", None


def fetch_best_product_categories():
    try:
        res = requests.get(f"{BASE}/best_product_categories", headers=HEADERS, timeout=30)
        if res.status_code != 200:
            return "", f"Best Product Categories (HTTP {res.status_code})", None
        items = res.json().get("items", [])
        if not items:
            return "", "Best Product Categories (empty)", None
        ctx = "Best Product Categories by Profit:\n"
        chart_data = {"categories": [], "profits": []}
        for i in items:
            c, p = i.get("category_name"), i.get("total_profit")
            if c and p is not None:
                profit = float(p)
                ctx += f"  {c}: ${profit:,.2f}\n"
                chart_data["categories"].append(c)
                chart_data["profits"].append(profit)
        return ctx, None, chart_data
    except Exception as e:
        return "", f"Best Product Categories (error: {e})", None


def fetch_credit_limit():
    try:
        res = requests.get(f"{BASE}/credit_limit", headers=HEADERS, timeout=30)
        if res.status_code != 200:
            return "", f"Credit Limit (HTTP {res.status_code})", None
        items = res.json().get("items", [])
        if not items:
            return "", "Credit Limit (empty)", None
        ctx = "Customers Exceeding Credit Limit Per Year:\n"
        chart_data = {"years": [], "counts": []}
        for i in items:
            y, c = i.get("order_year"), i.get("customers_exceeding_limit")
            if y and c is not None:
                count = int(c)
                ctx += f"  Year {y}: {count} customers\n"
                chart_data["years"].append(str(y))
                chart_data["counts"].append(count)
        return ctx, None, chart_data
    except Exception as e:
        return "", f"Credit Limit (error: {e})", None


def fetch_orders_per_region():
    try:
        res = requests.get(f"{BASE}/sales_per_region", headers=HEADERS, timeout=30)
        if res.status_code != 200:
            return "", f"Orders per Region (HTTP {res.status_code})", None
        items = res.json().get("items", [])
        if not items:
            return "", "Orders per Region (empty)", None
        ctx = "Sales Profit by Region and Category:\n"
        chart_data = {"regions": {}, "categories": set()}
        for i in items:
            r = i.get("region_name")
            c = i.get("category_name")
            p = i.get("total_profit")
            if r and c and p is not None:
                profit = float(p)
                ctx += f"  {r} - {c}: ${profit:,.2f}\n"
                if r not in chart_data["regions"]:
                    chart_data["regions"][r] = {}
                chart_data["regions"][r][c] = profit
                chart_data["categories"].add(c)
        return ctx, None, chart_data
    except Exception as e:
        return "", f"Orders per Region (error: {e})", None


def fetch_profits_per_employee():
    try:
        res = requests.get(f"{BASE}/profits_per_employee", headers=HEADERS, timeout=30)
        if res.status_code != 200:
            return "", f"Profits per Employee (HTTP {res.status_code})", None
        items = res.json().get("items", [])
        if not items:
            return "", "Profits per Employee (empty)", None
        ctx = "Employee Profit Data:\n"
        chart_data = {"employees": [], "profits": []}
        for i in items:
            name = i.get("employee_name")
            pv = i.get("total_profit")
            if name and pv is not None:
                if isinstance(pv, str):
                    pv = float(pv.strip().replace("$", "").replace(",", ""))
                profit = float(pv)
                ctx += f"  {name}: ${profit:,.2f}\n"
                chart_data["employees"].append(name)
                chart_data["profits"].append(profit)
        return ctx, None, chart_data
    except Exception as e:
        return "", f"Profits per Employee (error: {e})", None


# Chart data storage
CHART_DATA = {}


# ──────────────────────────────────────────────
# CHART GENERATION FUNCTIONS
# ──────────────────────────────────────────────

def create_chart_window(chart_type, data):
    """Create a new window with the requested chart"""
    chart_window = tk.Toplevel()
    chart_window.title(f"Chart: {chart_type}")
    chart_window.geometry("800x600")
    chart_window.configure(bg=BG)

    # Create figure and axes
    fig = Figure(figsize=(10, 6), dpi=100, facecolor='#212121')
    ax = fig.add_subplot(111)
    ax.set_facecolor('#1a1a1a')

    # Style the chart
    ax.tick_params(colors='#ececec')
    ax.xaxis.label.set_color('#ececec')
    ax.yaxis.label.set_color('#ececec')
    ax.title.set_color('#ececec')
    for spine in ax.spines.values():
        spine.set_color('#3f3f3f')

    if chart_type == "Average Order Value":
        if data and "months" in data:
            ax.bar(data["months"], data["values"], color='#ab68ff', alpha=0.8)
            ax.set_title('Average Order Value per Month (2017)', fontsize=14, pad=20)
            ax.set_xlabel('Month', fontsize=12)
            ax.set_ylabel('Order Value ($)', fontsize=12)
            ax.tick_params(axis='x', rotation=45)
            # Add value labels on bars
            for i, v in enumerate(data["values"]):
                ax.text(i, v + 1000, f'${v:,.0f}', ha='center', va='bottom', color='#ececec')

    elif chart_type == "Best Product Categories":
        if data and "categories" in data:
            ax.bar(data["categories"], data["profits"], color='#4caf50', alpha=0.8)
            ax.set_title('Best Product Categories by Profit', fontsize=14, pad=20)
            ax.set_xlabel('Category', fontsize=12)
            ax.set_ylabel('Profit ($)', fontsize=12)
            ax.tick_params(axis='x', rotation=45)
            for i, v in enumerate(data["profits"]):
                ax.text(i, v + 500, f'${v:,.0f}', ha='center', va='bottom', color='#ececec')

    elif chart_type == "Credit Limit":
        if data and "years" in data:
            ax.plot(data["years"], data["counts"], marker='o', linewidth=2,
                    markersize=8, color='#ff9800')
            ax.fill_between(data["years"], data["counts"], alpha=0.3, color='#ff9800')
            ax.set_title('Customers Exceeding Credit Limit Per Year', fontsize=14, pad=20)
            ax.set_xlabel('Year', fontsize=12)
            ax.set_ylabel('Number of Customers', fontsize=12)
            for i, v in enumerate(data["counts"]):
                ax.text(data["years"][i], v + 2, str(v), ha='center', va='bottom', color='#ececec')

    elif chart_type == "Orders per Region":
        if data and "regions" in data:
            regions = list(data["regions"].keys())
            categories = sorted(list(data["categories"]))

            # Prepare data for grouped bar chart
            x = np.arange(len(regions))
            width = 0.8 / len(categories) if categories else 0.8

            colors = ['#ab68ff', '#4caf50', '#ff9800', '#2196f3', '#f44336']
            for idx, category in enumerate(categories):
                values = []
                for region in regions:
                    val = data["regions"][region].get(category, 0)
                    values.append(val)
                offset = (idx - len(categories) / 2) * width
                ax.bar(x + offset, values, width, label=category, color=colors[idx % len(colors)], alpha=0.8)

            ax.set_title('Sales Profit by Region and Category', fontsize=14, pad=20)
            ax.set_xlabel('Region', fontsize=12)
            ax.set_ylabel('Profit ($)', fontsize=12)
            ax.set_xticks(x)
            ax.set_xticklabels(regions)
            ax.legend(facecolor='#1a1a1a', labelcolor='#ececec', edgecolor='#3f3f3f')

    elif chart_type == "Profits per Employee":
        if data and "employees" in data:
            # Show top 10 employees if there are many
            employees = data["employees"][:10]
            profits = data["profits"][:10]
            ax.barh(employees, profits, color='#2196f3', alpha=0.8)
            ax.set_title('Top Employee Profits', fontsize=14, pad=20)
            ax.set_xlabel('Profit ($)', fontsize=12)
            ax.set_ylabel('Employee', fontsize=12)
            for i, v in enumerate(profits):
                ax.text(v + 100, i, f'${v:,.0f}', va='center', color='#ececec')

    fig.tight_layout()

    # Embed chart in tkinter window
    canvas = FigureCanvasTkAgg(fig, master=chart_window)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Add close button
    close_btn = tk.Button(chart_window, text="Close", command=chart_window.destroy,
                          bg=SEND_BG, fg=FG, font=("Segoe UI", 10),
                          relief=tk.FLAT, cursor="hand2")
    close_btn.pack(pady=10)


# ──────────────────────────────────────────────
# LLM (receives full conversation history)
# ──────────────────────────────────────────────
def query_ollama(dataset_context: str, history: list, question: str) -> str:
    try:
        if not dataset_context.strip():
            return "No data was loaded. Please check your connection and restart."

        history_text = ""
        for role, text in history:
            label = "User" if role == "user" else "Assistant"
            history_text += f"{label}: {text}\n"

        prompt = (
                "You are a helpful data analyst assistant with access to real business data.\n\n"
                f"=== DATASET ===\n{dataset_context}\n\n"
                + (f"=== CONVERSATION SO FAR ===\n{history_text}\n" if history_text else "")
                + f"=== NEW QUESTION ===\n{question}\n\n"
                  "Instructions:\n"
                  "- Answer using the dataset with specific numbers, names, and figures.\n"
                  "- Use the conversation history to understand follow-up questions and "
                  "references like 'that', 'the previous', 'compare it', 'which was higher'.\n"
                  "- If asked for best/top/highest, identify it from the data.\n"
                  "- If asked for a summary, cover all relevant sections.\n"
                  "- Only decline if the question is entirely unrelated to business data.\n\n"
                  "Answer:"
        )

        response = requests.post(
            OLLAMA_URL,
            json={"model": MODEL, "prompt": prompt, "stream": False},
            timeout=180,
        )
        if response.status_code != 200:
            return f"Error {response.status_code}: {response.text}"
        return response.json().get("response", "No response")
    except Exception as e:
        return f"Error: {e}"


# ──────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────
def rounded_rect(cv, x1, y1, x2, y2, r, **kw):
    pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
           x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
           x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
    return cv.create_polygon(pts, smooth=True, **kw)


# ──────────────────────────────────────────────
# CHAT BUBBLE
# ──────────────────────────────────────────────
class ChatBubble(tk.Frame):
    def __init__(self, parent, message: str, role: str, **kw):
        super().__init__(parent, bg=BG, **kw)
        is_user = role == "user"
        bubble_bg = INPUT_BG if is_user else BG
        anchor = tk.E if is_user else tk.W
        pad = (80, 12) if is_user else (12, 80)

        tk.Label(
            self,
            text="You" if is_user else "✦ Assistant",
            bg=BG, fg=MUTED,
            font=("Segoe UI", 8, "bold"),
            anchor="e" if is_user else "w",
        ).pack(fill=tk.X, padx=pad, pady=(6, 2))

        bubble = tk.Frame(self, bg=bubble_bg, padx=14, pady=10)
        bubble.pack(anchor=anchor, padx=pad, pady=(0, 6))

        txt = tk.Text(
            bubble,
            bg=bubble_bg, fg=FG,
            font=("Segoe UI", 10),
            relief=tk.FLAT, bd=0,
            wrap=tk.WORD,
            cursor="arrow",
            state=tk.NORMAL,
            width=55,
            height=1,
        )
        txt.insert("1.0", message)
        txt.config(state=tk.DISABLED)
        txt.config(height=max(1, int(txt.index(tk.END).split(".")[0]) - 1))
        txt.pack()


# ──────────────────────────────────────────────
# LOADING SPLASH
# ──────────────────────────────────────────────
def show_loading_window(on_done_callback):
    splash = tk.Tk()
    splash.title("Data Analyst Assistant")
    splash.geometry("460x340")
    splash.resizable(False, False)
    splash.configure(bg=BG)

    splash.update_idletasks()
    sw, sh = splash.winfo_screenwidth(), splash.winfo_screenheight()
    splash.geometry(f"460x340+{(sw - 460) // 2}+{(sh - 340) // 2}")

    def F(size, weight="normal"):
        return tkfont.Font(family="Segoe UI", size=size, weight=weight)

    tk.Label(splash, text="Data Analyst Assistant",
             bg=BG, fg=FG, font=F(16, "bold")).pack(pady=(32, 4))
    tk.Label(splash, text="Loading reports, please wait…",
             bg=BG, fg=MUTED, font=F(10)).pack(pady=(0, 24))

    rows_frame = tk.Frame(splash, bg=BG)
    rows_frame.pack(fill=tk.X, padx=60)

    icon_vars = {}
    label_lbls = {}

    for label, _ in FETCHERS:
        row = tk.Frame(rows_frame, bg=BG)
        row.pack(fill=tk.X, pady=4)
        iv = tk.StringVar(value="◌")
        icon_lbl = tk.Label(row, textvariable=iv, bg=BG, fg=MUTED,
                            font=F(11), width=2, anchor="w")
        icon_lbl.pack(side=tk.LEFT)
        txt_lbl = tk.Label(row, text=label, bg=BG, fg=MUTED,
                           font=F(10), anchor="w")
        txt_lbl.pack(side=tk.LEFT)
        icon_vars[label] = iv
        label_lbls[label] = (icon_lbl, txt_lbl)

    status_var = tk.StringVar(value="")
    tk.Label(splash, textvariable=status_var,
             bg=BG, fg=MUTED, font=F(9)).pack(pady=(20, 0))

    spinner_frames = ["◐", "◓", "◑", "◒"]
    spinner_idx = [0]
    spinner_job = [None]

    def spin():
        spinner_idx[0] = (spinner_idx[0] + 1) % len(spinner_frames)
        for lbl, iv in icon_vars.items():
            if iv.get() not in ("✓", "✗"):
                iv.set(spinner_frames[spinner_idx[0]])
        spinner_job[0] = splash.after(120, spin)

    def stop_spinner():
        if spinner_job[0]:
            splash.after_cancel(spinner_job[0])
            spinner_job[0] = None

    completed = [0]
    results = [None] * len(FETCHERS)

    def on_fetch_done(idx, label, ctx, err, chart_data):
        results[idx] = (label, ctx, err, chart_data)
        icon_lbl, txt_lbl = label_lbls[label]
        if err is None:
            icon_vars[label].set("✓")
            icon_lbl.config(fg=GREEN)
            txt_lbl.config(fg=GREEN)
        else:
            icon_vars[label].set("✗")
            icon_lbl.config(fg=ORANGE)
            txt_lbl.config(fg=ORANGE)
        completed[0] += 1
        status_var.set(f"{completed[0]} / {len(FETCHERS)} complete")
        if completed[0] == len(FETCHERS):
            stop_spinner()
            splash.after(500, finish)

    def finish():
        context = ""
        loaded, failed = [], []
        for label, ctx, err, chart_data in results:
            if err:
                failed.append(err)
            else:
                context += f"\n=== {label} ===\n{ctx}"
                loaded.append(label)
                CHART_DATA[label] = chart_data
        splash.destroy()
        on_done_callback(context or "No data could be loaded.", loaded, failed)

    def fetch_one(idx, label, fn):
        ctx, err, chart_data = fn()
        splash.after(0, lambda: on_fetch_done(idx, label, ctx, err, chart_data))

    spin()
    for i, (label, fn) in enumerate(FETCHERS):
        threading.Thread(target=fetch_one, args=(i, label, fn), daemon=True).start()

    splash.mainloop()


# ──────────────────────────────────────────────
# MAIN CHAT UI
# ──────────────────────────────────────────────
def create_ui(context: str, loaded=None, failed=None):
    loaded = loaded or []
    failed = failed or []

    root = tk.Tk()
    root.title("Data Analyst Assistant")
    root.geometry("820x680")
    root.minsize(600, 500)
    root.configure(bg=BG)

    def F(size, weight="normal", slant="roman"):
        return tkfont.Font(family="Segoe UI", size=size, weight=weight, slant=slant)

    busy = [False]
    history = []  # ("user"|"assistant", text) pairs
    welcome_ref = [None]  # mutable ref so go_home can replace the frame

    # chip data with chart display functions
    def show_avg_order_chart():
        if "Average Order Value" in CHART_DATA and CHART_DATA["Average Order Value"]:
            create_chart_window("Average Order Value", CHART_DATA["Average Order Value"])
        else:
            print("No chart data available")

    def show_best_categories_chart():
        if "Best Product Categories" in CHART_DATA and CHART_DATA["Best Product Categories"]:
            create_chart_window("Best Product Categories", CHART_DATA["Best Product Categories"])

    def show_credit_limit_chart():
        if "Credit Limit" in CHART_DATA and CHART_DATA["Credit Limit"]:
            create_chart_window("Credit Limit", CHART_DATA["Credit Limit"])

    def show_regions_chart():
        if "Orders per Region" in CHART_DATA and CHART_DATA["Orders per Region"]:
            create_chart_window("Orders per Region", CHART_DATA["Orders per Region"])

    def show_profits_chart():
        if "Profits per Employee" in CHART_DATA and CHART_DATA["Profits per Employee"]:
            create_chart_window("Profits per Employee", CHART_DATA["Profits per Employee"])

    chip_data = [
        ("📊", "Average Order Value", show_avg_order_chart),
        ("🏷️", "Product Categories", show_best_categories_chart),
        ("💳", "Credit Limit", show_credit_limit_chart),
        ("🌍", "Orders per Region", show_regions_chart),
        ("💰", "Profit per Employee", show_profits_chart),
    ]

    # ── TOP BAR ──────────────────────────────
    topbar = tk.Frame(root, bg=BG, height=48)
    topbar.pack(fill=tk.X, padx=20, pady=(12, 0))
    topbar.pack_propagate(False)

    # Back button — hidden until first message is sent
    back_btn = tk.Button(
        topbar, text="← Back",
        bg=BG, fg=MUTED,
        font=F(10), relief=tk.FLAT,
        cursor="hand2", bd=0,
        activebackground=BG, activeforeground=FG,
        padx=0, pady=0,
    )
    # Not packed yet — appears after first send

    tk.Label(topbar, text="Data Analyst  ˅", bg=BG, fg=FG,
             font=F(22)).pack(side=tk.LEFT, pady=8)

    pill = tk.Canvas(topbar, bg=BG, highlightthickness=0, width=110, height=32)
    pill.pack(side=tk.RIGHT, pady=8)
    rounded_rect(pill, 0, 2, 110, 30, 14, fill=ACCENT, outline="")
    pill.create_text(55, 16, text="🎁  Reports", fill="white", font=F(9, "bold"))

    # ── STATUS BAR ───────────────────────────
    sf = tk.Frame(root, bg=BG2)
    sf.pack(fill=tk.X, padx=20, pady=(0, 4))
    msg = f"✓ {len(loaded)} report(s) loaded"
    color = GREEN
    if failed:
        msg += f"   ⚠ {len(failed)} failed: {', '.join(f.split('(')[0].strip() for f in failed)}"
        color = ORANGE
    tk.Label(sf, text=msg, bg=BG2, fg=color, font=F(8)).pack(anchor="w", pady=3)

    # ── CHAT CANVAS ──────────────────────────
    chat_outer = tk.Frame(root, bg=BG)
    chat_outer.pack(fill=tk.BOTH, expand=True)

    sb = tk.Scrollbar(chat_outer, bg=BG, troughcolor=BG,
                      activebackground=BORDER, bd=0, width=8)
    sb.pack(side=tk.RIGHT, fill=tk.Y)

    canvas = tk.Canvas(chat_outer, bg=BG, bd=0,
                       highlightthickness=0, yscrollcommand=sb.set)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    sb.config(command=canvas.yview)

    chat_frame = tk.Frame(canvas, bg=BG)
    win_id = canvas.create_window((0, 0), window=chat_frame, anchor="nw")

    def _sync_scroll(e=None):
        canvas.configure(scrollregion=canvas.bbox("all"))

    def _sync_width(e):
        canvas.itemconfig(win_id, width=e.width)

    chat_frame.bind("<Configure>", _sync_scroll)
    canvas.bind("<Configure>", _sync_width)

    def scroll_bottom():
        root.after(30, lambda: (canvas.update_idletasks(), canvas.yview_moveto(1.0)))

    # ── WELCOME BUILDER ───────────────────────
    def build_welcome():
        w = tk.Frame(chat_frame, bg=BG)
        w.pack(expand=True, pady=60)
        tk.Label(w, text="What's on the agenda today?",
                 bg=BG, fg=FG, font=F(20)).pack()
        cr = tk.Frame(w, bg=BG)
        cr.pack(pady=24)
        for icon, label, chart_func in chip_data:
            b = tk.Button(
                cr, text=f"{icon}  {label}",
                bg=INPUT_BG, fg=FG, font=F(9),
                relief=tk.FLAT, cursor="hand2",
                padx=12, pady=7, bd=1,
                highlightbackground=BORDER, highlightthickness=1,
                command=chart_func,
            )
            b.pack(side=tk.LEFT, padx=6)
            b.bind("<Enter>", lambda e, w=b: w.config(bg=BTN_HOV))
            b.bind("<Leave>", lambda e, w=b: w.config(bg=INPUT_BG))
        welcome_ref[0] = w

    build_welcome()

    # ── INPUT BAR ────────────────────────────
    bottom = tk.Frame(root, bg=BG)
    bottom.pack(fill=tk.X, padx=20, pady=(8, 16))

    input_box = tk.Frame(bottom, bg=INPUT_BG,
                         highlightbackground=BORDER, highlightthickness=1)
    input_box.pack(fill=tk.X)

    tk.Label(input_box, text="＋", bg=INPUT_BG, fg=MUTED,
             font=F(14), cursor="hand2", padx=10).pack(side=tk.LEFT, padx=(6, 0), pady=10)

    entry_var = tk.StringVar()
    entry = tk.Entry(input_box, textvariable=entry_var,
                     bg=INPUT_BG, fg=FG, insertbackground=FG,
                     font=F(10), relief=tk.FLAT, bd=0)
    entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=10, padx=6)

    tk.Label(input_box, text="🎤", bg=INPUT_BG,
             font=F(12), cursor="hand2", padx=6).pack(side=tk.LEFT, pady=10)

    send_cv = tk.Canvas(input_box, width=34, height=34,
                        bg=INPUT_BG, highlightthickness=0, cursor="hand2")
    send_cv.pack(side=tk.RIGHT, padx=(4, 8), pady=8)
    circ = send_cv.create_oval(2, 2, 32, 32, fill=SEND_BG, outline="")
    arrow = send_cv.create_text(17, 17, text="↑", fill="white", font=F(12, "bold"))

    tk.Label(bottom,
             text="Assistant can make mistakes. Verify important data.",
             bg=BG, fg=MUTED, font=F(8)).pack(pady=(4, 0))

    # ── THINKING INDICATOR ───────────────────
    think_var = tk.StringVar()
    tk.Label(root, textvariable=think_var, bg=BG, fg=MUTED,
             font=F(9, slant="italic")).pack(pady=(0, 4))

    _dots = ["", ".", "..", "..."]
    _di = [0]
    _job = [None]

    def start_thinking():
        stop_thinking()
        _di[0] = 0
        think_var.set("Assistant is thinking")
        _job[0] = root.after(400, _tick)

    def _tick():
        _di[0] = (_di[0] + 1) % len(_dots)
        think_var.set(f"Assistant is thinking{_dots[_di[0]]}")
        _job[0] = root.after(400, _tick)

    def stop_thinking():
        if _job[0] is not None:
            root.after_cancel(_job[0])
            _job[0] = None
        think_var.set("")

    # ── BACK BUTTON LOGIC ────────────────────
    def _show_back():
        """Reveal back button the first time a bubble is added."""
        if not back_btn.winfo_ismapped():
            back_btn.pack(in_=topbar, side=tk.LEFT, padx=(0, 14), pady=10)

    def go_home():
        """Wipe chat, reset history, restore welcome screen."""
        if busy[0]:
            return
        stop_thinking()

        # Destroy all bubble widgets
        for widget in chat_frame.winfo_children():
            widget.destroy()

        # Reset state
        history.clear()
        entry_var.set("")
        _set_busy(False)

        # Rebuild welcome and hide back button
        build_welcome()
        back_btn.pack_forget()

        root.after(10, _sync_scroll)
        entry.focus()

    back_btn.config(command=go_home)
    back_btn.bind("<Enter>", lambda e: back_btn.config(fg=FG))
    back_btn.bind("<Leave>", lambda e: back_btn.config(fg=MUTED))

    # ── SEND LOGIC ───────────────────────────
    def _hide_welcome():
        w = welcome_ref[0]
        if w and w.winfo_exists() and w.winfo_ismapped():
            w.pack_forget()
            root.after(10, _sync_scroll)

    def add_bubble(role, text):
        _hide_welcome()
        _show_back()
        ChatBubble(chat_frame, text, role).pack(fill=tk.X, pady=2)
        scroll_bottom()

    def _set_busy(state: bool):
        busy[0] = state
        entry.config(state=tk.DISABLED if state else tk.NORMAL)
        send_cv.itemconfig(circ, fill=MUTED if state else SEND_BG)

    def chip_click(label):
        if busy[0]:
            return
        entry_var.set(f"Show me the {label}")
        send_message()

    def send_message(event=None):
        if busy[0]:
            return
        msg = entry_var.get().strip()
        if not msg:
            return

        entry_var.set("")
        _set_busy(True)
        add_bubble("user", msg)
        start_thinking()

        history_snapshot = list(history)

        def worker():
            reply = query_ollama(context, history_snapshot, msg)
            root.after(0, lambda: _on_reply(msg, reply))

        def _on_reply(user_msg, reply):
            stop_thinking()
            history.append(("user", user_msg))
            history.append(("assistant", reply))
            add_bubble("assistant", reply)
            _set_busy(False)
            entry.focus()

        threading.Thread(target=worker, daemon=True).start()

    entry.bind("<Return>", send_message)
    for tag in (circ, arrow):
        send_cv.tag_bind(tag, "<Button-1>", lambda e: send_message())
    send_cv.bind("<Enter>", lambda e: send_cv.itemconfig(circ, fill=SEND_HOV) if not busy[0] else None)
    send_cv.bind("<Leave>", lambda e: send_cv.itemconfig(circ, fill=SEND_BG) if not busy[0] else None)

    entry.focus()
    root.mainloop()


# ──────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────
FETCHERS = [
    ("Average Order Value", fetch_average_order_value),
    ("Best Product Categories", fetch_best_product_categories),
    ("Credit Limit", fetch_credit_limit),
    ("Orders per Region", fetch_orders_per_region),
    ("Profits per Employee", fetch_profits_per_employee),
]

if __name__ == "__main__":
    show_loading_window(create_ui)
