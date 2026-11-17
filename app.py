"""
CareerLens - Resume-based employability check + skill-gap coach (Streamlit).

Run:  streamlit run app.py
Needs (same folder): employability_core.py, skill_gap.py, skills_registry.py,
                     model.joblib, preprocessor.joblib   (dataset.csv optional)
"""
import html
import os
import tempfile

import altair as alt
import pandas as pd

import streamlit as st
import sys
import importlib.util

print("========== DEPLOYMENT DIAGNOSTICS ==========")
print("Python version:", sys.version)
print("Joblib location:", importlib.util.find_spec("joblib"))

try:
    import joblib
    print("Joblib version:", joblib.__version__)
    print("JOBLIB IMPORT SUCCESSFUL")
except Exception as e:
    print("JOBLIB IMPORT FAILED:", repr(e))

print("============================================")

import employability_core as ec

import skill_gap as sg
import role_extensions  # adds Civil / Mechanical / Production / Electrical / ECE / Aerospace roles
from skills_registry import SKILLS, MODEL_TECH_SKILL_KEYS, display_name

BASE = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE, "model.joblib")
PREPROC_PATH = os.path.join(BASE, "preprocessor.joblib")
DATA_PATH = os.path.join(BASE, "dataset.csv")

st.set_page_config(page_title="CareerLens", page_icon="🎯", layout="wide")

# ------------------------------------------------------------------ styling
st.markdown("""
<style>
.hero{padding:1.5rem 1.8rem;border-radius:18px;margin-bottom:1.2rem;color:#fff;
      background:linear-gradient(120deg,#264653 0%,#2a9d8f 100%);}
.hero .t{font-size:2rem;font-weight:800;line-height:1.1}
.hero .s{margin-top:.4rem;font-size:1.02rem;opacity:.92}
.card{border:1px solid rgba(128,128,128,.28);border-radius:16px;padding:1.1rem 1.3rem;
      background:rgba(128,128,128,.06);height:100%}
.score{font-size:3.4rem;font-weight:800;line-height:1}
.lvl{font-size:1.15rem;font-weight:700;margin-top:.2rem}
.bar{height:12px;border-radius:8px;background:rgba(128,128,128,.25);overflow:hidden;margin-top:.8rem}
.bar>div{height:100%;border-radius:8px}
.small{font-size:.88rem;opacity:.8}
.chip{display:inline-block;padding:3px 12px;margin:3px 5px 3px 0;border-radius:999px;font-size:.88rem}
.chip.ok{background:rgba(42,157,143,.18);border:1px solid #2a9d8f}
.chip.gap{background:rgba(231,111,81,.14);border:1px solid #e76f51}
.chip.neu{background:rgba(128,128,128,.14);border:1px solid rgba(128,128,128,.5)}
.good{border-left:5px solid #2a9d8f;padding:.5rem .9rem;margin:.35rem 0;border-radius:6px;background:rgba(42,157,143,.08)}
.bad{border-left:5px solid #e76f51;padding:.5rem .9rem;margin:.35rem 0;border-radius:6px;background:rgba(231,111,81,.08)}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero"><div class="t">🎯 CareerLens</div>
<div class="s">Upload your resume, pick your dream role, and get your employability score,
a plain-English explanation, and a personalised plan to close your skill gaps.</div></div>
""", unsafe_allow_html=True)


# ------------------------------------------------------------------ loading
@st.cache_resource(show_spinner="Getting things ready...")
def load_all():
    m, p = ec.load_artifacts(MODEL_PATH, PREPROC_PATH)
    d = None
    if os.path.exists(DATA_PATH):
        try:
            d = pd.read_csv(DATA_PATH)
            if not all(c in d.columns for c in p.feature_names_in_):
                d = None
        except Exception:
            d = None
    return m, p, d


try:
    model, pre, df = load_all()
