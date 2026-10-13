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

function renderState(data, code) {
  const series=data.state_series[code];
  const first=series[0], last=series[series.length-1];
  const change=pctChange(last.nonresident, first.nonresident);
  document.querySelector('#state-2015').textContent=fmtInt.format(first.nonresident);
  document.querySelector('#state-2024').textContent=fmtInt.format(last.nonresident);
  document.querySelector('#state-change').textContent=signedPct(change);
  document.querySelector('#state-share').textContent=`${fmtPct.format(last.share_pct)}%`;
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

  barChart(document.querySelector('#state-bars'),data.top_states_latest);

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

  document.querySelector('#qa-archives').textContent=fmtInt.format(data.quality.source_archives);
  document.querySelector('#qa-years').textContent=fmtInt.format(data.quality.schema_years_passed);
  document.querySelector('#qa-rows').textContent=fmtInt.format(data.quality.institution_year_rows);
  document.querySelector('#qa-benchmark').textContent=data.quality.benchmark.status;

  const sources=document.querySelector('#source-list');
  data.sources.forEach(src=>{const li=document.createElement('li');const a=document.createElement('a');a.href=src.url;a.target='_blank';a.rel='noopener';a.textContent=src.label;li.appendChild(a);sources.appendChild(li);});
}

init().catch(error=>{
  console.error(error);
  document.querySelector('#national-chart').textContent='Unable to load analysis data.';
});
