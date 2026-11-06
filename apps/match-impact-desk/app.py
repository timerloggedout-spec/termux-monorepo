"""Match Impact Desk: deterministic three-way AP matching + human approval."""
from __future__ import annotations
import hashlib, json, os, secrets, sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from decimal import Decimal
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parent
STATIC=ROOT/"static"
DB=Path(os.environ.get("MATCHDESK_DB",ROOT/"data"/"matchdesk.sqlite3"))
HOST=os.environ.get("MATCHDESK_HOST","127.0.0.1")
PORT=int(os.environ.get("MATCHDESK_PORT","8080"))
ENV=os.environ.get("MATCHDESK_ENV","development")
TOKEN=os.environ.get("MATCHDESK_ADMIN_TOKEN","")
SEED=[
{"case_id":"MID-2401","payment_batch":"PAY-2026-11-07-A","invoice":{"number":"INV-ACME-1042","vendor":"Acme Industrial Supply","vendor_id":"V-ACME","lines":[{"sku":"BRG-440","description":"Industrial bearing assembly","qty":10,"price":"115.00"},{"sku":"SEAL-12","description":"Sealing kit","qty":5,"price":"42.00"}]},"po":{"number":"PO-7781","revision":2,"lines":[{"sku":"BRG-440","qty":10,"price":"115.00"},{"sku":"SEAL-12","qty":5,"price":"42.00"}]},"receipt":{"number":"GR-7781-01","lines":[{"sku":"BRG-440","qty":10},{"sku":"SEAL-12","qty":5}]}},
{"case_id":"MID-2402","payment_batch":"PAY-2026-11-07-A","invoice":{"number":"INV-NORTH-8821","vendor":"Northstar Components","vendor_id":"V-NORTH","lines":[{"sku":"MTR-220","description":"Servo motor, 2.2kW","qty":10,"price":"120.00"},{"sku":"DRV-80","description":"Drive controller","qty":2,"price":"340.00"}]},"po":{"number":"PO-7781-N","revision":2,"amendment":"Revision 2 reduced MTR-220 price from 120.00 to 115.00.","lines":[{"sku":"MTR-220","qty":10,"price":"115.00"},{"sku":"DRV-80","qty":2,"price":"340.00"}]},"receipt":{"number":"GR-7781-N-01","lines":[{"sku":"MTR-220","qty":10},{"sku":"DRV-80","qty":2}]}},
{"case_id":"MID-2403","payment_batch":"PAY-2026-11-07-B","invoice":{"number":"INV-ACME-1042-COPY","duplicate_of":"INV-ACME-1042","vendor":"Acme Industrial Supply","vendor_id":"V-ACME","lines":[{"sku":"BRG-440","description":"Industrial bearing assembly","qty":10,"price":"115.00"}]},"po":{"number":"PO-7781","revision":2,"lines":[{"sku":"BRG-440","qty":10,"price":"115.00"}]},"receipt":{"number":"GR-7781-01","lines":[{"sku":"BRG-440","qty":10}]}},
{"case_id":"MID-2404","payment_batch":"PAY-2026-11-07-B","invoice":{"number":"INV-DELTA-5510","vendor":"Delta Fabrication","vendor_id":"V-DELTA","lines":[{"sku":"PLT-09","description":"Precision steel plate","qty":12,"price":"200.00"}]},"po":{"number":"PO-8810","revision":1,"lines":[{"sku":"PLT-09","qty":12,"price":"200.00"}]},"receipt":{"number":"GR-8810-01","lines":[{"sku":"PLT-09","qty":8}]}}
]

def utcnow(): return datetime.now(timezone.utc).isoformat(timespec="seconds")
def db_connect():
    DB.parent.mkdir(parents=True,exist_ok=True)
    db=sqlite3.connect(DB,timeout=10); db.row_factory=sqlite3.Row
    db.execute("PRAGMA journal_mode=WAL"); db.execute("PRAGMA foreign_keys=ON")
    return db
@contextmanager
def db_session():
    db=db_connect()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def money(v): return Decimal(str(v)).quantize(Decimal("0.01"))