except Exception as e:  # admin-facing detail goes to the console only
    print("Startup error:", e)
    st.error("The app could not start. Please contact the administrator.")
    st.stop()

raw_cols = list(pre.feature_names_in_)
cats, handle = ec.categorical_info(pre)

# ------------------------------------------------------------------ labels
FIELD_LABELS = {
    "Education_Level": "Education level", "UG_Degree": "UG degree", "PG_Specialization": "PG specialization",
    "Branch": "Branch / discipline", "Year": "Year of study", "CGPA": "CGPA", "Backlogs": "Active backlogs",
    "Project_Count": "Number of projects", "Relevant_Project_Count": "Projects relevant to your target role",
    "Internship": "Internship experience", "Internship_Duration_Months": "Internship duration (months)",
    "Hackathon_Participation": "Hackathon participation", "Certification_Count": "Number of certifications",
    "Relevant_Certification_Count": "Role-relevant certifications", "Open_Source_Contribution": "Open-source contributions",
    "Attendance_Percentage": "Attendance %", "Core_Subject_Score": "Core subject score",
    "Technical_Subject_Score": "Technical subject score", "Aptitude_Score": "Aptitude score",
    "PG_Required_For_Target_Role": "Target role needs a PG degree", "Relevant_Degree_Required": "Target role needs a relevant degree",
}
BINARY_FIELDS = {"Internship", "Hackathon_Participation", "Open_Source_Contribution",
                 "PG_Required_For_Target_Role", "Relevant_Degree_Required"}


def flabel(c):
    if c in SKILLS:
        return display_name(c)
    return FIELD_LABELS.get(c, c.replace("_", " "))


def fmt_value(feat, v):
    if feat in MODEL_TECH_SKILL_KEYS:
        return "Listed" if v == 1 else "Not listed"
    if feat in BINARY_FIELDS:
        return "Yes" if v == 1 else "No"
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return f"{v:g}"
    return str(v)


def describe(row):
    f, v, name = row.feature, row.student_value, flabel(row.feature)
    if f in MODEL_TECH_SKILL_KEYS:
        return f"**{name}** is on your profile" if v == 1 else f"**{name}** is not on your profile yet"
    return f"**{name}**: {fmt_value(f, v)}"


def strength(x, mx):
    r = abs(x) / mx if mx else 0
    return "Major" if r >= 0.6 else "Moderate" if r >= 0.3 else "Minor"


def level_of(p):
    if p >= 0.75:
        return "Strong profile", "#2a9d8f", "You are well positioned. Keep building projects and practise interviews."
    if p >= 0.5:
        return "Promising profile", "#8ab17d", "You have a good base. A few focused improvements can make a real difference."
    if p >= 0.3:
        return "Developing profile", "#e9a23b", "You are on your way. Closing the key gaps below will move the needle."
    return "Early stage", "#e76f51", "Everyone starts somewhere. Follow the plan below step by step."


# ------------------------------------------------------------------ helpers
def ynu(label, key, optional=False, default=None):
    opts = ["Yes", "No"] + (["(not provided)"] if optional else [])
    idx = opts.index(default) if default in opts else (len(opts) - 1 if optional else 0)
    v = st.selectbox(label, opts, index=idx, key=key)
    return None if v == "(not provided)" else (1 if v == "Yes" else 0)


def opt_number(label, key):
    s = st.text_input(f"{label} (optional)", key=key, placeholder="leave blank if unsure").strip()
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        st.warning(f"{label}: '{s}' is not a number, so it was left out.")
        return None


def pick_index(options, guess):
    if not guess:
        return 0
    g = str(guess).lower()
    for i, o in enumerate(options):
        if str(o).lower() == g:
            return i
    for i, o in enumerate(options):
        if g in str(o).lower():
            return i
    return 0


def chips(rows):
    out = []
    for r in rows.itertuples():
        cls, icon = ("ok", "✓") if r.status == "Have" else ("gap", "＋")
        out.append(f'<span class="chip {cls}">{icon} {html.escape(r.requirement)}</span>')
    return "".join(out) or '<span class="small">None listed for this role.</span>'


