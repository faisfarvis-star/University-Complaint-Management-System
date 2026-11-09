/* CampusFlow – admin analytics. Reads server data from <script type="application/json" id="chart-data">. */
(function () {
  "use strict";
  var node = document.getElementById("chart-data");
  if (!node || typeof Chart === "undefined") return;
  var data = JSON.parse(node.textContent);
  var charts = [];
  function css(v) { return getComputedStyle(document.documentElement).getPropertyValue(v).trim(); }
  function sum(a) { return a.reduce(function (x, y) { return x + y; }, 0); }

  function make(id, config, values) {
    var canvas = document.getElementById(id); if (!canvas) return;
    var box = canvas.closest(".chart-box");
    if (!values.length || sum(values) === 0) { box.classList.add("is-empty"); return; }
    charts.push(new Chart(canvas, config));
  }
  function base() {
    return { maintainAspectRatio: false, animation: { duration: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? 0 : 700 },
      plugins: { legend: { labels: { color: css("--text-2"), usePointStyle: true, boxWidth: 8, font: { family: css("--font") } } } } };
  }
  function axes() {
    var tick = { color: css("--text-2"), font: { family: css("--font") } };
    return { x: { ticks: tick, grid: { display: false } }, y: { beginAtZero: true, ticks: Object.assign({ precision: 0 }, tick), grid: { color: css("--border") } } };
  }
  function build() {
    var P = css("--primary"), S = css("--secondary"), A = css("--accent"), OK = css("--success"), W = css("--warning"), D = css("--danger");
    var trendVals = data.trend.map(function (t) { return t.count; });
    var o = base(); o.plugins.legend.display = false; o.scales = axes();
    make("trendChart", { type: "line", data: { labels: data.trend.map(function (t) { return t.label; }),
      datasets: [{ label: "Complaints", data: trendVals, borderColor: P, backgroundColor: "rgba(99,102,241,.16)", fill: true, tension: .35, pointRadius: 4, pointBackgroundColor: P }] }, options: o }, trendVals);

    var sv = [data.status.pending, data.status.in_progress, data.status.resolved, data.status.closed];
    var so = base(); so.cutout = "68%"; so.plugins.legend.position = "bottom";
    make("statusChart", { type: "doughnut", data: { labels: ["Pending", "In progress", "Resolved", "Closed"],
      datasets: [{ data: sv, backgroundColor: [W, S, OK, "#64748B"], borderColor: css("--surface"), borderWidth: 3 }] }, options: so }, sv);

    var cv = Object.keys(data.category).map(function (k) { return data.category[k]; });
    var co = base(); co.indexAxis = "y"; co.plugins.legend.display = false;
    var ax = axes();
    co.scales = { x: Object.assign({}, ax.y), y: Object.assign({}, ax.x, { beginAtZero: false }) };
    make("categoryChart", { type: "bar", data: { labels: Object.keys(data.category),
      datasets: [{ label: "Complaints", data: cv, backgroundColor: [P, S, A, OK, W, D, "#64748B"], borderRadius: 8, maxBarThickness: 26 }] }, options: co }, cv);

    var pv = Object.keys(data.priority).map(function (k) { return data.priority[k]; });
    var po = base(); po.cutout = "68%"; po.plugins.legend.position = "bottom";
    make("priorityChart", { type: "doughnut", data: { labels: Object.keys(data.priority),
      datasets: [{ data: pv, backgroundColor: ["#94A3B8", A, W, D], borderColor: css("--surface"), borderWidth: 3 }] }, options: po }, pv);
  }
  function rebuild() { charts.forEach(function (c) { c.destroy(); }); charts = []; document.querySelectorAll(".chart-box").forEach(function (b) { b.classList.remove("is-empty"); }); build(); }
  build();
  document.addEventListener("cf:theme", rebuild);
})();