def analyze(case):
    inv,po,gr=case["invoice"],case["po"],case["receipt"]
    po_lines={x["sku"]:x for x in po["lines"]}; gr_lines={x["sku"]:x for x in gr["lines"]}
    exceptions=[]; lines=[]; variance=Decimal("0"); shortage_value=Decimal("0")
    if inv.get("duplicate_of"):
        exceptions.append({"code":"DUPLICATE_INVOICE","severity":"critical","message":"Invoice duplicates an existing vendor invoice.","evidence":[inv["number"],inv["duplicate_of"]],"action":"Block duplicate payable and link to original."})
    for line in inv["lines"]:
        p,r=po_lines.get(line["sku"]),gr_lines.get(line["sku"])
        if not p or not r:
            exceptions.append({"code":"MISSING_REFERENCE_LINE","severity":"high","message":line["sku"]+" missing from PO or receipt.","evidence":[line["sku"]],"action":"Hold until source evidence is reconciled."})
            lines.append({"sku":line["sku"],"description":line.get("description",""),"status":"exception","qty":line["qty"],"received":None,"po_price":None,"price":line["price"],"variance":None}); continue
        q=Decimal(str(line["qty"])); received=Decimal(str(r["qty"])); price=money(line["price"]); po_price=money(p["price"]); delta=money((price-po_price)*q); status="matched"
        if q>received or q>Decimal(str(p["qty"])):
            status="exception"; missing=max(q-received,q-Decimal(str(p["qty"])),Decimal("0")); shortage_value+=money(missing*price)
            exceptions.append({"code":"QUANTITY_OVER_RECEIPT","severity":"high","message":line["sku"]+": invoice quantity exceeds received or authorized quantity.","evidence":["invoice="+str(q),"received="+str(received),"po="+str(p["qty"])],"action":"Hold disputed quantity; request receipt correction or vendor credit."})
        if abs(delta)>Decimal("0.01"):
            status="exception"; variance+=delta
            exceptions.append({"code":"UNIT_PRICE_VARIANCE","severity":"high" if delta>0 else "medium","message":line["sku"]+": invoice price differs from current PO revision.","evidence":["invoice="+str(price),"po="+str(po_price),"quantity="+str(q),"variance="+str(delta)],"action":"Request a credit memo or confirm the PO amendment."})
        lines.append({"sku":line["sku"],"description":line.get("description",""),"status":status,"qty":str(q),"received":str(received),"po_price":str(po_price),"price":str(price),"variance":str(delta)})
    total=money(sum((money(x["price"])*Decimal(str(x["qty"])) for x in inv["lines"]),Decimal("0")))
    duplicate=bool(inv.get("duplicate_of"))
    if duplicate: recommendation,disposition="Block duplicate payable; retain the original invoice as the payable source.","block"
    elif any(x["code"]=="QUANTITY_OVER_RECEIPT" for x in exceptions): recommendation,disposition="Hold the disputed quantity until receipt evidence is corrected.","hold"
    elif any(x["code"]=="UNIT_PRICE_VARIANCE" for x in exceptions): recommendation,disposition="Request a "+str(abs(variance))+" credit memo; approve only the undisputed amount.","credit_memo"
    elif exceptions: recommendation,disposition="Route missing reference evidence to the controller.","hold"
    else: recommendation,disposition="Three-way match passed; eligible for controller approval.","approve"
    exposure=total if duplicate else money(max(variance,Decimal("0"))+shortage_value)
    impact={"severity":"critical" if duplicate else "high" if shortage_value else "medium" if exceptions else "low","exposure":str(exposure),"basis":"full invoice value at duplicate risk" if duplicate else "price variance plus unreceived quantity" if exceptions else "no exception exposure","affected":[{"type":"invoice","id":inv["number"]},{"type":"purchase_order","id":po["number"]},{"type":"goods_receipt","id":gr["number"]},{"type":"vendor","id":inv["vendor_id"]},{"type":"payment_batch","id":case["payment_batch"]}],"blocked":["payment_release","ledger_posting","vendor_remittance"]}
    return {"invoice_total":str(total),"line_results":lines,"exceptions":exceptions,"exception_count":len(exceptions),"match_status":"exception" if exceptions else "matched","recommendation":recommendation,"disposition":disposition,"impact":impact}

