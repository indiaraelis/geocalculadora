/* ======================================================================
   GEOCALCULADORA BRASIL — SCRIPT PRINCIPAL
   ====================================================================== */

/* --------------------------- FUNÇÕES UTILITÁRIAS --------------------------- */
const getInputValue        = id => document.getElementById(id).value.trim();
const getInputValueAsFloat = id => parseFloat(getInputValue(id)) || 0;
const getSelectValue       = id => document.getElementById(id).value;

const formatarNumero = (num, casas = 2) =>
  Number(num).toLocaleString('pt-BR', {
    minimumFractionDigits: casas,
    maximumFractionDigits: casas
  });

const formatarDistancia = m =>
  m >= 1_000_000 ? `${formatarNumero(m / 1_000_000, 3)} Mm`
: m >=     1000 ? `${formatarNumero(m /     1000, 3)} km`
                : `${formatarNumero(m, 2)} m`;

const formatarArea = m2 =>
  m2 >= 1_000_000 ? `${formatarNumero(m2 / 1_000_000, 6)} km²`
: m2 >=     10000 ? `${formatarNumero(m2 /     10000, 4)} ha`
                  : `${formatarNumero(m2, 2)} m²`;

const formatarCoordenada = (c, casas = 6) => formatarNumero(c, casas);

/* ----------------------- CHAMADA PADRÃO AO BACKEND ------------------------ */
async function apiRequest(endpoint, payload, btn, resultEl) {
  const txt = btn.innerHTML;
  btn.disabled = true;
  btn.innerHTML = '<span class="loader"></span> Calculando…';
  resultEl.innerHTML = '';

  try {
    const res  = await fetch(endpoint, {
      method : 'POST',
      headers: { 'Content-Type': 'application/json' },
      body   : JSON.stringify(payload)
    });
    const data = await res.json();
    if (!res.ok || data.success === false)
      throw new Error(data.error || `HTTP ${res.status}`);
    return data;
  } catch (err) {
    console.error(err);
    resultEl.innerHTML = `<div class="result-error">${err.message}</div>`;
    throw err;
  } finally {
    btn.disabled = false;
    btn.innerHTML = txt;
  }
}

/* -------------------- FUNÇÃO GENÉRICA PARA CADA PAINEL -------------------- */
function handleRequest(event, endpoint, buildPayload, renderHtml) {
  const btn          = event.currentTarget;
  const resSelector  = btn.dataset.result || '';
  const resultEl     = document.querySelector(resSelector) || btn.nextElementSibling;
  const payload      = buildPayload();

  apiRequest(endpoint, payload, btn, resultEl)
    .then(renderHtml)
    .then(html => { resultEl.innerHTML = html; })
    .catch(() => {/* já tratado em apiRequest */});
}

/* ---------------------- HANDLERS DOS PAINÉIS (CRUD) ----------------------- */
const getDatum = () => getSelectValue('datumGlobalSelect');

/* Distância ---------------------------------------------------------------- */
function handleDistancia(e){
  handleRequest(e, '/calcular_distancia', () => ({
    lat1 : getInputValueAsFloat('dist_lat1'),  lon1 : getInputValueAsFloat('dist_lon1'),
    lat2 : getInputValueAsFloat('dist_lat2'),  lon2 : getInputValueAsFloat('dist_lon2'),
    datum: getDatum()
  }), d => `
    <div class="result-success">
      <h4>Distância & Azimute</h4>
      <p><b>Distância:</b> ${formatarDistancia(d.distancia_metros)}</p>
      <p><b>Azimute Direto:</b> ${formatarNumero(d.azimute_direto,4)}°</p>
      <p><b>Azimute Inverso:</b> ${formatarNumero(d.azimute_inverso,4)}°</p>
      <p><b>Datum:</b> ${d.datum_usado}</p>
    </div>`);}
    
/* Área --------------------------------------------------------------------- */
function handleArea(e){
  handleRequest(e, '/calcular_area', () => ({
    latA:getInputValueAsFloat('area_latA'), lonA:getInputValueAsFloat('area_lonA'),
    latB:getInputValueAsFloat('area_latB'), lonB:getInputValueAsFloat('area_lonB'),
    latC:getInputValueAsFloat('area_latC'), lonC:getInputValueAsFloat('area_lonC'),
    datum:getDatum()
  }), d => `
    <div class="result-success">
      <h4>Área do Triângulo</h4>
      <p><b>Área:</b> ${formatarArea(d.area_m2)}</p>
      <p><b>Perímetro:</b> ${formatarDistancia(d.perimetro_m)}</p>
      <p><b>Datum:</b> ${d.datum_usado}</p>
    </div>`);}
    
/* Azimute ------------------------------------------------------------------ */
function handleAzimute(e){
  handleRequest(e,'/calcular_azimute',()=>({
    lat1:getInputValueAsFloat('azimute_lat1'), lon1:getInputValueAsFloat('azimute_lon1'),
    lat2:getInputValueAsFloat('azimute_lat2'), lon2:getInputValueAsFloat('azimute_lon2'),
    datum:getDatum()
  }), d=>`
    <div class="result-success">
      <h4>Azimute & Distância</h4>
      <p><b>Azimute Direto:</b> ${formatarNumero(d.azimute_direto,4)}°</p>
      <p><b>Distância:</b> ${formatarDistancia(d.distancia_m)}</p>
      <p><b>Datum:</b> ${d.datum_usado}</p>
    </div>`);}
    
