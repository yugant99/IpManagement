> Historical record: superseded by the user-directed agent-to-agent review. See agent-grilling.md.

# Round 1 — product boundary and delivery intent

Status: awaiting real user answers. Recommendations are not decisions.

❓ **Q001** — What must be true at the end of the three days: a coherent working demo, a demo with at least one real sandbox integration, or a production-design package?

➡️ **Recommended:** A coherent working demo with explicit simulated boundaries; include one real sandbox only if access and the contract are ready early.

---

❓ **Q002** — Which workflow should be the centerpiece: migration/import/compare, subscriber change through ServiceNow, or domain operations and alerts?

➡️ **Recommended:** Migration/import/compare feeding one reviewed IP change and a correlated ServiceNow handoff.

---

❓ **Q003** — Should multi-tenant mean internal domains with controlled access, or separate customer organizations with hard isolation?

➡️ **Recommended:** Internal domain access first; treat separate customer tenants as a distinct later requirement.

---

❓ **Q004** — Should containerized/virtualized networks mean deploying IPAM in containers/VMs, or managing those networks' address inventory?

➡️ **Recommended:** Managing their address inventory; packaging is already a separate capability.

---

❓ **Q005** — What should the maturity assessment deliver: an evidence-backed gap/action report, a scored maturity model, or external benchmarking?

➡️ **Recommended:** An evidence-backed gap/action report with owners and priorities.

---

❓ **Q006** — Is the product expected to manage existing DNS/DHCP systems, or operate the DNS/DHCP services themselves?

➡️ **Recommended:** Manage existing systems through supported interfaces; keep DNS writes excluded.

---

❓ **Q007** — What three-day window and working-hour budget should the plan use, including your review time and Spencer's available hours?

➡️ **Recommended:** Start the clock at implementation authorization, reserve 20% for integration/recovery, and use Spencer's earlier 6–8 hours total only if you renew that budget.

---

❓ **Q008** — Whose successful use should determine the demo's flow: a domain operator, an integration engineer, or an executive reviewer?

➡️ **Recommended:** A domain operator, with short supporting integration and executive views.

---
