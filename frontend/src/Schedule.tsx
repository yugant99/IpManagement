import { currentContext } from "./api";

export default function Schedule() {
  return <section aria-labelledby="schedule-heading">
    <div className="page-heading"><div><p className="eyebrow">Domain {currentContext().selected_domain} · saved evidence</p>
      <h1 id="schedule-heading">Evidence acquisition</h1>
      <p className="intro">Global acquisition, timer, schedule and callback controls are managed by the evidence operator.</p></div></div>
    <div className="notice" role="status">This domain session can inspect permitted saved run projections in Reconciliation and Capacity. If no run is available, it is awaiting evidence.</div>
  </section>;
}