def impact_chart(d):
    order = list(d["label"])
    return (alt.Chart(d).mark_bar(cornerRadiusEnd=5)
            .encode(x=alt.X("impact:Q", title="← Holding you back          Helping you →",
                            axis=alt.Axis(labels=False, ticks=False), scale=alt.Scale(domain=[-105, 105])),
                    y=alt.Y("label:N", sort=order, title=None, axis=alt.Axis(labelLimit=320)),
                    color=alt.condition(alt.datum.impact > 0, alt.value("#2a9d8f"), alt.value("#e76f51")),
                    tooltip=[alt.Tooltip("label:N", title="Factor"), alt.Tooltip("effect:N", title="Effect")])
            .properties(height=max(120, 30 * len(d) + 30)))


def gain_chart(d):
    return (alt.Chart(d).mark_bar(cornerRadiusEnd=5, color="#2a9d8f")
            .encode(x=alt.X("gain:Q", title="Estimated score gain (percentage points)"),
                    y=alt.Y("skill:N", sort="-x", title=None),
                    tooltip=[alt.Tooltip("skill:N", title="Skill"), alt.Tooltip("gain:Q", title="Gain (pts)", format="+.1f")])
            .properties(height=max(120, 32 * len(d) + 30)))


def plain(s):
    return s.replace("**", "")


def build_report(role_name, score, lvl, helping, hurting, res, gains):
    g, r = res["gap"], res["recs"]
    L = [f"# CareerLens report: {role_name}", "",
         f"**Employability score:** {score:.0f}% ({lvl})", "",
         "## What is helping you"] + [f"- {plain(x)}" for x in helping] + \
        ["", "## What is holding you back"] + [f"- {plain(x)}" for x in hurting] + \
        ["", f"## Role readiness: {g['score']:.0f}/100",
         f"Core skills covered: {g['core_pct'] or 0}%  |  Preferred skills covered: {g['preferred_pct'] or 0}%", "",
         g["label"], "", "## Skill gaps"]
    for title, d in (("Core", g["missing_core"]), ("Preferred", g["missing_preferred"])):
        L.append(f"- **{title}:** " + (", ".join(d["requirement"]) if len(d) else "none"))
    L += ["", "## Learning plan"]
    for row in r["learning_plan"].itertuples():
        L.append(f"- **{row.phase}: {row.skill}** (~{row.est_weeks} weeks) - {row.how}")
    if r["projects"]:
        L += ["", "## Projects to build"] + [f"- {p['title']}" for p in r["projects"]]
    if r["certifications"]:
        L += ["", "## Certifications to consider"] + [f"- {c}" for c in r["certifications"]]
    L += ["", "## Profile improvements"] + [f"- {x}" for x in r["profile"]]
    L += ["", "## Resume tips"] + [f"- {x}" for x in r["resume"]]
    if r["interview_topics"]:
        L += ["", "## Interview topics"] + [f"- {x}" for x in r["interview_topics"]]
    if gains is not None and len(gains):
        L += ["", "## Quickest score boosters"] + [f"- {row.skill}: about {row.gain:+.1f} points" for row in gains.itertuples()]
    return "\n".join(L)


# ------------------------------------------------------------------ sidebar
with st.sidebar:
    st.markdown("### How it works")
    st.markdown("1. **Upload** your resume\n2. **Choose** your target role\n3. **Confirm** the details we found\n"
                "4. **Get** your score, explanation and action plan")
    st.caption("🔒 Your resume is processed in memory only and is never stored.")

# ------------------------------------------------------------------ step 1
st.markdown("#### Step 1 · Your resume and target role")
if "_family_guess" in st.session_state:  # set after a resume is read; applied before the widget is created
    st.session_state["family"] = st.session_state.pop("_family_guess")
