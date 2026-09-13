#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from html import escape
from pathlib import Path


def latest_report(root: Path) -> Path:
    reports = sorted((root / "outputs").glob("report-*.json"), key=lambda p: p.stat().st_mtime)
    if not reports:
        raise FileNotFoundError("No report found. Run scripts/run_v1.py first.")
    return reports[-1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    report_path = args.report or latest_report(root)
    report = json.loads(report_path.read_text(encoding="utf-8"))
    metrics = report.get("metrics", {})
    calibration = metrics.get("calibration", {})
    thresholds = metrics.get("threshold_analysis", {})
    subgroups = metrics.get("subgroup_diagnostics", {})
    findings = report.get("findings", [])

    finding_rows = "".join(
        f"<tr><td>{escape(f['check'])}</td><td class='{('pass' if f['passed'] else 'warn')}'>{'PASS' if f['passed'] else 'FLAG'}</td>"
        f"<td>{escape(f['severity'].upper())}</td><td>{escape(f['evidence'])}</td></tr>" for f in findings
    )
    threshold_rows = "".join(
        f"<tr><td>{row['threshold']:.2f}</td><td>{row['flagged_count']:,}</td><td>{row['precision']:.3f}</td>"
        f"<td>{row['recall']:.3f}</td><td>{row['illustrative_cost']:,.0f}</td></tr>" for row in thresholds.get("rows", [])
    )
    chain_html = "".join(
        f"<li><b>{escape(item['stage'].upper())}</b><span>{escape(item['result'])}</span></li>"
        for item in report.get("evidence_chain", [])
    )
    limitations = "".join(f"<li>{escape(item)}</li>" for item in report.get("limitations", []))
    prevalence_shift = abs(metrics.get("positive_rate_test", 0) - metrics.get("positive_rate_train", 0))
    baseline_brier = metrics.get("baseline_brier_score", 0)
    model_brier = metrics.get("brier_score", 0)
    brier_skill = 1 - model_brier / baseline_brier if baseline_brier else 0

    labels = ["ROC AUC", "Avg precision", "Brier skill", "Balanced accuracy"]
    values = [metrics.get("roc_auc", 0), metrics.get("average_precision", 0), brier_skill, metrics.get("balanced_accuracy_at_0_5", 0)]
    calibration_bins = calibration.get("bins", [])
    threshold_data = thresholds.get("rows", [])
    subgroup_rows = subgroups.get("rows", [])

    status_html = escape(report["status"]).replace("_", "_<wbr>")

    html = f"""<!doctype html>
<html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>A2 V1.1 Evidence Surface</title><script src='https://cdn.plot.ly/plotly-2.35.2.min.js'></script>
<style>
:root{{--ink:#10243e;--muted:#637083;--line:#d9e0e8;--blue:#177ddc;--amber:#a45f00;--green:#16815d;--paper:#f4f7fa}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--paper);color:var(--ink);font:15px/1.5 Inter,system-ui,sans-serif}}
header{{background:#071b31;color:white;padding:38px max(5vw,28px)}} h1{{margin:5px 0;font-size:clamp(28px,4vw,48px);letter-spacing:-.03em}} h2{{margin-top:0}}
.eyebrow{{color:#9fc8ee;font-weight:700;letter-spacing:.12em;font-size:12px}} main{{max-width:1280px;margin:0 auto;padding:28px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:16px}} .two{{display:grid;grid-template-columns:repeat(auto-fit,minmax(440px,1fr));gap:18px}}
.card{{min-width:0;background:white;border:1px solid var(--line);border-radius:12px;padding:20px;box-shadow:0 4px 18px #10243e0a}} .big{{font-size:29px;font-weight:760}}
.muted{{color:var(--muted)}} .status,.warn{{color:var(--amber);font-weight:700}} .status{{font-size:clamp(18px,1.8vw,24px);line-height:1.12;overflow-wrap:anywhere}} section{{margin:22px 0}} .boundary{{border-left:5px solid var(--amber);background:#fff8eb}}
table{{width:100%;border-collapse:collapse}} th,td{{padding:10px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}} th{{font-size:11px;text-transform:uppercase;color:var(--muted)}}
.pass{{color:var(--green);font-weight:700}} .chain{{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:10px;padding:0;list-style:none}}
.chain li{{background:#eef5fb;border-left:4px solid var(--blue);padding:13px}} .chain span{{display:block;color:var(--muted);margin-top:5px}} .scroll{{overflow-x:auto}}
.pill{{display:inline-block;border:1px solid #416584;border-radius:99px;padding:3px 9px;margin-top:8px;color:#bed7ee;font-size:12px}}
@media(max-width:600px){{main{{padding:16px}} .two{{grid-template-columns:1fr}}}}
</style></head><body>
<header><div class='eyebrow'>PROJECT A PRO — A2 V1.1</div><h1>Evidence-Governed Data Science</h1><div>Model performance, evidence sufficiency and execution authority are separate decisions.</div><div class='pill'>Run {escape(report.get('run_id', 'unknown'))}</div></header>
<main><div class='grid'>
<div class='card'><div class='muted'>Decision status</div><div class='big status'>{status_html}</div></div>
<div class='card'><div class='muted'>Analysis complete</div><div class='big'>{str(report['analysis_complete']).upper()}</div></div>
<div class='card'><div class='muted'>Action authorised</div><div class='big'>{str(report['action_authorised']).upper()}</div></div>
<div class='card'><div class='muted'>Expected calibration error</div><div class='big'>{calibration.get('expected_calibration_error', 0):.3f}</div></div>
<div class='card'><div class='muted'>Target prevalence shift</div><div class='big'>{prevalence_shift:.1%}</div></div>
</div>
<section class='card boundary'><h2>Authority boundary</h2><p><b>Analysis is complete, but no action is authorised.</b> The severe historical population shift, probability miscalibration in high-score bands and absent consent/capacity criteria require accountable human review and prospective validation.</p></section>
<div class='two'>
<section class='card'><h2>Validation evidence</h2><div id='metrics' style='height:350px'></div></section>
<section class='card'><h2>Calibration reliability</h2><div id='calibration' style='height:350px'></div><p class='muted'>{escape(calibration.get('warning', ''))}</p></section>
<section class='card'><h2>Threshold consequences</h2><div id='thresholds' style='height:350px'></div><p class='muted'>{escape(thresholds.get('warning', ''))}</p></section>
<section class='card'><h2>Subgroup stability</h2><div id='subgroups' style='height:350px'></div><p class='muted'>{escape(subgroups.get('warning', ''))}</p></section>
</div>
<section class='card'><h2>Threshold sensitivity table</h2><p class='muted'>Illustrative cost only: false positive = 1 unit; false negative = 5 units. Lowest displayed cost is not an authorised operating threshold.</p><div class='scroll'><table><thead><tr><th>Threshold</th><th>Flagged</th><th>Precision</th><th>Recall</th><th>Illustrative cost</th></tr></thead><tbody>{threshold_rows}</tbody></table></div></section>
<section class='card'><h2>Evidence-qualified conclusion</h2><p>{escape(report.get('conclusion', ''))}</p></section>
<section class='card'><h2>Evidence chain</h2><ol class='chain'>{chain_html}</ol></section>
<section class='card'><h2>Data-quality and assumption gates</h2><div class='scroll'><table><thead><tr><th>Check</th><th>Result</th><th>Severity</th><th>Evidence</th></tr></thead><tbody>{finding_rows}</tbody></table></div></section>
<section class='card'><h2>Limitations visible at decision time</h2><ul>{limitations}</ul></section>
</main><script>
const base={{margin:{{t:20,l:50,r:20,b:55}},paper_bgcolor:'white',plot_bgcolor:'white',font:{{color:'#10243e'}}}};
Plotly.newPlot('metrics',[{{type:'bar',x:{json.dumps(labels)},y:{json.dumps(values)},marker:{{color:['#177ddc','#16815d','#7f8da0','#a45f00']}}}}],{{...base,yaxis:{{range:[0,1],title:'Score'}}}},{{responsive:true,displaylogo:false}});
const cb={json.dumps(calibration_bins)};
Plotly.newPlot('calibration',[{{type:'scatter',mode:'lines',x:[0,1],y:[0,1],name:'Ideal',line:{{dash:'dot',color:'#7f8da0'}}}},{{type:'scatter',mode:'lines+markers',x:cb.map(d=>d.mean_prediction),y:cb.map(d=>d.observed_rate),text:cb.map(d=>'n='+d.count),name:'Observed',line:{{color:'#177ddc'}}}}],{{...base,xaxis:{{range:[0,1],title:'Mean predicted probability'}},yaxis:{{range:[0,1],title:'Observed rate'}}}},{{responsive:true,displaylogo:false}});
const th={json.dumps(threshold_data)};
Plotly.newPlot('thresholds',[{{type:'scatter',mode:'lines+markers',x:th.map(d=>d.threshold),y:th.map(d=>d.precision),name:'Precision'}},{{type:'scatter',mode:'lines+markers',x:th.map(d=>d.threshold),y:th.map(d=>d.recall),name:'Recall'}},{{type:'scatter',mode:'lines+markers',x:th.map(d=>d.threshold),y:th.map(d=>d.flagged_rate),name:'Flagged rate'}}],{{...base,xaxis:{{title:'Threshold'}},yaxis:{{range:[0,1],title:'Rate'}},legend:{{orientation:'h'}}}},{{responsive:true,displaylogo:false}});
const sg={json.dumps(subgroup_rows)}; const colors={{age_band:'#177ddc',job:'#16815d',contact:'#a45f00'}};
Plotly.newPlot('subgroups',Object.keys(colors).map(field=>{{const rows=sg.filter(d=>d.field===field);return {{type:'bar',name:field,x:rows.map(d=>d.group),y:rows.map(d=>d.brier_score),text:rows.map(d=>'n='+d.n),marker:{{color:colors[field]}}}}}}),{{...base,barmode:'group',xaxis:{{tickangle:-40}},yaxis:{{title:'Brier score (lower is better)'}},legend:{{orientation:'h'}}}},{{responsive:true,displaylogo:false}});
</script></body></html>"""
    destination = root / "dashboard" / "index.html"
    destination.write_text(html, encoding="utf-8")
    print(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
