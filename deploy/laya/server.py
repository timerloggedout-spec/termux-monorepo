#!/usr/bin/env python3
"""Minimal bounded Render HTTP adapter around Laya."""
from __future__ import annotations
import json,os
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from laya import Router
router=Router(preload=os.getenv("LAYA_PRELOAD","0").lower() in {"1","true","yes"})
class Handler(BaseHTTPRequestHandler):
 def _json(self,status,payload):
  raw=json.dumps(payload,sort_keys=True).encode(); self.send_response(status)
  self.send_header("Content-Type","application/json"); self.send_header("Content-Length",str(len(raw))); self.end_headers(); self.wfile.write(raw)
 def do_GET(self):
  self._json(200,{"ok":True,"engine":"laya","mode":"system-one"}) if self.path=="/healthz" else self._json(404,{"error":"not_found"})
 def do_POST(self):
  if self.path!="/decide": return self._json(404,{"error":"not_found"})
  try:
   size=int(self.headers.get("Content-Length","0"))
   if size>256*1024: raise ValueError("request too large")
   body=json.loads(self.rfile.read(size)); self._json(200,router.predict(body["state"],body["questions"]))
  except Exception as exc: self._json(400,{"error":type(exc).__name__,"message":str(exc)})
if __name__=="__main__": ThreadingHTTPServer(("0.0.0.0",int(os.getenv("PORT","10000"))),Handler).serve_forever()
