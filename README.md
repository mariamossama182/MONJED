<div align="center">

# 🌍 MONJED AI

### Multi-Hazard Early Warning & Community Resilience Platform

**From Risk Intelligence to Resilient Action.**

A full-stack disaster resilience platform that combines independent hazard assessment, community intelligence, deterministic decision-making, controlled AI communication, accessibility-aware assistance, and low-connectivity alert delivery.

---

</div>

## 🚨 The Problem

During disasters, receiving a warning is not always enough.

A person may know that a flood or earthquake risk exists but still face barriers such as:

- Limited or no internet connectivity
- Blocked roads or transportation challenges
- Difficulty understanding technical risk information
- Accessibility needs
- Lack of immediate access to emergency assistance

Traditional warning systems often focus on **detecting and publishing risk**. MONJED extends the journey beyond detection by connecting:

> **Risk → Understanding → Decision → Communication → Action → Human Support**

---

# 🎯 What is MONJED?

**MONJED AI** is a multi-hazard early warning and community resilience platform designed to transform environmental signals and community reports into **zone-specific, explainable, and actionable information**.

The platform brings together:

- 🌊 Independent flood risk assessment
- 🌎 Independent earthquake risk assessment
- 👥 Community disaster reports
- ⚖️ Deterministic decision-making
- 🤖 Controlled AI-powered alert communication
- ♿ Accessibility-aware assistance
- 🤝 Human and volunteer support workflows
- 📱 SMS communication for low-connectivity situations

MONJED is designed around one fundamental principle:

> ## **The system decides. AI communicates.**

Artificial Intelligence is not allowed to independently calculate risk, determine emergency actions, or override the backend decision.

---

# ✨ Key Capabilities

| Capability | MONJED Implementation |
|---|---|
| 🌊 **Flood Risk Assessment** | Independent environmental flood risk analysis |
| 🌎 **Earthquake Assessment** | Independent seismic activity assessment |
| 📍 **Zone-Based Intelligence** | Risk and decisions associated with geographic zones |
| ⚖️ **Independent Hazards** | Flood and earthquake remain separate throughout assessment |
| 👥 **Community Reports** | Structured reports provide local context and evidence |
| 🧠 **Decision Engine** | Deterministic source of truth for safety actions |
| 🤖 **Controlled AI Communication** | AI transforms approved decisions into human-readable alerts |
| 🛡️ **AI Validation** | AI output is validated against protected backend values |
| ♿ **Accessibility Support** | Accessibility-aware assistance and communication context |
| 🆘 **Help Requests** | Users can request assistance through the platform |
| 🤝 **Volunteer Workflows** | Supports connecting assistance needs with human response |
| 📱 **SMS Alerts** | Alternative communication pathway for low-connectivity scenarios |
| 🌐 **Web Platform** | Interactive frontend for users and platform workflows |
| 🗄️ **Persistent Data Layer** | MongoDB repositories for platform entities and records |

---

# 🏗️ System Architecture

MONJED is built as a layered full-stack system where each component has a clear responsibility.

```text
                           ┌─────────────────────┐
                           │  EXTERNAL DATA      │
                           │                     │
                           │  Environmental &    │
                           │  Seismic Sources    │
                           └──────────┬──────────┘
                                      │
                         ┌────────────┴────────────┐
                         ▼                         ▼
                  FLOOD RISK ENGINE       EARTHQUAKE ENGINE
                         │                         │
                         └────────────┬────────────┘
                                      ▼
                           INDEPENDENT HAZARDS
                                      │
                                      ▼
                           COMMUNITY EVIDENCE
                                      │
                                      ▼
                             DECISION ENGINE
                                      │
                                      ▼
                      ACCESSIBILITY CONTEXT
                           (Optional)
                                      │
                                      ▼
                                AI ADAPTER
                                      │
                         ┌────────────┴────────────┐
                         ▼                         ▼
                  GEMINI COMMUNICATION     DETERMINISTIC
                        LAYER                FALLBACK
                         │                         │
                         └────────────┬────────────┘
                                      ▼
                              OUTPUT VALIDATION
                                      │
                         ┌────────────┴────────────┐
                         ▼                         ▼
                     WEB PLATFORM              SMS ALERTS