left, right = st.columns(2)
resume = left.file_uploader("Upload your resume (PDF or DOCX)", type=["pdf", "docx"])
with right:
    family = st.selectbox("Your field of engineering", role_extensions.family_names(), key="family")
    role = st.selectbox("Target job role", role_extensions.roles_in(family), key=f"role_{family}")

just_loaded = False
if resume is not None and st.session_state.get("resume_name") != resume.name:
    suffix = os.path.splitext(resume.name)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as f:
        f.write(resume.getvalue())
        tmp = f.name
    try:
        with st.spinner("Reading your resume..."):
            st.session_state.ex = ec.extract_resume(path=tmp, filename=resume.name)
            st.session_state.resume_text = ec.extract_text(tmp)
        st.session_state.resume_name = resume.name
        st.session_state.pop("result", None)
        fam = role_extensions.guess_family(st.session_state.ex, st.session_state.resume_text)
        if fam:
            st.session_state["_family_guess"] = fam
        just_loaded = True
    except Exception as e:
        st.error(f"We could not read this resume: {e}")
        st.stop()
    finally:
        os.unlink(tmp)
    if just_loaded:
        st.rerun()

if "ex" not in st.session_state:
    st.info("👆 Upload your resume to begin.")
    st.stop()

ex = st.session_state.ex
resume_text = st.session_state.resume_text
rid = st.session_state.resume_name
K = lambda n: f"{n}_{rid}"

n_sk = len(ex["technical_skills"])
st.success(f"Resume read successfully. We spotted **{n_sk} skill{'s' if n_sk != 1 else ''}**.")
with st.expander("See what we found in your resume"):
    st.markdown("".join(f'<span class="chip neu">{html.escape(str(s))}</span>' for s in ex["technical_skills"])
                or "No skills detected.", unsafe_allow_html=True)
    st.write(f"CGPA found: {', '.join(str(c[0]) for c in ex['cgpa'].get('candidates', [])) or 'not found'} · "
             f"Projects (estimate): {ex['project_count_estimate']} · "
             f"Certifications (estimate): {ex['certification_count_estimate']}")
    for n in ex["parsing_notes"]:
        st.caption(n)

