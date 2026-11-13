#!/usr/bin/env python3
"""Small read-only GitHub feed adapter for the Delphic Observatory."""
from __future__ import annotations
import json, os, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
REPO=os.environ.get("GITHUB_REPOSITORY","timerloggedout-spec/termux-monorepo")
PORT=int(os.environ.get("PORT","10000")); TTL=int(os.environ.get("FEED_CACHE_TTL_SECONDS","45")); CACHE={}
def fetch(path):
 now=time.time(); old=CACHE.get(path)
 if old and now-old["at"]<TTL: return {**old["body"],"cache":"hit"}
 req=Request(f"https://api.github.com/repos/{REPO}{path}",headers={"Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28","User-Agent":"delphic-observatory-readonly-feed/1"})
 token=os.environ.get("GITHUB_READ_TOKEN")
 if token: req.add_header("Authorization",f"Bearer {token}")
 with urlopen(req,timeout=8) as res:
  data=json.loads(res.read().decode()); observed=time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime())
  body={"schema":"observatory-feed/v1","source":"github","source_ref":REPO,"observed_at":observed,"source_updated_at":observed,"stale":False,"data":data}
  CACHE[path]={"at":now,"body":body}; return {**body,"cache":"miss"}
class Handler(BaseHTTPRequestHandler):
 def send_json(self,status,body):
  raw=json.dumps(body,separators=(",",":")).encode(); self.send_response(status)
  self.send_header("Content-Type","application/json; charset=utf-8"); self.send_header("Content-Length",str(len(raw)))
  self.send_header("Cache-Control","public, max-age=15, stale-while-revalidate=30")
  self.send_header("Access-Control-Allow-Origin","*"); self.send_header("Access-Control-Allow-Methods","GET, OPTIONS"); self.send_header("Access-Control-Allow-Headers","Content-Type"); self.end_headers()
  if status!=204: self.wfile.write(raw)
 def do_OPTIONS(self): self.send_json(204,{})
 def do_GET(self):
  path=self.path.split("?",1)[0]
  if path=="/healthz": return self.send_json(200,{"status":"ok","service":"delphic-observatory-feed","schema":"observatory-feed/v1","repository":REPO})
  routes={"/api/pulls":"/pulls?state=open&per_page=10","/api/actions/runs":"/actions/runs?per_page=10"}
  if path not in routes: return self.send_json(404,{"error":"not_found"})
  try: return self.send_json(200,fetch(routes[path]))
  except HTTPError as exc: return self.send_json(exc.code if exc.code in (403,429) else 502,{"error":"upstream_http_error","status":exc.code,"stale":False})
  except (URLError,TimeoutError,ValueError) as exc: return self.send_json(503,{"error":"upstream_unavailable","detail":str(exc),"stale":False})
 def log_message(self,fmt,*args): print("%s - %s"%(self.address_string(),fmt%args),flush=True)
if __name__=="__main__": ThreadingHTTPServer(("0.0.0.0",PORT),Handler).serve_forever()
