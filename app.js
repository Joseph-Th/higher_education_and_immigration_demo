const fmtInt = new Intl.NumberFormat('en-US');
const fmtPct = new Intl.NumberFormat('en-US', { maximumFractionDigits: 1, minimumFractionDigits: 1 });

const STATE_NAMES = {
  AL:'Alabama', AK:'Alaska', AZ:'Arizona', AR:'Arkansas', CA:'California', CO:'Colorado', CT:'Connecticut', DE:'Delaware', DC:'District of Columbia', FL:'Florida', GA:'Georgia', HI:'Hawaii', ID:'Idaho', IL:'Illinois', IN:'Indiana', IA:'Iowa', KS:'Kansas', KY:'Kentucky', LA:'Louisiana', ME:'Maine', MD:'Maryland', MA:'Massachusetts', MI:'Michigan', MN:'Minnesota', MS:'Mississippi', MO:'Missouri', MT:'Montana', NE:'Nebraska', NV:'Nevada', NH:'New Hampshire', NJ:'New Jersey', NM:'New Mexico', NY:'New York', NC:'North Carolina', ND:'North Dakota', OH:'Ohio', OK:'Oklahoma', OR:'Oregon', PA:'Pennsylvania', RI:'Rhode Island', SC:'South Carolina', SD:'South Dakota', TN:'Tennessee', TX:'Texas', UT:'Utah', VT:'Vermont', VA:'Virginia', WA:'Washington', WV:'West Virginia', WI:'Wisconsin', WY:'Wyoming'
};

const svgNS = 'http://www.w3.org/2000/svg';
const svgEl = (name, attrs = {}) => {
  const node = document.createElementNS(svgNS, name);
  Object.entries(attrs).forEach(([k,v]) => node.setAttribute(k, v));
  return node;
};

function lineChart(container, series, options = {}) {
  const width = 900, height = options.height || 330;
  const margin = { top: 24, right: 30, bottom: 42, left: 72 };
  const plotW = width - margin.left - margin.right;
  const plotH = height - margin.top - margin.bottom;
  const values = series.flatMap(s => s.values.map(d => d.value));
  const minYear = Math.min(...series[0].values.map(d => d.year));
  const maxYear = Math.max(...series[0].values.map(d => d.year));
  const minV = options.minValue ?? Math.min(...values) * .94;
  const maxV = options.maxValue ?? Math.max(...values) * 1.05;
  const x = year => margin.left + (year - minYear) / (maxYear - minYear) * plotW;
  const y = value => margin.top + (maxV - value) / (maxV - minV) * plotH;

  const svg = svgEl('svg', { viewBox: `0 0 ${width} ${height}`, role:'img', 'aria-label': options.ariaLabel || 'Line chart' });
  const ticks = 4;
  for (let i=0; i<=ticks; i++) {
    const v = minV + (maxV-minV) * i/ticks;
    const yy = y(v);
    svg.appendChild(svgEl('line', { x1:margin.left, y1:yy, x2:width-margin.right, y2:yy, class:'grid-line' }));
    const label = svgEl('text', { x:margin.left-12, y:yy+4, 'text-anchor':'end', class:'chart-label' });
    label.textContent = options.valueFormatter ? options.valueFormatter(v) : fmtInt.format(Math.round(v));
    svg.appendChild(label);
  }
  series[0].values.forEach(d => {
    const label = svgEl('text', { x:x(d.year), y:height-14, 'text-anchor':'middle', class:'chart-label' });
    label.textContent = d.year;
    svg.appendChild(label);
  });
  svg.appendChild(svgEl('line', { x1:margin.left, y1:margin.top+plotH, x2:width-margin.right, y2:margin.top+plotH, class:'axis-line' }));

  if (options.annotationYear) {
    const xx = x(options.annotationYear);
    svg.appendChild(svgEl('line', { x1:xx, y1:margin.top, x2:xx, y2:margin.top+plotH, class:'annotation-line' }));
    const ann = svgEl('text', { x:xx+8, y:margin.top+14, class:'chart-title-label' });
    ann.textContent = options.annotationLabel || String(options.annotationYear);
    svg.appendChild(ann);
  }

  series.forEach((s, idx) => {
    const points = s.values.map(d => `${x(d.year)},${y(d.value)}`).join(' ');
    svg.appendChild(svgEl('polyline', { points, class:`series-line ${idx ? 'secondary' : ''}` }));
    s.values.forEach(d => svg.appendChild(svgEl('circle', { cx:x(d.year), cy:y(d.value), r:4.2, class:`series-point ${idx ? 'secondary' : ''}` })));
    const last = s.values[s.values.length-1];
    const label = svgEl('text', { x:x(last.year)-5, y:y(last.value)-12, 'text-anchor':'end', class:'chart-title-label' });
    label.textContent = s.name;
    svg.appendChild(label);
  });
  container.replaceChildren(svg);
}

