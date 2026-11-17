const REPO="timerloggedout-spec/termux-monorepo";
const ORIGIN="https://timerloggedout-spec.github.io";
const cors={"Access-Control-Allow-Origin":ORIGIN,"Access-Control-Allow-Methods":"GET, POST, OPTIONS","Access-Control-Allow-Headers":"Authorization, Content-Type","Access-Control-Max-Age":"86400"};
async function gh(path,token){const r=await fetch("https://api.github.com"+path,{headers:{"Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28","Authorization":"Bearer "+token,"User-Agent":"admin-graph-live"}});if(!r.ok)throw new Error("GitHub verification failed: "+r.status);return r.json();}
export default{async fetch(req,env){
 const u=new URL(req.url);
 if(req.method==="OPTIONS")return new Response(null,{status:204,headers:cors});
 if(u.pathname==="/health"&&req.method==="GET"){const row=await env.EVENTS_DB.prepare("SELECT COUNT(*) AS n, MAX(received_at) AS latest FROM runtime_events").first();return Response.json({ok:true,repo:REPO,...row},{headers:{...cors,"Cache-Control":"no-store"}});}
 if(u.pathname==="/ingest"&&req.method==="POST"){
  const auth=req.headers.get("Authorization")||"",token=auth.startsWith("Bearer ")?auth.slice(7):"";
  if(!token)return new Response("unauthorized",{status:401});
  let body;try{body=await req.json();}catch{return new Response("invalid json",{status:400});}
  const events=Array.isArray(body.events)?body.events:[body.event||body];
  if(!events.length||events.length>100)return new Response("invalid event batch",{status:400});
  try{
   for(const e of events){
    if(e.repo!==REPO||!e.run_id||!e.id||!e.event||!e.status)return new Response("invalid event envelope",{status:400});
    const run=await gh("/repos/"+REPO+"/actions/runs/"+encodeURIComponent(e.run_id),token);
    if(String(run.id)!==String(e.run_id)||run.repository?.full_name!==REPO)return new Response("run does not match repository",{status:403});
    if(e.job_id){const job=await gh("/repos/"+REPO+"/actions/jobs/"+encodeURIComponent(e.job_id),token);if(String(job.run_id)!==String(e.run_id))return new Response("job/run mismatch",{status:403});}
    const workflow=run.name||e.workflow||"GitHub Actions";
    const runStatus=run.status==="completed"?(run.conclusion||"completed"):(run.status||"unknown");
    const runAt=run.updated_at||run.run_started_at||run.created_at||new Date().toISOString();
    const runEventId="workflow:"+run.id+":"+(run.run_attempt||1)+":"+runStatus+":"+runAt;
    await env.EVENTS_DB.prepare("INSERT OR IGNORE INTO runtime_events (id,kind,event,status,workflow,job,step,repo,run_id,run_attempt,job_id,head_sha,url,occurred_at,received_at,payload) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)")
     .bind(runEventId,"workflow","workflow_"+runStatus,runStatus,workflow,null,null,REPO,Number(run.id),Number(run.run_attempt||1),null,run.head_sha||null,run.html_url||null,String(runAt),new Date().toISOString(),JSON.stringify({workflow_path:run.path||null,actor:e.actor||null})).run();
    await env.EVENTS_DB.prepare("INSERT OR IGNORE INTO runtime_events (id,kind,event,status,workflow,job,step,repo,run_id,run_attempt,job_id,head_sha,url,occurred_at,received_at,payload) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)")
     .bind(String(e.id),String(e.kind||"job"),String(e.event),String(e.status),String(workflow),e.job||null,e.step||null,REPO,Number(e.run_id),Number(e.run_attempt||run.run_attempt||1),e.job_id?Number(e.job_id):null,e.head_sha||run.head_sha||null,e.url||run.html_url||null,String(e.occurred_at||new Date().toISOString()),new Date().toISOString(),JSON.stringify({actor:e.actor||null})).run();
   }
   return Response.json({ok:true,accepted:events.length},{headers:{...cors,"Cache-Control":"no-store"}});
  }catch(err){return Response.json({ok:false,error:"verification_or_storage_failed",message:String(err.message||err)},{status:502,headers:cors});}
 }
 if(u.pathname==="/events"&&req.method==="GET"){
  const limit=Math.min(400,Math.max(1,Number(u.searchParams.get("limit")||200)));
  const rows=await env.EVENTS_DB.prepare("SELECT id,kind,event,status,workflow,job,step,repo,run_id,run_attempt,job_id,head_sha,url,occurred_at,received_at FROM runtime_events ORDER BY occurred_at DESC LIMIT ?").bind(limit).all();
  return Response.json({schema:"admin-graph-live-events/v1",source:"GitHub Actions workflow_job observer + API-backed workflow-run reconciler",repo:REPO,generated_at:new Date().toISOString(),poll_hint_ms:5000,events:(rows.results||[]).reverse()},{headers:{...cors,"Cache-Control":"no-store"}});
 }
 return new Response("not found",{status:404});
}};