# ------------------------------------------------------------------ step 2
st.markdown("#### Step 2 · Confirm your details")
with st.expander("Your details (edit anything we got wrong)", expanded="result" not in st.session_state):
    with st.form("profile"):
        vals = {}
        edu = ex.get("education", {})
        guesses = {"Education_Level": edu.get("level_guess"),
                   "Branch": role_extensions.branch_guess(ex, resume_text)}

        st.markdown("**🎓 Education**")
        c1, c2, c3 = st.columns(3)
        cat_cols = [c for c in cats if c in raw_cols]
        for i, c in enumerate(cat_cols):
            required = c in ec.CRITICAL_FIELDS
            options = cats[c] if required else ["(not provided)"] + cats[c]
            v = (c1, c2, c3)[i % 3].selectbox(flabel(c), options, index=pick_index(options, guesses.get(c)),
                                              key=K(f"cat_{c}"))
            vals[c] = None if v == "(not provided)" else v
        vals["Year"] = c1.number_input("Year of study", 1, 6, 3, key=K("year"))
        best = ex["cgpa"].get("best")
        vals["CGPA"] = c2.number_input("CGPA (out of 10)", 0.0, 10.0, float(best) if best else 8.0, 0.01, key=K("cgpa"))
        vals["Backlogs"] = c3.number_input("Active backlogs", 0, 50, 0, key=K("backlogs"))

        st.markdown("**💼 Experience**")
        e1, e2, e3 = st.columns(3)
        vals["Project_Count"] = e1.number_input("Projects", 0, 50, int(ex["project_count_estimate"] or 0), key=K("proj"))
        vals["Internship"] = int(e2.selectbox("Internship done?", ["No", "Yes"],
                                              index=1 if ex["internship"].get("internship_keyword") else 0,
                                              key=K("intern")) == "Yes")
        vals["Internship_Duration_Months"] = e3.number_input(
            "Internship months (if yes)", 0.0, 36.0, float(ex["internship"].get("duration_months_candidate") or 0.0),
            0.5, key=K("intern_m"))

        st.markdown("**✨ Optional extras** — the more you add, the more personal your result.")
        o1, o2, o3 = st.columns(3)
        opt_cols = [c for c in ("Certification_Count", "Relevant_Project_Count", "Relevant_Certification_Count",
                                "Attendance_Percentage", "Core_Subject_Score", "Technical_Subject_Score",
                                "Aptitude_Score") if c in raw_cols]
        for i, c in enumerate(opt_cols):
            with (o1, o2, o3)[i % 3]:
                vals[c] = opt_number(flabel(c), K(f"opt_{c}"))
        with o1:
            for c, mention in (("Hackathon_Participation", ex.get("hackathon_mention")),
                               ("Open_Source_Contribution", ex.get("open_source_mention"))):
                if c in raw_cols:
                    vals[c] = ynu(flabel(c), K(f"yn_{c}"), optional=True, default="Yes" if mention else None)
        with o2:
            for c in ("PG_Required_For_Target_Role", "Relevant_Degree_Required"):
                if c in raw_cols:
                    vals[c] = ynu(flabel(c), K(f"yn_{c}"), optional=True)
        with o3:
            for c in ec.SOFT_SKILL_COLUMNS:
                if c in raw_cols:
                    vals[c] = opt_number(flabel(c), K(f"soft_{c}"))

        st.markdown("**🧰 Your skills** — tick what you can genuinely use.")
        detected = [k for k in ex["skill_detections"] if k in SKILLS]
        all_keys = [k for k in MODEL_TECH_SKILL_KEYS if k in raw_cols]
        default_present = [k for k in detected if k in all_keys]
        present = st.multiselect("Skills you have", all_keys, default=default_present,
                                 format_func=display_name, key=K("present"))
        domains = sorted({SKILLS[k]["domain"] for k in all_keys})
        default_domains = sorted({SKILLS[k]["domain"] for k in default_present})
        absent_domains = st.multiselect(
            "Skill areas where your list above is complete (anything not ticked there = you don't have it)",
            domains, default=default_domains, key=K("domains"))
        manual = st.text_input("Other skills not in the list (comma-separated)", key=K("manual"))
        not_have = st.text_input("Skills on your resume that you can't really use yet (comma-separated)",
                                 key=K("nothave"))
        go = st.form_submit_button("🚀 Analyze my profile", type="primary")

if go:
    p = ec.StudentProfile()
    for c, v in vals.items():
        if c in raw_cols and v is not None:
            p.set(c, v)
    if vals.get("Internship") == 0:
        p.set("Internship_Duration_Months", 0)
    ec.apply_skill_review(p, ex["skill_detections"], set(present), absent_domains=tuple(absent_domains))
    X_raw, rep = ec.build_raw_row(p, raw_cols, cats, handle)
    if rep["errors"]:
        st.error("Please fix the following:\n\n" + "\n".join(f"- {e}" for e in rep["errors"]))
        st.stop()
    st.session_state.result = dict(p=p, X_raw=X_raw, rep=rep,
                                   manual=[s.strip() for s in manual.split(",") if s.strip()],
                                   not_have=[s.strip() for s in not_have.split(",") if s.strip()])

if "result" not in st.session_state:
    st.stop()

# ------------------------------------------------------------------ compute
R = st.session_state.result
p, X_raw, rep = R["p"], R["X_raw"], R["rep"]

try:
    pred = ec.predict_employability(model, pre, X_raw)
except Exception as e:
    print("Scoring error:", e)
    st.error("We couldn't calculate a score for these details. Please check your entries and try again.")
    st.stop()
score = pred["p_placed"] * 100
lvl, lvl_color, lvl_msg = level_of(pred["p_placed"])

