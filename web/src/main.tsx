import React, {useEffect, useState, type FormEvent, type ReactNode} from 'react';
import {createRoot} from 'react-dom/client';
import {LayoutDashboard, Users, Workflow, BrainCircuit, PanelsTopLeft, RefreshCw, Plus, Search, Download, CheckCircle2, ArrowUpRight, Database, X, Building2, CircleHelp, ShieldCheck} from 'lucide-react';
import './styles.css';

type Row = Record<string, any>;
type Page = 'overview'|'crm'|'pipeline'|'intelligence'|'sectors'|'projects';
type Customer = {id:string;name:string;segment:string;consent:number;frequency:number;monetary_cents:number;recency_days:number|null;audience:string};
type Deal = {id:number;customer_id:string;customer:string;title:string;value_cents:number;stage:string;version:number};
const money=(value:number)=>new Intl.NumberFormat('pt-BR',{style:'currency',currency:'BRL',maximumFractionDigits:0}).format(value/100);
const percent=(value:number)=>new Intl.NumberFormat('pt-BR',{style:'percent',maximumFractionDigits:1}).format(value);
const stages=[{key:'novo',label:'Novo'},{key:'contato',label:'Em contato'},{key:'proposta',label:'Proposta'},{key:'ganho',label:'Ganho'},{key:'perdido',label:'Perdido'}];