/* UTM ---------------------------------------------------------------------- */
function handleUTM(e){
  handleRequest(e,'/calcular_utm',()=>({
    latitude : getInputValueAsFloat('utm_lat'),
    longitude: getInputValueAsFloat('utm_lon'),
    datum    : getDatum()
  }), d=>`
    <div class="result-success">
      <h4>Coordenadas UTM</h4>
      <p><b>Zona:</b> ${d.zona_utm} (${d.fuso})</p>
      <p><b>Hem:</b> ${d.hemisferio}</p>
      <p><b>Easting:</b> ${formatarNumero(d.easting,3)} m</p>
      <p><b>Northing:</b> ${formatarNumero(d.northing,3)} m</p>
      <p><b>EPSG:</b> ${d.epsg_utm}</p>
    </div>`);}
    
/* Novas Coordenadas --------------------------------------------------------- */
function handleNovasCoordenadas(e){
  handleRequest(e,'/calcular_novas_coordenadas',()=>({
    lat : getInputValueAsFloat('novascoords_lat'),
    lon : getInputValueAsFloat('novascoords_lon'),
    distancia: getInputValueAsFloat('novascoords_distancia'),
    azimute  : getInputValueAsFloat('novascoords_azimute'),
    datum    : getDatum()
  }), d=>`
    <div class="result-success">
      <h4>Novas Coordenadas</h4>
      <p><b>Latitude:</b> ${formatarCoordenada(d.lat,8)}</p>
      <p><b>Longitude:</b> ${formatarCoordenada(d.lon,8)}</p>
      <p><b>Azimute Final:</b> ${formatarNumero(d.azimute_final,3)}°</p>
    </div>`);}
    
/* Conversão de Unidades ----------------------------------------------------- */
function handleConversaoUnidades(e){
  handleRequest(e,'/calcular_conversao',()=>({
    valor  : getInputValueAsFloat('valorConversao'),
    origem : getSelectValue('unidadeOrigem'),
    destino: getSelectValue('unidadeDestino')
  }), d=>{
    const nomes = {
      km:'quilômetros', milhas:'milhas', m_nauticas:'milhas náuticas',
      metros:'metros',  pes:'pés',     jardas:'jardas'
    };
    if (!d || d.valor_original==null) return `<div class="result-error">Erro.</div>`;
    return `
      <div class="result-success">
        <h4>Conversão de Unidades</h4>
        <p><b>Valor Original:</b> ${formatarNumero(d.valor_original,4)} ${nomes[d.unidade_origem]||d.unidade_origem}</p>
        <p><b>Resultado:</b> ${formatarNumero(d.resultado,6)} ${nomes[d.unidade_destino]||d.unidade_destino}</p>
      </div>`;}
);}

/* Decimal → DMS ------------------------------------------------------------ */
function handleDecimalParaDMS(e){
  handleRequest(e,'/converter_decimal_para_dms',()=>({
    valorDecimal: getInputValueAsFloat('decimal_input')
  }), d=>`
    <div class="result-success">
      <h4>Decimal → DMS</h4>
      <p><b>Original:</b> ${formatarCoordenada(d.valor_original,8)}°</p>
      <p><b>DMS:</b> ${d.dms_formatado}</p>
    </div>`);}
    
/* DMS → Decimal ------------------------------------------------------------ */
function handleDMSParaDecimal(e){
  handleRequest(e,'/converter_dms_para_decimal',()=>({
    graus   : getInputValueAsFloat('dms_graus'),
    minutos : getInputValueAsFloat('dms_minutos'),
    segundos: getInputValueAsFloat('dms_segundos')
  }), d=>`
    <div class="result-success">
      <h4>DMS → Decimal</h4>
      <p><b>Decimal:</b> ${formatarCoordenada(d.resultado,8)}°</p>
    </div>`);}
    
/* ------------------------- VALIDAÇÃO DE COORDENADAS ------------------------ */
function validarCoordenada(input, tipo){
  const v   = parseFloat(input.value);
  const min = tipo==='latitude' ? -90 : -180;
  const max = tipo==='latitude' ?  90 :  180;
  if (isNaN(v))         input.setCustomValidity('Número inválido.');
  else if (v<min||v>max)input.setCustomValidity(`Deve estar entre ${min} e ${max}.`);
  else                  input.setCustomValidity('');
}

/* ------------------------- REGISTRO DE EVENTOS ---------------------------- */
document.addEventListener('DOMContentLoaded', () => {

  /* Navegação por abas */
  const tabs = document.querySelectorAll('.tab-button');
  const panels = document.querySelectorAll('.calculator-panel');
  tabs.forEach(btn=>{
    btn.addEventListener('click',()=>{
      tabs.forEach(b=>b.classList.remove('active'));
      panels.forEach(p=>p.classList.remove('active'));
      btn.classList.add('active');
      document.getElementById(btn.dataset.tab).classList.add('active');
    });
  });

  /* Helper para vincular botão → handler */
  const link = (sel, fn) => {
    const el = document.querySelector(sel);
    if (el) el.addEventListener('click', fn);
    else    console.warn('Botão não encontrado:', sel);
  };

  link('#distanciaTab        button[data-result]', handleDistancia);
  link('#areaTab             button[data-result]', handleArea);
  link('#azimuteTab          button[data-result]', handleAzimute);
  link('#utmTab              button[data-result]', handleUTM);
  link('#novasCoordenadasTab button[data-result]', handleNovasCoordenadas);
  link('#conversaoUnidadesTab button[data-result]', handleConversaoUnidades);
  link('#btn-decimal-dms[data-result]',  handleDecimalParaDMS);
  link('#btn-dms-decimal[data-result]',  handleDMSParaDecimal);

  /* Validação em tempo real */
  document.querySelectorAll('input[id*="lat"]').forEach(i=>{
    i.addEventListener('input',()=>validarCoordenada(i,'latitude'));});
  document.querySelectorAll('input[id*="lon"]').forEach(i=>{
    i.addEventListener('input',()=>validarCoordenada(i,'longitude'));});
});