function dynamicsChart(container, dynamics) {
  const rows=[
    {label:'Continuing institutions',value:dynamics.continuing_change},
    {label:'Entered universe',value:dynamics.entered_enrollment},
    {label:'Left universe',value:-dynamics.left_enrollment},
    {label:'Net national change',value:dynamics.national_change,net:true}
  ];
  const width=900, height=330, margin={top:18,right:125,bottom:28,left:190};
  const center=width*.5;
  const usable=Math.min(center-margin.left-20,width-margin.right-center-20);
  const rowH=(height-margin.top-margin.bottom)/rows.length;
  const max=Math.max(...rows.map(row=>Math.abs(row.value)));
  const svg=svgEl('svg',{viewBox:`0 0 ${width} ${height}`,role:'img','aria-label':'Decomposition of the 2015 to 2024 national enrollment change into continuing institutions, institutions entering the analytic universe, institutions leaving the analytic universe, and net change'});
  svg.appendChild(svgEl('line',{x1:center,y1:margin.top,x2:center,y2:height-margin.bottom,class:'zero-line'}));
  rows.forEach((row,i)=>{
    const yy=margin.top+i*rowH+8;
    const magnitude=Math.abs(row.value)/max*usable;
    const positive=row.value>=0;
    const x=positive?center:center-magnitude;
    const label=svgEl('text',{x:margin.left-12,y:yy+rowH*.45,'text-anchor':'end',class:'chart-title-label'});
    label.textContent=row.label; svg.appendChild(label);
    svg.appendChild(svgEl('rect',{x,y:yy,width:magnitude,height:Math.max(18,rowH-20),rx:5,class:row.net?'change-bar-net':positive?'change-bar-positive':'change-bar-negative'}));
    const val=svgEl('text',{x:positive?x+magnitude+9:x-9,y:yy+rowH*.45,'text-anchor':positive?'start':'end',class:'bar-value'});
    val.textContent=signedInt(row.value); svg.appendChild(val);
  });
  container.replaceChildren(svg);
}

function updateChangeChart(container, review) {
  const rows=[
    {label:'Undergraduate',value:review.national.undergraduate_change},
    {label:'Graduate',value:review.national.graduate_change},
    {label:'Net change',value:review.national.absolute_change,net:true}
  ];
  const width=900, height=290, margin={top:22,right:120,bottom:30,left:165};
  const center=width*.49;
  const usable=Math.min(center-margin.left-24,width-margin.right-center-24);
  const rowH=(height-margin.top-margin.bottom)/rows.length;
  const max=Math.max(...rows.map(row=>Math.abs(row.value)));
  const prior=review.coverage.prior_year, latest=review.coverage.latest_year;
  const svg=svgEl('svg',{viewBox:`0 0 ${width} ${height}`,role:'img','aria-label':`Change in U.S. nonresident enrollment from ${prior} to ${latest}, decomposed into undergraduate, graduate, and net change`});
  svg.appendChild(svgEl('line',{x1:center,y1:margin.top,x2:center,y2:height-margin.bottom,class:'zero-line'}));
  rows.forEach((row,i)=>{
    const yy=margin.top+i*rowH+8;
    const magnitude=Math.abs(row.value)/max*usable;
    const positive=row.value>=0;
    const x=positive?center:center-magnitude;
    const label=svgEl('text',{x:margin.left-12,y:yy+rowH*.45,'text-anchor':'end',class:'chart-title-label'});
    label.textContent=row.label; svg.appendChild(label);
    svg.appendChild(svgEl('rect',{x,y:yy,width:magnitude,height:Math.max(20,rowH-22),rx:5,class:row.net?'change-bar-net':positive?'change-bar-positive':'change-bar-negative'}));
    const val=svgEl('text',{x:positive?x+magnitude+9:x-9,y:yy+rowH*.45,'text-anchor':positive?'start':'end',class:'bar-value'});
    val.textContent=signedInt(row.value); svg.appendChild(val);
  });
  container.replaceChildren(svg);
}