async function api<T=Row>(path:string,method='GET',body?:unknown):Promise<T>{
  const response=await fetch('/api'+path,{method,headers:body===undefined?undefined:{'Content-Type':'application/json'},body:body===undefined?undefined:JSON.stringify(body)});
  if(!response.ok){
    let message='Não foi possível concluir a operação.';
    try{const result=await response.json();message=typeof result.detail==='string'?result.detail:JSON.stringify(result.detail)}catch{message='Falha na conexão com a API ('+response.status+').'}
    throw new Error(message);
  }
  return response.json();
}
function useResource<T>(path:string,revision:number){
  const [data,setData]=useState<T|null>(null),[error,setError]=useState(''),[loading,setLoading]=useState(true);
  useEffect(()=>{
    let active=true;setLoading(true);setError('');
    api<T>(path).then(value=>{if(active)setData(value)}).catch(error=>{if(active)setError(error.message)}).finally(()=>{if(active)setLoading(false)});
    return()=>{active=false};
  },[path,revision]);
  return{data,error,loading};
}
function State({loading,error,children}:{loading:boolean;error:string;children:ReactNode}){
  if(loading)return <div className="empty" role="status"><RefreshCw className="spin" size={22}/><p>Carregando dados…</p></div>;
  if(error)return <div className="error" role="alert">{error}</div>;
  return <>{children}</>;
}
function Empty({children}:{children:ReactNode}){return <div className="empty"><Database size={24}/><p>{children}</p></div>}
function Section({title,subtitle,action,children}:{title:string;subtitle?:string;action?:ReactNode;children:ReactNode}){
  return <section className="panel"><header className="section-head"><div><h2>{title}</h2>{subtitle&&<p>{subtitle}</p>}</div>{action}</header>{children}</section>;
}
function Stat({label,value,detail}:{label:string;value:ReactNode;detail?:string}){return <div className="stat"><span>{label}</span><strong>{value}</strong>{detail&&<small>{detail}</small>}</div>}
function Table({headers,children}:{headers:string[];children:ReactNode}){return <div className="table-wrap"><table><thead><tr>{headers.map(header=><th key={header}>{header}</th>)}</tr></thead><tbody>{children}</tbody></table></div>}
function Badge({children,tone='neutral'}:{children:ReactNode;tone?:string}){return <span className={'badge '+tone}>{children}</span>}
function Modal({title,close,children}:{title:string;close:()=>void;children:ReactNode}){
  const element=React.useRef<HTMLDivElement>(null);
  useEffect(()=>{
    const previous=document.activeElement as HTMLElement|null;
    const candidates=()=>Array.from(element.current?.querySelectorAll<HTMLElement>('button,input,select,textarea,a[href]')??[]).filter(item=>!item.hasAttribute('disabled'));
    candidates()[0]?.focus();
    function trap(event:KeyboardEvent){
      if(event.key==='Escape')close();
      if(event.key==='Tab'){const items=candidates(),first=items[0],last=items[items.length-1];if(event.shiftKey&&document.activeElement===first){event.preventDefault();last?.focus()}else if(!event.shiftKey&&document.activeElement===last){event.preventDefault();first?.focus()}}
    }
    document.addEventListener('keydown',trap);
    return()=>{document.removeEventListener('keydown',trap);previous?.focus()};
  },[]);
  return <div className="modal-overlay"><div ref={element} className="modal" role="dialog" aria-modal="true" aria-label={title}><header><h2>{title}</h2><button className="icon-button" aria-label="Fechar" onClick={close}><X size={20}/></button></header>{children}</div></div>;
}
function Overview({revision,navigate}:{revision:number;navigate:(page:Page)=>void}){
  const summary=useResource<Row>('/overview',revision),reconciliation=useResource<Row>('/reconcile',revision),scores=useResource<Row[]>('/lead-scores',revision);
  return <State loading={summary.loading} error={summary.error}>{summary.data&&<>
    <div className="intro"><div><span className="eyebrow">Visão de negócio</span><h1>Dados que movem<br/>o relacionamento.</h1><p>Acompanhe a receita, priorize clientes e confira a qualidade da operação em um só lugar.</p></div><div className="intro-note"><ShieldCheck size={28}/><strong>Ambiente demonstrativo</strong><span>Dados sintéticos e regras explícitas.<br/>Referência em {summary.data.as_of}.</span></div></div>
    <div className="stats"><Stat label="Receita acumulada" value={money(summary.data.revenue_cents)} detail="Pedidos até a data de referência"/><Stat label="Clientes na base" value={summary.data.customers} detail="Visão consolidada"/><Stat label="Elegíveis à reativação" value={summary.data.reactivation} detail="Com consentimento de contato"/><Stat label="Conciliação" value={reconciliation.loading?'…':reconciliation.error?'Indisponível':reconciliation.data?.balanced?'Consistente':'Revisar'} detail="Origem × agregado"/></div>
    <div className="two-columns"><Section title="Evolução da receita" subtitle="Total mensal dos pedidos">{summary.data.monthly.length?<div className="chart" role="img" aria-label="Receita por mês">{summary.data.monthly.map((month:Row)=>{
      const max=Math.max(...summary.data!.monthly.map((item:Row)=>item.revenue_cents),1);
      return <div className="bar-column" key={month.month}><span className="bar-value">{money(month.revenue_cents)}</span><div className="bar-track"><div className="bar" style={{height:Math.max(2,month.revenue_cents/max*100)+'%'}}/></div><span>{month.month.slice(5)}/{month.month.slice(2,4)}</span></div>;
    })}</div>:<Empty>Importe pedidos para visualizar a receita.</Empty>}</Section>
    <Section title="Prioridades comerciais" subtitle="Pontuação por regras transparentes" action={<button className="text-button" onClick={()=>navigate('crm')}>Abrir CRM <ArrowUpRight size={16}/></button>}><State loading={scores.loading} error={scores.error}>{scores.data?.length?<ol className="priority-list">{scores.data.slice(0,5).map(item=><li key={item.id}><span className="avatar">{item.name.slice(-2)}</span><div><strong>{item.name}</strong><small>{item.reasons.join(' · ')}</small></div><span className="score">{item.score}</span></li>)}</ol>:<Empty>Cadastre clientes para começar.</Empty>}</State></Section></div>
    <div className="next-actions"><button onClick={()=>navigate('pipeline')}><Workflow/><span><strong>Conferir os dados</strong><small>Importação, validação e histórico</small></span><ArrowUpRight/></button><button onClick={()=>navigate('intelligence')}><BrainCircuit/><span><strong>Investigar com fontes</strong><small>Busca, métricas e revisão de alertas</small></span><ArrowUpRight/></button></div>
  </>}</State>;
}
function CRM({revision,refresh,notify}:{revision:number;refresh:()=>void;notify:(text:string)=>void}){
  const people=useResource<Customer[]>('/customers',revision),deals=useResource<Deal[]>('/deals',revision);
  const [tab,setTab]=useState('customers'),[query,setQuery]=useState(''),[audience,setAudience]=useState('');
  const [modal,setModal]=useState<'customer'|'deal'|null>(null),[busy,setBusy]=useState(false),[error,setError]=useState('');
  const filtered=people.data?.filter(item=>(item.name+' '+item.id).toLocaleLowerCase().includes(query.toLocaleLowerCase())&&(!audience||item.audience===audience))??[];
  async function save(event:FormEvent<HTMLFormElement>){
    event.preventDefault();setBusy(true);setError('');
    const form=new FormData(event.currentTarget);
    try{
      if(modal==='customer')await api('/customers','POST',{id:form.get('id'),name:form.get('name'),segment:form.get('segment'),consent:form.get('consent')==='on'});
      else await api('/deals','POST',{customer_id:form.get('customer_id'),title:form.get('title'),value_cents:Math.round(Number(form.get('value'))*100)});
      notify(modal==='customer'?'Cliente cadastrado.':'Oportunidade criada.');setModal(null);refresh();
    }catch(error){setError((error as Error).message)}finally{setBusy(false)}
  }
  async function move(deal:Deal,stage:string){
    setBusy(true);setError('');
    try{await api('/deals/'+deal.id,'PATCH',{stage,version:deal.version});refresh();notify('Etapa atualizada.')}catch(error){setError((error as Error).message);refresh()}finally{setBusy(false)}
  }
  async function prepare(){
    setBusy(true);setError('');
    try{const result=await api('/campaigns/prepare','POST');notify(result.added+' clientes adicionados à fila de revisão. Nenhuma mensagem enviada.');refresh()}catch(error){setError((error as Error).message)}finally{setBusy(false)}
  }
  return <>
    <div className="page-title"><div><h1>Relacionamento com clientes</h1><p>Organize o funil e transforme comportamento em prioridades.</p></div><button className="primary" onClick={()=>{setError('');setModal(tab==='customers'?'customer':'deal')}}><Plus size={17}/>{tab==='customers'?'Novo cliente':'Nova oportunidade'}</button></div>
    <div className="tabs" role="tablist" aria-label="Visões do CRM">{[['customers','Clientes e segmentos'],['deals','Funil comercial'],['campaigns','Reativação']].map(([key,label])=><button role="tab" aria-selected={tab===key} className={tab===key?'active':''} key={key} onClick={()=>setTab(key)}>{label}</button>)}</div>
    {error&&!modal&&<div className="error" role="alert">{error}</div>}
    <State loading={people.loading||deals.loading} error={people.error||deals.error}>
    {tab==='customers'&&<Section title="Base de clientes" subtitle={filtered.length+' clientes encontrados'} action={<a className="secondary" href="/api/export/customers"><Download size={16}/>Exportar métricas</a>}>
      <div className="filters"><label className="search-field"><Search size={18}/><input aria-label="Buscar clientes" value={query} onChange={event=>setQuery(event.target.value)} placeholder="Buscar nome ou identificador"/></label><select aria-label="Filtrar público" value={audience} onChange={event=>setAudience(event.target.value)}><option value="">Todos os públicos</option>{['Reativação','Recorrente','Acompanhamento','Sem compras','Sem consentimento'].map(value=><option key={value}>{value}</option>)}</select></div>
      {filtered.length?<Table headers={['Cliente','Setor','Compras','Última compra','Receita','Público']}>{filtered.map(item=><tr key={item.id}><td><strong>{item.name}</strong><small>{item.id}</small></td><td>{item.segment}</td><td>{item.frequency}</td><td>{item.recency_days===null?'Sem histórico':item.recency_days+' dias'}</td><td className="numeric">{money(item.monetary_cents)}</td><td><Badge tone={item.audience==='Reativação'?'amber':item.audience==='Recorrente'?'teal':'neutral'}>{item.audience}</Badge></td></tr>)}</Table>:<Empty>Nenhum cliente corresponde aos filtros.</Empty>}
    </Section>}
    {tab==='deals'&&<div className="kanban">{stages.map(stage=>{
      const cards=deals.data?.filter(deal=>deal.stage===stage.key)??[];
      return <section className={'lane lane-'+stage.key} key={stage.key}><header><h2>{stage.label}</h2><span>{cards.length}</span></header><p className="lane-total">{money(cards.reduce((total,item)=>total+item.value_cents,0))}</p>{cards.map(deal=><article className="deal" key={deal.id}><small>{deal.customer}</small><h3>{deal.title}</h3><strong>{money(deal.value_cents)}</strong><label>Etapa<select value={deal.stage} disabled={busy} onChange={event=>move(deal,event.target.value)}>{stages.map(stage=><option value={stage.key} key={stage.key}>{stage.label}</option>)}</select></label></article>)}{!cards.length&&<p className="lane-empty">Sem oportunidades nesta etapa.</p>}</section>;
    })}</div>}
    {tab==='campaigns'&&<><Section title="Audiência de reativação" subtitle="Pelo menos duas compras, recência a partir de 60 dias e consentimento." action={<button className="primary" disabled={busy} onClick={prepare}>{busy?'Preparando…':'Preparar para revisão'}</button>}><p className="callout">A preparação cria uma fila idempotente de revisão. Este ambiente demonstra a seleção do público e não realiza disparos.</p><Table headers={['Cliente','Última compra','Compras','Receita acumulada']}>{people.data?.filter(person=>person.audience==='Reativação').map(person=><tr key={person.id}><td>{person.name}</td><td>{person.recency_days} dias</td><td>{person.frequency}</td><td>{money(person.monetary_cents)}</td></tr>)}</Table></Section><CampaignQueue revision={revision}/></>}
    </State>
    {modal&&<Modal title={modal==='customer'?'Cadastrar cliente':'Criar oportunidade'} close={()=>setModal(null)}><form onSubmit={save} className="form-stack">
      {modal==='customer'?<><label>Identificador<input name="id" required pattern="[A-Za-z0-9_-]{1,32}" maxLength={32} placeholder="Ex.: C041"/></label><label>Nome<input name="name" required minLength={2} maxLength={100}/></label><label>Setor<select name="segment"><option>Serviços</option><option>Comércio</option><option>Tecnologia</option></select></label><label className="checkbox"><input name="consent" type="checkbox"/>Possui consentimento de contato</label></>:<><label>Cliente<select name="customer_id" required><option value="">Selecione um cliente</option>{people.data?.map(person=><option key={person.id} value={person.id}>{person.name}</option>)}</select></label><label>Oportunidade<input name="title" minLength={2} maxLength={100} required/></label><label>Valor em reais<input name="value" type="number" min="0" max="100000000" step="0.01" required/></label></>}
      {error&&<p className="error" role="alert">{error}</p>}<button className="primary" disabled={busy}>{busy?'Salvando…':'Salvar'}</button>
    </form></Modal>}
  </>;
}
function CampaignQueue({revision}:{revision:number}){const result=useResource<Row[]>('/campaigns',revision);return <Section title="Fila de revisão"><State loading={result.loading} error={result.error}>{result.data?.length?<Table headers={['Cliente','Campanha','Situação']}>{result.data.map(row=><tr key={row.customer_id+row.campaign}><td>{row.customer_id}</td><td>{row.campaign}</td><td><Badge tone="amber">Pendente de revisão</Badge></td></tr>)}</Table>:<Empty>A fila está vazia. Prepare a audiência acima.</Empty>}</State></Section>}
function Pipeline({revision,refresh,notify}:{revision:number;refresh:()=>void;notify:(message:string)=>void}){
  const operations=useResource<Row>('/operations',revision),reconcile=useResource<Row>('/reconcile',revision);
  const [content,setContent]=useState(''),[result,setResult]=useState<Row|null>(null),[busy,setBusy]=useState(false),[error,setError]=useState('');
  async function run(mode:'validate'|'run'){
    setBusy(true);setError('');setResult(null);
    try{const result=await api('/pipeline/'+mode,'POST',{content});setResult(result);if(mode==='run'){refresh();notify('Carga concluída. Confira o resultado das validações.')}}catch(error){setError((error as Error).message)}finally{setBusy(false)}
  }
  return <><div className="page-title"><div><h1>Qualidade e operação</h1><p>Valide a entrada, acompanhe as cargas e concilie os resultados.</p></div></div>
    <div className="two-columns"><Section title="Importação de pedidos" subtitle="CSV com identificador, cliente, data, valor e versão"><div className="form-stack padded"><label>Arquivo CSV<input type="file" accept=".csv,text/csv" onChange={async event=>{const file=event.target.files?.[0];if(!file)return;if(file.size>1_000_000){setError('O arquivo deve ter até 1 MB.');return}setContent(await file.text());setResult(null);setError('')}}/></label><label>Conteúdo<textarea rows={8} value={content} onChange={event=>{setContent(event.target.value);setResult(null)}} placeholder={'id,customer_id,day,amount,version\nPEDIDO-DEMO,C001,2026-11-17,150.00,1'} maxLength={1_000_000}/></label><p className="hint">Versões maiores atualizam pedidos existentes. Linhas rejeitadas aparecem com o motivo.</p><div className="button-row"><button className="secondary" disabled={busy||!content.trim()} onClick={()=>run('validate')}>Validar CSV</button><button className="primary" disabled={busy||!content.trim()} onClick={()=>run('run')}>{busy?'Processando…':'Executar carga'}</button></div>{error&&<div className="error" role="alert">{error}</div>}{result&&<div aria-live="polite"><div className="result-line"><Badge tone="teal">{result.accepted} aceitas</Badge><Badge tone={result.rejected?'amber':'neutral'}>{result.rejected} rejeitadas</Badge>{result.changed!==undefined&&<Badge>{result.changed} alteradas</Badge>}</div>{result.errors?.length>0&&<ul className="validation-list">{result.errors.map((item:Row,index:number)=><li key={index}>Linha {item.line}: {item.reason}</li>)}</ul>}</div>}</div></Section>
    <Section title="Conciliação de receita" subtitle="Conferência entre registros e agregação por cliente"><State loading={reconcile.loading} error={reconcile.error}>{reconcile.data&&<div className="reconciliation"><div className={'reconcile-icon '+(reconcile.data.balanced?'good':'')}><ShieldCheck size={38}/></div><h3>{reconcile.data.balanced?'Valores conciliados':'Divergência encontrada'}</h3><dl><dt>Total da origem</dt><dd>{money(reconcile.data.source_cents)}</dd><dt>Total agregado</dt><dd>{money(reconcile.data.aggregate_cents)}</dd><dt>Diferença</dt><dd>{money(reconcile.data.difference_cents)}</dd><dt>Pedidos</dt><dd>{reconcile.data.orders}</dd></dl></div>}</State></Section></div>
    <Section title="Histórico de cargas"><State loading={operations.loading} error={operations.error}>{operations.data?.runs.length?<Table headers={['Execução','Recebidas','Aceitas','Rejeitadas','Alteradas','Duração']}>{operations.data.runs.map((run:Row)=><tr key={run.id}><td>#{run.id}<small>{run.created_at}</small></td><td>{run.input_rows}</td><td>{run.accepted}</td><td>{run.rejected}</td><td>{run.changed}</td><td>{run.elapsed_ms} ms</td></tr>)}</Table>:<Empty>Nenhuma carga executada.</Empty>}</State></Section>
    <Section title="Trilha de alterações"><State loading={operations.loading} error={operations.error}>{operations.data?.audit.length?<Table headers={['Quando','Ação','Detalhe']}>{operations.data.audit.map((entry:Row)=><tr key={entry.id}><td>{entry.created_at}</td><td>{entry.action}</td><td><code>{entry.detail}</code></td></tr>)}</Table>:<Empty>Nenhuma alteração registrada.</Empty>}</State></Section>
  </>;
}
function Intelligence({revision}:{revision:number}){
  const [question,setQuestion]=useState(''),[result,setResult]=useState<Row|null>(null),[trace,setTrace]=useState<Row|null>(null),[error,setError]=useState(''),[busy,setBusy]=useState(false);
  const evaluations=useResource<Row>('/evaluations',revision),anomalies=useResource<Row>('/anomalies',revision);
  async function submit(event:FormEvent){event.preventDefault();setBusy(true);setError('');setTrace(null);try{setResult(await api('/search','POST',{question}))}catch(error){setError((error as Error).message)}finally{setBusy(false)}}
  async function investigate(){setBusy(true);setError('');try{setTrace(await api('/investigate','POST',{question}))}catch(error){setError((error as Error).message)}finally{setBusy(false)}}
  return <><div className="page-title"><div><h1>Engenharia de IA</h1><p>Recuperação com fontes, avaliação reproduzível e alertas para revisão.</p></div></div>
    <Section title="Consultar regras da operação" subtitle="Busca lexical TF-IDF na documentação de demonstração"><form className="search-form" onSubmit={submit}><label className="search-field"><Search size={20}/><input aria-label="Pergunta sobre a operação" minLength={3} maxLength={500} required value={question} onChange={event=>setQuestion(event.target.value)} placeholder="Como funciona a carga incremental?"/></label><button className="primary" disabled={busy||question.trim().length<3}>{busy?'Consultando…':'Buscar fontes'}</button><button type="button" className="secondary" disabled={busy||question.trim().length<3} onClick={investigate}>Investigar dados</button></form>{error&&<div className="error" role="alert">{error}</div>}
    {result&&<div className="search-results"><p className="hint">{result.matches.length} trechos · {result.elapsed_ms} ms · {result.method}</p>{result.matches.length?result.matches.map((item:Row)=><article key={item.id}><header><Badge>{item.source}</Badge><small>Similaridade {item.score.toFixed(3)}</small></header><p>{item.text}</p></article>):<Empty>Nenhum trecho relevante. Tente palavras como consentimento, carga, anomalia ou reativação.</Empty>}</div>}
    {trace&&<div className="padded"><h3>{trace.conclusion}</h3><p className="hint">Fluxo determinístico com ferramentas de conciliação, indicadores e busca.</p>{trace.steps.map((step:Row)=><details key={step.tool}><summary>{step.tool}</summary><pre>{JSON.stringify(step.result,null,2)}</pre></details>)}</div>}</Section>
    <div className="two-columns"><Section title="Avaliação de recuperação" subtitle="Recall@3 e posição da fonte esperada"><State loading={evaluations.loading} error={evaluations.error}>{evaluations.data&&<><div className="mini-stats"><Stat label="Recall@3" value={percent(evaluations.data.recall_at_3)}/><Stat label="MRR" value={evaluations.data.mrr.toFixed(2)}/></div><Table headers={['Pergunta','Fonte','Posição']}>{evaluations.data.cases.map((item:Row)=><tr key={item.question}><td>{item.question}</td><td>{item.expected}</td><td>{item.rank??'Não recuperada'}</td></tr>)}</Table><p className="hint padded">{evaluations.data.scope}</p></>}</State></Section>
    <Section title="Pedidos para revisão" subtitle="Detecção por Isolation Forest sobre valores"><State loading={anomalies.loading} error={anomalies.error}>{anomalies.data?.items.length?<><Table headers={['Pedido','Valor','Score']}>{anomalies.data.items.map((item:Row)=><tr key={item.id}><td>{item.id}</td><td>{money(item.amount_cents)}</td><td>{item.score}</td></tr>)}</Table><p className="hint padded">O alerta indica comportamento incomum. A classificação exige análise humana e contexto de negócio.</p></>:<Empty>{anomalies.data?.status==='insufficient_data'?'São necessários pelo menos dez pedidos.':'Nenhum alerta encontrado.'}</Empty>}</State></Section></div>
  </>;
}
function Sectors({revision}:{revision:number}){
  const procurement=useResource<Row[]>('/procurement',revision),workforce=useResource<Row[]>('/workforce',revision),forecast=useResource<Row>('/forecast',revision),cohorts=useResource<Row[]>('/cohorts',revision);
  const groups=[...new Set(cohorts.data?.map(row=>row.cohort)??[])];
  return <><div className="page-title"><div><h1>Análises por área</h1><p>Compras, pessoas, receita e retenção com dados sintéticos.</p></div></div>
    <div className="two-columns"><Section title="Compras e fornecedores" subtitle="Concentração de gastos e entregas no prazo"><State loading={procurement.loading} error={procurement.error}><Table headers={['Fornecedor','Gastos','Participação','No prazo']}>{procurement.data?.map(row=><tr key={row.supplier}><td>{row.supplier}</td><td>{money(row.spend_cents)}</td><td>{percent(row.share)}</td><td>{percent(row.on_time_rate)}</td></tr>)}</Table></State></Section>
    <Section title="Pessoas e capacidade" subtitle="Indicadores agregados por departamento"><State loading={workforce.loading} error={workforce.error}><Table headers={['Área','Pessoas','Custo','Ausência']}>{workforce.data?.map(row=><tr key={row.department}><td>{row.department}</td><td>{row.people}</td><td>{money(row.cost_cents)}</td><td>{percent(row.absence_rate)}</td></tr>)}</Table></State></Section></div>
    <div className="two-columns"><Section title="Retenção por coorte" subtitle="Clientes ativos por mês desde a primeira compra"><State loading={cohorts.loading} error={cohorts.error}>{groups.length?<div className="cohorts"><div className="cohort-head"><span>Coorte</span><span>Retenção nos meses observados</span></div>{groups.map(group=><div className="cohort-row" key={group}><strong>{group}</strong><div>{cohorts.data?.filter(row=>row.cohort===group).map(row=><span key={row.month_index} title={'Mês '+row.month_index+': '+row.active+' de '+row.size+' clientes'} style={{background:'rgba(20,116,112,'+(0.08+row.retention*0.75)+')',color:row.retention>.6?'white':'#183c48'}}>{percent(row.retention)}</span>)}</div></div>)}</div>:<Empty>Sem histórico para coortes.</Empty>}</State></Section>
    <Section title="Referência de receita" subtitle="Projeção por média móvel e erro histórico"><State loading={forecast.loading} error={forecast.error}>{forecast.data?.status==='insufficient_history'?<Empty>São necessários pelo menos quatro meses completos.</Empty>:forecast.data&&<div className="padded"><div className="mini-stats"><Stat label="Próximo mês completo" value={money(forecast.data.next_month_cents)}/><Stat label="Erro médio absoluto" value={money(forecast.data.backtest_mae_cents)}/></div><p>{forecast.data.method}</p><p className="hint">{forecast.data.backtest_points} pontos de backtest. Referência calculada com dados sintéticos, sujeita a revisão de negócio.</p></div>}</State></Section></div>
  </>;
}
function Projects({revision}:{revision:number}){
  const projects=useResource<Row[]>('/projects',revision),[query,setQuery]=useState('');
  const filtered=projects.data?.filter(item=>JSON.stringify(item).toLocaleLowerCase().includes(query.toLocaleLowerCase()))??[];
  return <><div className="page-title"><div><h1>Projetos do portfólio</h1><p>Explore os casos, as ferramentas e os pontos de entrada da implementação.</p></div><label className="search-field"><Search size={18}/><input aria-label="Buscar projetos" placeholder="Buscar projeto ou tecnologia" value={query} onChange={event=>setQuery(event.target.value)}/></label></div>
    <State loading={projects.loading} error={projects.error}>{filtered.length?<div className="project-grid">{filtered.map((item,index)=><article className="project" key={item.id??index}><div><Badge>{item.domain??item.category??'Dados e tecnologia'}</Badge></div><h2>{item.title??item.name}</h2><p>{item.description??item.problem}</p><div className="tags">{(item.tools??item.stack??[]).map((tool:string)=><span key={tool}>{tool}</span>)}</div>{item.endpoint&&<code>{item.endpoint}</code>}{item.status&&<small>{item.status}</small>}</article>)}</div>:<Empty>Nenhum projeto corresponde à busca.</Empty>}</State>
  </>;
}
const navigation=[{key:'overview',label:'Visão geral',icon:LayoutDashboard},{key:'crm',label:'Clientes e CRM',icon:Users},{key:'pipeline',label:'Qualidade e operação',icon:Workflow},{key:'intelligence',label:'Engenharia de IA',icon:BrainCircuit},{key:'sectors',label:'Análises por área',icon:Building2},{key:'projects',label:'Projetos',icon:PanelsTopLeft}] as const;
function App(){
  const [page,setPage]=useState<Page>('overview'),[revision,setRevision]=useState(0),[notice,setNotice]=useState('');
  const refresh=()=>setRevision(value=>value+1);
  useEffect(()=>{if(!notice)return;const timer=setTimeout(()=>setNotice(''),7000);return()=>clearTimeout(timer)},[notice]);
  const props={revision,refresh,notify:setNotice};
  return <div className="shell"><aside className="sidebar"><a className="brand" href="#" onClick={event=>{event.preventDefault();setPage('overview')}}><span className="brand-mark"><Database size={23}/></span><span>Customer Data<strong>Workbench</strong></span></a><div className="workspace"><span className="workspace-avatar">MD</span><span>Michael Douglas<small>Portfólio de engenharia</small></span></div><nav aria-label="Navegação principal">{navigation.map(item=>{const Icon=item.icon;return <button aria-current={page===item.key?'page':undefined} key={item.key} className={page===item.key?'selected':''} onClick={()=>setPage(item.key)}><Icon size={19}/>{item.label}</button>})}</nav><div className="sidebar-bottom"><Badge tone="dark">Dados sintéticos</Badge><p>Ambiente local de demonstração com regras de negócio verificáveis.</p><a href="/docs" target="_blank" rel="noreferrer"><CircleHelp size={17}/>Documentação da API</a></div></aside><div className="main"><header className="topbar"><span>{navigation.find(item=>item.key===page)?.label}</span><div><span className="live-dot"/>Ambiente de demonstração<button className="icon-button" onClick={refresh} title="Atualizar dados" aria-label="Atualizar dados"><RefreshCw size={18}/></button></div></header><main id="main-content">
    {notice&&<div className="toast" role="status"><CheckCircle2 size={18}/>{notice}<button onClick={()=>setNotice('')} aria-label="Fechar aviso"><X size={17}/></button></div>}
    {page==='overview'&&<Overview revision={revision} navigate={setPage}/>}
    {page==='crm'&&<CRM {...props}/>}
    {page==='pipeline'&&<Pipeline {...props}/>}
    {page==='intelligence'&&<Intelligence revision={revision}/>}
    {page==='sectors'&&<Sectors revision={revision}/>}
    {page==='projects'&&<Projects revision={revision}/>}
  </main><footer>Michael Douglas · Engenharia de dados, BI e aplicações de negócio<span>Dados de demonstração</span></footer></div></div>;
}
createRoot(document.getElementById('root')!).render(<React.StrictMode><App/></React.StrictMode>);