def validate_case(case):
    import re
    if not isinstance(case,dict): raise ValueError("case must be an object")
    for key in ("case_id","payment_batch","invoice","po","receipt"):
        if key not in case: raise ValueError("missing case field: "+key)
    if not re.fullmatch(r"[A-Z0-9-]{3,48}",str(case["case_id"])): raise ValueError("invalid case_id")
    inv,po,gr=case["invoice"],case["po"],case["receipt"]
    if not all(isinstance(x,dict) for x in (inv,po,gr)): raise ValueError("invoice, po and receipt must be objects")
    for key in ("number","vendor","vendor_id","lines"):
        if key not in inv: raise ValueError("invoice missing "+key)
    for key in ("number","revision","lines"):
        if key not in po: raise ValueError("purchase order missing "+key)
    for key in ("number","lines"):
        if key not in gr: raise ValueError("goods receipt missing "+key)
    if not isinstance(inv["lines"],list) or not inv["lines"] or not isinstance(po["lines"],list) or not isinstance(gr["lines"],list): raise ValueError("document lines must be non-empty arrays")
    for line in inv["lines"]:
        if not all(k in line for k in ("sku","qty","price")): raise ValueError("invoice line needs sku, qty and price")
        if Decimal(str(line["qty"]))<=0 or money(line["price"])<0: raise ValueError("invalid invoice quantity or price")
    for line in po["lines"]:
        if not all(k in line for k in ("sku","qty","price")): raise ValueError("PO line needs sku, qty and price")
        if Decimal(str(line["qty"]))<=0 or money(line["price"])<0: raise ValueError("invalid PO quantity or price")
    for line in gr["lines"]:
        if not all(k in line for k in ("sku","qty")) or Decimal(str(line["qty"]))<0: raise ValueError("invalid receipt line")
    return case