function controlChangeChart(container, rows) {
  const width=900, height=300, margin={top:22,right:110,bottom:34,left:170};
  const center=width*.48;
  const usable=Math.min(center-margin.left-24,width-margin.right-center-24);
  const rowH=(height-margin.top-margin.bottom)/rows.length;
  const max=Math.max(...rows.map(r=>Math.abs(r.absolute_change)));
  const svg=svgEl('svg',{viewBox:`0 0 ${width} ${height}`,role:'img','aria-label':'Change in U.S. nonresident enrollment by institutional control from 2015 to 2024'});
  svg.appendChild(svgEl('line',{x1:center,y1:margin.top,x2:center,y2:height-margin.bottom,class:'zero-line'}));
  rows.forEach((r,i)=>{
    const yy=margin.top+i*rowH+10;
    const magnitude=Math.abs(r.absolute_change)/max*usable;
    const positive=r.absolute_change>=0;
    const x=positive?center:center-magnitude;
    const label=svgEl('text',{x:margin.left-12,y:yy+rowH*.42,'text-anchor':'end',class:'chart-title-label'});
    label.textContent=r.control; svg.appendChild(label);
    svg.appendChild(svgEl('rect',{x,y:yy,width:magnitude,height:Math.max(20,rowH-24),rx:5,class:positive?'change-bar-positive':'change-bar-negative'}));
    const val=svgEl('text',{x:positive?x+magnitude+9:x-9,y:yy+rowH*.42,'text-anchor':positive?'start':'end',class:'bar-value'});
    val.textContent=signedInt(r.absolute_change); svg.appendChild(val);
  });
  container.replaceChildren(svg);
}

function divergingBarChart(container, gains, shortfalls) {
  const rows=[...gains.slice(0,6), ...shortfalls.slice(0,6)];
  const width=900, height=430, margin={top:12,right:92,bottom:30,left:72};
  const center=width/2;
  const usable=Math.min(center-margin.left-22, width-margin.right-center-22);
  const rowH=(height-margin.top-margin.bottom)/rows.length;
  const max=Math.max(...rows.map(r=>Math.abs(r.absolute_change)));
  const svg=svgEl('svg',{viewBox:`0 0 ${width} ${height}`,role:'img','aria-label':'Largest state gains and shortfalls in U.S. nonresident enrollment from 2019 to 2024'});
  svg.appendChild(svgEl('line',{x1:center,y1:margin.top,x2:center,y2:height-margin.bottom,class:'zero-line'}));
  rows.forEach((r,i)=>{
    const yy=margin.top+i*rowH+4;
    const magnitude=Math.abs(r.absolute_change)/max*usable;
    const positive=r.absolute_change>=0;
    const x=positive?center:center-magnitude;
    svg.appendChild(svgEl('rect',{x,y:yy,width:magnitude,height:Math.max(12,rowH-8),rx:4,class:positive?'change-bar-positive':'change-bar-negative'}));
    const state=svgEl('text',{x:positive?center-10:center+10,y:yy+rowH*.55,'text-anchor':positive?'end':'start',class:'chart-title-label'});
    state.textContent=r.state; svg.appendChild(state);
    const value=svgEl('text',{x:positive?x+magnitude+8:x-8,y:yy+rowH*.55,'text-anchor':positive?'start':'end',class:'bar-value'});
    value.textContent=`${r.absolute_change>=0?'+':''}${fmtInt.format(r.absolute_change)}`; svg.appendChild(value);
  });
  container.replaceChildren(svg);
}