sx, helping, hurting, assumed, chart_df, baseline = None, [], [], [], None, None
try:
    sx = ec.explain_prediction(model, pre, X_raw, background_df=df)
    t = sx["raw_table"]
    known = t[(~t["imputed"]) & (t["shap"].abs() > 1e-3)]
    assumed = list(t[t["imputed"]]["feature"])
    mx = known["shap"].abs().max() if len(known) else 1.0
    pos = known[known["shap"] > 0].sort_values("shap", ascending=False).head(5)
    neg = known[known["shap"] < 0].sort_values("shap").head(5)
    helping = [f"{describe(r)} — {strength(r.shap, mx).lower()} boost" for r in pos.itertuples()]
    hurting = [f"{describe(r)} — {strength(r.shap, mx).lower()} drag" for r in neg.itertuples()]
    top = known.reindex(known["shap"].abs().sort_values(ascending=False).index).head(10)
    chart_df = pd.DataFrame({
        "label": [f"{flabel(r.feature)} ({fmt_value(r.feature, r.student_value)})" for r in top.itertuples()],
        "impact": [100 * r.shap / mx for r in top.itertuples()],
        "effect": [("Helps · " if r.shap > 0 else "Holds back · ") + strength(r.shap, mx) for r in top.itertuples()]})
    baseline = sx["base_probability"]
except Exception as e:
    print("Explanation error:", e)

res, wi, gains, gap_err = None, None, None, None
try:
    res = sg.run_skill_gap(role, ec=ec, resume_text=resume_text, ex=ex, profile=p,
                           manual_skills=R["manual"], not_have=R["not_have"], interactive=False)
    try:
        wi = sg.what_if_model(ec, model, pre, X_raw, res["gap"])
        if len(wi["table"]):
            gains = wi["table"].assign(gain=lambda d: d["change"] * 100)
            gains = gains[gains["gain"] > 0.05].head(8)[["skill", "gain"]]
    except Exception as e:
        print("What-if error:", e)
except Exception as e:
    gap_err = e

# ------------------------------------------------------------------ results
st.markdown("---")
tab1, tab2 = st.tabs(["📊 Your employability score", f"🧭 Skills for {role}"])

with tab1:
    for w in rep["warnings"]:
        st.warning(w)
    a, b = st.columns([1, 1.5])
    with a:
        st.markdown(f"""<div class="card"><div class="small">Your employability score</div>
<div class="score" style="color:{lvl_color}">{score:.0f}%</div>
<div class="lvl" style="color:{lvl_color}">{lvl}</div>
<div class="bar"><div style="width:{score:.0f}%;background:{lvl_color}"></div></div>
{f'<div class="small" style="margin-top:.6rem">Typical profile: about {baseline*100:.0f}%</div>' if baseline is not None else ''}
</div>""", unsafe_allow_html=True)
    with b:
        if gains is not None and len(gains):
            items = "".join(f"<li>Add <b>{html.escape(r.skill)}</b> → about <b>{r.gain:+.1f} points</b></li>"
                            for r in gains.head(3).itertuples())
            extra = f"<b>Quickest ways to raise your score</b><ul>{items}</ul>"
        else:
            extra = "Fill in the optional extras and confirm your skills to sharpen this score."
        st.markdown(f'<div class="card"><b>{lvl_msg}</b><br><br>{extra}</div>', unsafe_allow_html=True)
    st.caption("This score is an estimate to help you prepare. It is not a guarantee of any hiring outcome.")

    st.subheader("Why you got this score")
    if sx is None:
        st.info("A detailed breakdown isn't available right now.")
    else:
        g1, g2 = st.columns(2)
        with g1:
            st.markdown("##### 👍 What is helping you")
            for h in helping or ["Nothing stands out yet. Add details to see more."]:
                st.markdown(f'<div class="good">{h}</div>', unsafe_allow_html=True)
        with g2:
            st.markdown("##### 👎 What is holding you back")
            for h in hurting or ["Nothing stands out. Nice!"]:
                st.markdown(f'<div class="bad">{h}</div>', unsafe_allow_html=True)
        if chart_df is not None and len(chart_df):
            st.markdown("##### Biggest factors at a glance")
            st.altair_chart(impact_chart(chart_df))
            st.caption("Bars show relative influence on your score. Longer bar = bigger influence.")
        if assumed:
            with st.expander(f"{len(assumed)} details weren't provided, so we assumed average values"):
                st.write(", ".join(flabel(c) for c in assumed))
                st.caption("Add these in Step 2 for a more personal result.")

