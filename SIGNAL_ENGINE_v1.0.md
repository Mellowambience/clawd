# 🧲 SIGNAL ENGINE v1.0 — Geo-Aware Opportunity & Positioning System

**Principle:**  
You don’t chase jobs.  
You engineer visibility so the right opportunities pull you in.

---

## 0. 🧠 Core Model

> Signal + Fit + Timing = Opportunity

- **Signal** → How clearly you communicate value
- **Fit** → Alignment with role/company
- **Timing** → Entering early and directly

This system compresses time, not judgment.

---

## 1. 📡 Opportunity Radar (Geo-Aware Intake)

### Sources

- Job boards (LinkedIn, Indeed — limited usage)
- Company career pages (Greenhouse, Lever, Workday)
- Hiring posts (LinkedIn activity)
- Recruiter signals

### Filters

- Location: user-defined (e.g. NJ + Remote)
- Posted within 72 hours
- Role + seniority alignment
- Optional: salary threshold

### Output

→ 5–10 high-quality opportunities/day

---

## 2. 📍 Geo-Intelligence Layer

- Remote / Hybrid / Onsite classification
- Radius filtering (e.g. 25–100 miles)
- Commute scoring (optional)
- Market density awareness

---

## 3. 🧬 Profile Engine (Source of Truth)

Structured user data:

```json
{
  "skills": [],
  "roles": [],
  "achievements": [],
  "metrics": [],
  "tools": [],
  "tone": "concise-confident"
}
```

### Rules

- No fabrication
- Only verified experience
- Metrics prioritized

---

## 4. 🧠 Signal Sculptor (Core Output Engine)

For each approved job, generate:

### A. Tailored Resume

- 1 page max
- Relevant experience only
- Metrics surfaced early
- ATS-compatible

### B. Micro-Message

Short, direct, human:

> “Hey — saw you’re hiring for [role].  
> I’ve done [specific result].  
> If that’s relevant, I’d be open to a quick conversation.”

### C. Insight Drop (Optional)

- 1-line observation about company problem or stage
- Demonstrates awareness

---

## 5. 🎯 Entry Strategy (Leverage Layer)

### Path A (Preferred)

1. Identify hiring manager / team lead
2. Send micro-message
3. Submit application

### Path B

1. Apply
2. Immediately follow up with message

### Path C (Fallback)

- Apply only

---

## 6. 🧮 Relevance Scoring

### Hard Filters

- Skills match ≥ 70%
- Title gap ≤ 2 levels

### Score Calculation

```text
score =
  skills_match * 0.5 +
  recency * 0.2 +
  company_fit * 0.15 +
  role_alignment * 0.15
```

### Threshold

- Act only on score ≥ 80

---

## 7. ⚡ Automation Layer

### Automate

- Job discovery
- Filtering + scoring
- Resume draft generation
- Message drafting
- Contact discovery

### Do NOT Automate

- Final resume approval
- Message sending
- Conversations

Mode: Assisted (default)

---

## 8. 🔄 Daily Execution Loop (30–60 min)

1. System surfaces top 5 roles
2. User approves 3–5
3. Review generated assets
4. Send message (if possible)
5. Apply
6. Log outcome

---

## 9. 🔁 Feedback & Learning

Track:

- Applications sent
- Responses
- Interviews
- Rejections

Adjust:

- Messaging tone
- Resume emphasis
- Target role selection

Inject:

- 10–20% adjacent role exploration (avoid overfitting)

---

## 10. 🛡️ Risk Constraints (Built-In)

### Anti-Bot Protection

- No high-volume auto-apply
- Human-paced sessions
- Daily cap: 10–20 applications

### CAPTCHA Handling

- Pause + notify user
- Resume manually

### Data Integrity

- No fabricated experience
- Only structured profile inputs used

### Platform Compliance

- Prefer APIs / public sources
- Minimize scraping intensity

### System Resilience

- Modular scrapers
- Failover sources
- Health monitoring

---

## 11. 🛠️ Implementation Stack (Lean)

### Backend

- Python (FastAPI)

### Automation

- Playwright (persistent sessions)

### AI Layer

- OpenAI (generation + embeddings)

### Storage

- PostgreSQL (data)
- Redis (queue)

### Interface

- Notion / simple dashboard

### No-Code Alternative

- Zapier / Make
- Google Sheets
- OpenAI API

---

## 12. ⚙️ System Config (Safe Mode)

```ini
mode = assisted
daily_app_limit = 15
score_threshold = 80
auto_apply = false
resume_truth_mode = strict
scraping_intensity = low
```

---

## 13. 🧬 Multipliers

- Apply within first 24–48 hours
- Prioritize smaller companies (faster response)
- Message > application
- 10 high-signal entries > 100 blind applications

---

## 14. 🧭 End State

- < 1 hour/day effort
- Only high-quality roles surfaced
- Tailored positioning per opportunity
- Recruiter responses increase
- Reduced reliance on mass applying

---

## 15. 🔥 Final Principle

You are not trying to win the applicant pool.

You are positioning yourself so that:

By the time they see your resume,  
they already recognize your name.

---

## 16. 🚀 Minimal Command Interface

```bash
signal start
signal role "Customer Success Manager"
signal location "NJ + Remote"
signal daily_limit 5
signal mode assisted
```

---

**Result:**  
Consistent, high-quality opportunities with leverage—without brute force.