function barChart(container, rows) {
  const width=900, height=390, margin={top:8,right:35,bottom:34,left:72};
  const plotW=width-margin.left-margin.right;
  const rowH=(height-margin.top-margin.bottom)/rows.length;
  const max=Math.max(...rows.map(r=>r.nonresident));
  const svg=svgEl('svg',{viewBox:`0 0 ${width} ${height}`,role:'img','aria-label':'Top states by U.S. nonresident enrollment in 2024'});
  rows.forEach((r,i)=>{
    const yy=margin.top+i*rowH+4;
    const w=r.nonresident/max*plotW;
    const state=svgEl('text',{x:margin.left-12,y:yy+rowH*.55,'text-anchor':'end',class:'chart-title-label'}); state.textContent=r.state; svg.appendChild(state);
    svg.appendChild(svgEl('rect',{x:margin.left,y:yy,width:w,height:Math.max(13,rowH-9),rx:4,class:'bar'}));
    const val=svgEl('text',{x:margin.left+w+8,y:yy+rowH*.55,class:'chart-label'}); val.textContent=fmtInt.format(r.nonresident); svg.appendChild(val);
  });
  container.replaceChildren(svg);
}

function pctChange(newV, oldV) { return (newV-oldV)/oldV*100; }
function signedPct(value) { return `${value >= 0 ? '+' : ''}${fmtPct.format(value)}%`; }
function signedInt(value) { return `${value >= 0 ? '+' : ''}${fmtInt.format(value)}`; }

const CASE_LABELS = {
  unresolved_anomaly:'Hold the anomaly',
  corroborated_movement:'Corroborate the direction',
  structural_change:'Explain the structural change'
};

function renderQaCases(container, cases) {
  const decision = value => value === 'safe_with_context' ? 'Publish with context' : 'Hold institution-specific claim';
  cases.forEach(caseRow=>{
    const article=document.createElement('article'); article.className='qa-case-card';
    const kicker=document.createElement('p'); kicker.className='case-kicker'; kicker.textContent=CASE_LABELS[caseRow.case_type]||'Analyst review';
    const title=document.createElement('h3'); title.textContent=caseRow.institution;
    const change=document.createElement('p'); change.className='case-change'; change.textContent=`${signedInt(Number(caseRow.absolute_change))} students`;
    const note=document.createElement('p'); note.textContent=caseRow.analyst_note;
    const footer=document.createElement('div'); footer.className='case-footer';
    const badge=document.createElement('span'); badge.className='case-decision'; badge.textContent=decision(caseRow.publication_class);
    const evidence=document.createElement('a'); evidence.href=caseRow.evidence_url; evidence.target='_blank'; evidence.rel='noopener'; evidence.textContent='Review evidence';
    footer.append(badge,evidence); article.append(kicker,title,change,note,footer); container.appendChild(article);
  });
}

function renderState(data, code) {
  const series=data.state_series[code];
  const first=series[0], last=series[series.length-1];
  const change=pctChange(last.nonresident, first.nonresident);
  document.querySelector('#state-2015').textContent=fmtInt.format(first.nonresident);
  document.querySelector('#state-2024').textContent=fmtInt.format(last.nonresident);
  document.querySelector('#state-change').textContent=signedPct(change);
  document.querySelector('#state-share').textContent=`${fmtPct.format(last.share_pct)}%`;
  const profileLink=document.querySelector('#state-profile-link');
  profileLink.href=`state.html?state=${code}`;
  profileLink.textContent=`Open ${STATE_NAMES[code]} state profile`;
  lineChart(document.querySelector('#state-chart'), [{name:code,values:series.map(d=>({year:d.year,value:d.nonresident}))}], {height:240, minValue:0, ariaLabel:`${STATE_NAMES[code]} U.S. nonresident enrollment, 2015 to 2024`, valueFormatter:v=>`${Math.round(v/1000)}k`});
}