def audit_append(db,cid,kind,actor,payload):
    prev=db.execute("SELECT event_hash FROM audit ORDER BY id DESC LIMIT 1").fetchone()
    previous=prev["event_hash"] if prev else "0"*64
    event={"case_id":cid,"kind":kind,"actor":actor,"payload":payload,"at":utcnow(),"previous_hash":previous}
    digest=hashlib.sha256(json.dumps(event,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    db.execute("INSERT INTO audit(case_id,kind,actor,payload,at,previous_hash,event_hash) VALUES(?,?,?,?,?,?,?)",(cid,kind,actor,json.dumps(payload,sort_keys=True),event["at"],previous,digest))

def initialize():
    with db_session() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS cases(case_id TEXT PRIMARY KEY,payload TEXT NOT NULL,status TEXT NOT NULL,version INTEGER NOT NULL,decision TEXT,updated_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY AUTOINCREMENT,case_id TEXT,kind TEXT NOT NULL,actor TEXT NOT NULL,payload TEXT NOT NULL,at TEXT NOT NULL,previous_hash TEXT NOT NULL,event_hash TEXT NOT NULL);
        CREATE TRIGGER IF NOT EXISTS audit_no_update BEFORE UPDATE ON audit BEGIN SELECT RAISE(ABORT,'audit is append-only'); END;
        CREATE TRIGGER IF NOT EXISTS audit_no_delete BEFORE DELETE ON audit BEGIN SELECT RAISE(ABORT,'audit is append-only'); END;
        """)
        if db.execute("SELECT COUNT(*) n FROM cases").fetchone()["n"]==0:
            for c in SEED:
                a=analyze(c); status="matched" if a["match_status"]=="matched" else "needs_review"
                db.execute("INSERT INTO cases VALUES(?,?,?,?,?,?)",(c["case_id"],json.dumps(c),status,1,None,utcnow()))
                audit_append(db,c["case_id"],"case_ingested","system",{"invoice":c["invoice"]["number"],"analysis":a})

def cases_all():
    with db_session() as db: rows=db.execute("SELECT * FROM cases ORDER BY case_id").fetchall()
    out=[]
    for row in rows:
        c=json.loads(row["payload"]); out.append({**c,"status":row["status"],"version":row["version"],"decision":json.loads(row["decision"]) if row["decision"] else None,"analysis":analyze(c),"updated_at":row["updated_at"]})
    return out

def verify_chain():
    with db_session() as db: rows=db.execute("SELECT * FROM audit ORDER BY id").fetchall()
    previous="0"*64
    for row in rows:
        event={"case_id":row["case_id"],"kind":row["kind"],"actor":row["actor"],"payload":json.loads(row["payload"]),"at":row["at"],"previous_hash":previous}
        digest=hashlib.sha256(json.dumps(event,sort_keys=True,separators=(",",":")).encode()).hexdigest()
        if row["previous_hash"]!=previous or row["event_hash"]!=digest: return {"valid":False,"failed_event":row["id"]}
        previous=row["event_hash"]
    return {"valid":True,"events_checked":len(rows),"head_hash":previous}

def review_brief(case):
    a=case["analysis"]; base=os.environ.get("MATCHDESK_INFERENCE_BASE_URL","").strip()
    if not base:
        codes=", ".join(x["code"] for x in a["exceptions"]) or "none"
        return {"provider":"deterministic-fallback","brief":case["case_id"]+" · "+case["invoice"]["number"]+" · "+a["invoice_total"]+" USD. Exceptions: "+codes+". "+a["recommendation"]+" Payment release and ledger posting remain blocked."}
    model=os.environ.get("MATCHDESK_INFERENCE_MODEL","")
    if not model: raise ValueError("MATCHDESK_INFERENCE_MODEL required with inference endpoint")
    base=base.rstrip("/")
    if not base.endswith("/v1") and not base.endswith("/api/v1"): base+="/v1"
    safe={"case_id":case["case_id"],"invoice":case["invoice"]["number"],"amount":a["invoice_total"],"po":case["po"]["number"],"exceptions":a["exceptions"],"recommendation":a["recommendation"]}
    payload={"model":model,"temperature":0.1,"max_tokens":240,"messages":[{"role":"system","content":"Draft a concise AP controller brief using only supplied evidence. Do not invent facts, alter amounts, approve payment, or post to a ledger."},{"role":"user","content":json.dumps(safe,sort_keys=True)}]}
    headers={"Content-Type":"application/json"}; key=os.environ.get("MATCHDESK_INFERENCE_API_KEY","")
    if key: headers["Authorization"]="Bearer "+key
    req=Request(base+"/chat/completions",data=json.dumps(payload).encode(),headers=headers,method="POST")
    with urlopen(req,timeout=20) as res: result=json.loads(res.read(1000000))
    return {"provider":"openai-compatible","model":model,"brief":result["choices"][0]["message"]["content"]}

class Handler(BaseHTTPRequestHandler):
    server_version="MatchImpactDesk/0.1"
    def log_message(self,fmt,*args): print(self.log_date_time_string(),fmt%args)
    def send_json(self,code,data):
        raw=json.dumps(data).encode(); self.send_response(code); self.send_header("Content-Type","application/json; charset=utf-8"); self.send_header("Content-Length",str(len(raw))); self.send_header("Cache-Control","no-store"); self.send_header("X-Content-Type-Options","nosniff"); self.send_header("X-Frame-Options","DENY"); self.send_header("Content-Security-Policy","default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'"); self.end_headers(); self.wfile.write(raw)
    def read_body(self):
        n=int(self.headers.get("Content-Length","0"))
        if n<1 or n>65536 or "application/json" not in self.headers.get("Content-Type",""): raise ValueError("Expected small application/json body")
        value=json.loads(self.rfile.read(n))
        if not isinstance(value,dict): raise ValueError("JSON body must be an object")
        return value
    def authorized(self):
        if ENV!="production" and not TOKEN: return self.client_address[0] in ("127.0.0.1","::1")
        return bool(TOKEN) and secrets.compare_digest(self.headers.get("X-Operator-Token",""),TOKEN)
    def do_GET(self):
        path=urlparse(self.path).path
        if path=="/health": return self.send_json(200,{"ok":True,"service":"match-impact-desk","mode":ENV})
        if path=="/api/overview":
            cs=cases_all(); return self.send_json(200,{"invoices":len(cs),"matched":sum(c["analysis"]["match_status"]=="matched" for c in cs),"exceptions":sum(c["analysis"]["exception_count"]>0 for c in cs),"open_exposure":round(sum(float(c["analysis"]["impact"]["exposure"]) for c in cs if c["status"] not in ("approved","rejected")),2)})
        if path=="/api/cases": return self.send_json(200,{"cases":cases_all()})
        if path=="/api/audit/verify": return self.send_json(200,verify_chain())
        if path=="/api/audit":
            with db_session() as db: rows=db.execute("SELECT * FROM audit ORDER BY id DESC LIMIT 200").fetchall()
            return self.send_json(200,{"events":[{"id":r["id"],"case_id":r["case_id"],"kind":r["kind"],"actor":r["actor"],"payload":json.loads(r["payload"]),"at":r["at"],"hash":r["event_hash"]} for r in rows]})
        if path.startswith("/api/cases/") and path.endswith("/evidence"):
            cid=path.split("/")[3]; c=next((x for x in cases_all() if x["case_id"]==cid),None)
            if not c: return self.send_json(404,{"error":"case_not_found"})
            with db_session() as db: rows=db.execute("SELECT * FROM audit WHERE case_id=? ORDER BY id",(cid,)).fetchall()
            packet={"schema":"match-impact-desk/evidence.v1","case":c,"audit":[dict(r) for r in rows],"notice":"Synthetic data; no payment or ledger action."}
            packet["sha256"]=hashlib.sha256(json.dumps(packet,sort_keys=True,default=str).encode()).hexdigest()
            return self.send_json(200,packet)
        if path.startswith("/api/cases/"):
            cid=path.rsplit("/",1)[-1]; c=next((x for x in cases_all() if x["case_id"]==cid),None)
            return self.send_json(200,c) if c else self.send_json(404,{"error":"case_not_found"})
        name="index.html" if path=="/" else path.lstrip("/")
        target=(STATIC/name).resolve()
        if STATIC.resolve() not in target.parents or not target.is_file(): return self.send_json(404,{"error":"not_found"})
        data=target.read_bytes(); import mimetypes
        self.send_response(200); self.send_header("Content-Type",mimetypes.guess_type(target.name)[0] or "application/octet-stream"); self.send_header("Content-Length",str(len(data))); self.send_header("X-Content-Type-Options","nosniff"); self.send_header("Cache-Control","no-cache"); self.end_headers(); self.wfile.write(data)
    def do_POST(self):
        if not self.authorized(): return self.send_json(403,{"error":"operator_authorization_required"})
        try:
            body=self.read_body(); path=urlparse(self.path).path
            if path=="/api/cases":
                case=validate_case(body.get("case",body))
                with db_session() as db:
                    db.execute("BEGIN IMMEDIATE")
                    prior=db.execute("SELECT payload FROM cases").fetchall()
                    for item in prior:
                        old=json.loads(item["payload"])
                        if old["invoice"]["vendor_id"]==case["invoice"]["vendor_id"] and old["invoice"]["number"]==case["invoice"]["number"]:
                            case["invoice"]["duplicate_of"]=old["invoice"]["number"]
                    if db.execute("SELECT 1 FROM cases WHERE case_id=?",(case["case_id"],)).fetchone(): return self.send_json(409,{"error":"case_id_already_exists"})
                    analysis=analyze(case)
                    state="matched" if analysis["match_status"]=="matched" else "needs_review"
                    db.execute("INSERT INTO cases VALUES(?,?,?,?,?,?)",(case["case_id"],json.dumps(case),state,1,None,utcnow()))
                    audit_append(db,case["case_id"],"case_ingested",str(body.get("actor","operator"))[:80],{"invoice":case["invoice"]["number"],"analysis":analysis})
                result=next(x for x in cases_all() if x["case_id"]==case["case_id"])
                return self.send_json(201,{"case":result})
            if path.startswith("/api/cases/") and path.endswith("/brief"):
                cid=path.split("/")[3]; c=next((x for x in cases_all() if x["case_id"]==cid),None)
                if not c: return self.send_json(404,{"error":"case_not_found"})
                brief=review_brief(c)
                digest=hashlib.sha256(brief["brief"].encode()).hexdigest()
                with db_session() as db: audit_append(db,cid,"controller_brief_drafted",str(body.get("actor","Controller"))[:80],{"provider":brief.get("provider"),"model":brief.get("model"),"brief_sha256":digest})
                return self.send_json(200,brief)
            if path.startswith("/api/cases/") and path.endswith("/decision"):
                cid=path.split("/")[3]; decision=body.get("decision"); actor=str(body.get("actor","Controller"))[:80]; note=str(body.get("note",""))[:1000]; expected=int(body.get("expected_version",0))
                if decision not in ("approve","hold","reject"): raise ValueError("decision must be approve, hold, or reject")
                with db_session() as db:
                    db.execute("BEGIN IMMEDIATE")
                    row=db.execute("SELECT * FROM cases WHERE case_id=?",(cid,)).fetchone()
                    if not row: return self.send_json(404,{"error":"case_not_found"})
                    if row["version"]!=expected: return self.send_json(409,{"error":"stale_version"})
                    if row["status"] in ("approved","rejected"): return self.send_json(409,{"error":"case_already_final"})
                    c=json.loads(row["payload"]); a=analyze(c)
                    if decision=="approve" and a["exception_count"] and len(note.strip())<12: raise ValueError("exception approval requires a substantive resolution note")
                    state={"approve":"approved","hold":"on_hold","reject":"rejected"}[decision]
                    record={"decision":decision,"actor":actor,"note":note.strip(),"payment_released":False,"ledger_posted":False,"at":utcnow()}
                    db.execute("UPDATE cases SET status=?,version=version+1,decision=?,updated_at=? WHERE case_id=?",(state,json.dumps(record),utcnow(),cid))
                    audit_append(db,cid,"controller_decision",actor,record)
                c=next(x for x in cases_all() if x["case_id"]==cid); return self.send_json(200,{"case":c})
            return self.send_json(404,{"error":"not_found"})
        except (ValueError,TypeError,json.JSONDecodeError) as e: return self.send_json(400,{"error":str(e)})
        except Exception as e: return self.send_json(502,{"error":"operation_failed","detail":type(e).__name__})

def main():
    initialize(); print("Match Impact Desk on http://"+HOST+":"+str(PORT)+" ("+ENV+")")
    ThreadingHTTPServer((HOST,PORT),Handler).serve_forever()

if __name__=="__main__": main()