with tab2:
    if gap_err is not None:
        st.error(f"We couldn't analyse this role: {gap_err}")
    else:
        g, r = res["gap"], res["recs"]
        st.subheader(f"Your readiness for {res['role_name']}")
        m1, m2, m3 = st.columns(3)
        m1.metric("Overall readiness", f"{g['score']:.0f}/100")
        m2.metric("Must-have skills covered", f"{g['core_pct'] or 0:.0f}%")
        m3.metric("Nice-to-have skills covered", f"{g['preferred_pct'] or 0:.0f}%")
        st.progress(min(max(g["score"] / 100, 0.0), 1.0))
        st.write(g["label"])

        t = g["table"]
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("##### Must-have skills")
            st.markdown(chips(t[t.importance == "Core"]), unsafe_allow_html=True)
        with c2:
            st.markdown("##### Nice-to-have skills")
            st.markdown(chips(t[t.importance == "Preferred"]), unsafe_allow_html=True)
        st.caption("✓ you have it · ＋ gap to close. Readiness counts must-have skills double.")

        st.markdown("### 🗺️ Your learning plan")
        lp = r["learning_plan"]
        if lp.empty:
            st.success("No gaps against this role's skill list. Focus on projects, depth and interview practice.")
        else:
            for phase, d in lp.groupby("phase", sort=False):
                with st.expander(f"{phase}  ·  {len(d)} skill{'s' if len(d) != 1 else ''}", expanded=phase.startswith("Phase 1")):
                    for row in d.itertuples():
                        st.markdown(f"**{row.skill}** · ~{row.est_weeks} week{'s' if row.est_weeks != 1 else ''}")
                        st.caption(row.how)
            st.info(f"Roughly **{r['core_weeks']} weeks** for the must-haves, plus about "
                    f"**{r['preferred_weeks']} weeks** for the nice-to-haves (at 8–10 hours a week).")

        if gains is not None and len(gains):
            st.markdown("### 🚀 Skills that would lift your score the most")
            st.altair_chart(gain_chart(gains))

        pc, cc = st.columns(2)
        with pc:
            st.markdown("### 🛠️ Projects to build")
            for x in r["projects"] or []:
                cov = f" — closes: {', '.join(x['covers'])}" if x["covers"] else ""
                st.markdown(f"- {x['title']}{cov}")
            if not r["projects"]:
                st.caption("No project suggestions for this role.")
        with cc:
            st.markdown("### 🎓 Certifications to consider")
            st.caption("Check current availability and cost.")
            for x in r["certifications"] or []:
                st.markdown(f"- {x}")
            if not r["certifications"]:
                st.caption("No certification suggestions for this role.")

        q1, q2, q3 = st.columns(3)
        for col, title, items in ((q1, "👤 Profile improvements", r["profile"]),
                                  (q2, "📄 Resume tips", r["resume"]),
                                  (q3, "🎤 Interview topics", r["interview_topics"])):
            with col:
                st.markdown(f"#### {title}")
                for i in items:
                    st.markdown(f"- {i}")

        st.download_button("⬇️ Download my full report", build_report(res["role_name"], score, lvl, helping, hurting, res, gains),
                           file_name="careerlens_report.md", mime="text/markdown")