async function init() {
  const response=await fetch('data/site_data.json');
  if (!response.ok) throw new Error(`Data load failed: ${response.status}`);
  const data=await response.json();
  const h=data.headline;
  document.querySelector('#metric-total').textContent=fmtInt.format(h.latest_nonresident);
  document.querySelector('#metric-share').textContent=`${fmtPct.format(h.latest_share_pct)}%`;
  document.querySelector('#metric-change').textContent=signedPct(h.change_since_2015_pct);
  document.querySelector('#metric-change-count').textContent=`${h.change_since_2015 >= 0 ? '+' : ''}${fmtInt.format(h.change_since_2015)} students`;
  document.querySelector('#metric-decline').textContent=`${fmtPct.format(h.largest_yoy_decline.pct)}%`;
  document.querySelector('#top5-share').textContent=`Top 5 states: ${fmtPct.format(h.top5_state_share_pct)}% of total`;

  const national=data.national_series;
  lineChart(document.querySelector('#national-chart'), [{name:'U.S. nonresident',values:national.map(d=>({year:d.year,value:d.nonresident}))}], {annotationYear:2020,annotationLabel:'2020 decline',ariaLabel:'National U.S. nonresident fall enrollment from 2015 through 2024',valueFormatter:v=>`${(v/1e6).toFixed(1)}M`});
  lineChart(document.querySelector('#level-chart'), [
    {name:'Graduate',values:national.map(d=>({year:d.year,value:d.graduate_nonresident}))},
    {name:'Undergraduate',values:national.map(d=>({year:d.year,value:d.undergraduate_nonresident}))}
  ], {ariaLabel:'Graduate and undergraduate U.S. nonresident fall enrollment from 2015 through 2024',valueFormatter:v=>`${Math.round(v/1000)}k`});

  const first=national[0], last=national[national.length-1];
  document.querySelector('#graduate-share').textContent=`${fmtPct.format(last.graduate_nonresident/last.nonresident*100)}%`;
  document.querySelector('#graduate-change').textContent=signedPct(pctChange(last.graduate_nonresident,first.graduate_nonresident));
  document.querySelector('#undergrad-change').textContent=signedPct(pctChange(last.undergraduate_nonresident,first.undergraduate_nonresident));
  document.querySelector('#graduate-change-count').textContent=signedInt(data.level_decomposition.graduate_change_students);
  document.querySelector('#undergrad-change-count').textContent=signedInt(data.level_decomposition.undergraduate_change_students);
  document.querySelector('#net-change-count').textContent=signedInt(data.level_decomposition.net_change_students);

  barChart(document.querySelector('#state-bars'),data.top_states_latest);
  document.querySelector('#states-recovered').textContent=data.recovery.states_at_or_above_baseline;
  document.querySelector('#states-below').textContent=data.recovery.states_below_baseline;
  divergingBarChart(document.querySelector('#recovery-chart'),data.recovery.largest_gains,data.recovery.largest_shortfalls);

  const controlChanges=data.institution_control.changes;
  controlChangeChart(document.querySelector('#control-change-chart'),controlChanges);
  const nonprofit=controlChanges.find(row=>row.control==='Private nonprofit');
  document.querySelector('#nonprofit-share-shift').textContent=`${fmtPct.format(nonprofit.start_national_share_pct)}% → ${fmtPct.format(nonprofit.latest_national_share_pct)}%`;
  document.querySelector('#nonprofit-grad-change').textContent=signedInt(nonprofit.graduate_change);
  document.querySelector('#nonprofit-total-change').textContent=signedInt(nonprofit.absolute_change);

  const dynamics=data.institution_dynamics.decade;
  dynamicsChart(document.querySelector('#dynamics-chart'),dynamics);
  document.querySelector('#dynamics-continuing-count').textContent=fmtInt.format(dynamics.continuing_institutions);
  document.querySelector('#dynamics-grew').textContent=fmtInt.format(dynamics.continuing_grew);
  document.querySelector('#dynamics-declined').textContent=fmtInt.format(dynamics.continuing_declined);
  document.querySelector('#dynamics-entry-exit-net').textContent=signedInt(dynamics.entry_exit_net);

  const update=data.latest_update_review;
  updateChangeChart(document.querySelector('#update-change-chart'),update);
  document.querySelector('#update-change-pct').textContent=signedPct(update.national.pct_change);
  document.querySelector('#update-total-change-copy').textContent=`${signedInt(update.national.absolute_change)} students from ${update.coverage.prior_year} to ${update.coverage.latest_year}`;
  document.querySelector('#update-undergrad-change').textContent=signedInt(update.national.undergraduate_change);
  document.querySelector('#update-grad-change').textContent=signedInt(update.national.graduate_change);
  document.querySelector('#update-high-priority').textContent=fmtInt.format(update.review_queue.high);
  document.querySelector('#update-medium-priority').textContent=fmtInt.format(update.review_queue.medium);
  document.querySelector('#update-entry-exit-net').textContent=signedInt(update.institution_accounting.entry_exit_net);
  const topUpdateState=update.state_change.largest_gains[0];
  document.querySelector('#update-top-state').textContent=`${topUpdateState.state} ${signedInt(topUpdateState.absolute_change)}`;
  const resolution=data.qa_resolution_summary;
  document.querySelector('#resolution-reviewed').textContent=fmtInt.format(resolution.reviewed_count);
  document.querySelector('#resolution-safe').textContent=fmtInt.format(resolution.safe_with_context);
  document.querySelector('#resolution-held').textContent=fmtInt.format(resolution.hold_for_confirmation);
  renderQaCases(document.querySelector('#qa-case-studies'),resolution.case_studies);

  const select=document.querySelector('#state-select');
  Object.keys(data.state_series).sort((a,b)=>STATE_NAMES[a].localeCompare(STATE_NAMES[b])).forEach(code=>{
    const opt=document.createElement('option'); opt.value=code; opt.textContent=`${STATE_NAMES[code]} (${code})`; select.appendChild(opt);
  });
  select.value='AZ';
  renderState(data,'AZ');
  select.addEventListener('change',()=>renderState(data,select.value));

  const tbody=document.querySelector('#institution-table');
  data.top_institutions_latest.slice(0,10).forEach(row=>{
    const tr=document.createElement('tr');
    [row.institution,row.state,fmtInt.format(row.nonresident),`${fmtPct.format(row.share_pct)}%`].forEach(text=>{const td=document.createElement('td');td.textContent=text;tr.appendChild(td);});
    tbody.appendChild(tr);
  });
  document.querySelector('#top10-inst-share').textContent=`${fmtPct.format(data.concentration.top10_institutions_share_pct)}%`;
  document.querySelector('#top100-inst-share').textContent=`${fmtPct.format(data.concentration.top100_institutions_share_pct)}%`;

  document.querySelector('#qa-archives').textContent=fmtInt.format(data.quality.source_archives);
  document.querySelector('#qa-years').textContent=fmtInt.format(data.quality.schema_years_passed);
  document.querySelector('#qa-rows').textContent=fmtInt.format(data.quality.institution_year_rows);
  document.querySelector('#qa-benchmark').textContent=data.quality.benchmark.checks_passed;

  const benchmarkLabels={
    total_enrollment:'All enrollment',
    nonresident_enrollment:'U.S. nonresident',
    undergraduate_nonresident:'Undergraduate nonresident',
    graduate_nonresident:'Graduate nonresident'
  };
  const benchmarkBody=document.querySelector('#benchmark-table');
  data.quality.benchmark.latest_rows.forEach(row=>{
    const tr=document.createElement('tr');
    const digest=Number(row.digest_approx_students);
    const diff=Number(row.difference_students);
    [benchmarkLabels[row.metric]||row.metric,fmtInt.format(Number(row.current_ipeds_value)),`≈ ${fmtInt.format(digest)}`,`${signedInt(diff)} (${signedPct(Number(row.difference_pct))})`].forEach(text=>{
      const td=document.createElement('td'); td.textContent=text; tr.appendChild(td);
    });
    benchmarkBody.appendChild(tr);
  });

  const sources=document.querySelector('#source-list');
  data.sources.forEach(src=>{const li=document.createElement('li');const a=document.createElement('a');a.href=src.url;a.target='_blank';a.rel='noopener';a.textContent=src.label;li.appendChild(a);sources.appendChild(li);});
}

init().catch(error=>{
  console.error(error);
  document.querySelector('#national-chart').textContent='Unable to load analysis data.';
});
