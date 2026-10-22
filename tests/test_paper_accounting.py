import csv, io, tempfile, threading, unittest, multiprocessing, subprocess, sys, os, json
from pathlib import Path
from scripts.model_selection_market.accounting import PaperMarket, AccountingError, CorruptJournal

class PaperAccountingTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(); self.path=Path(self.tmp.name)/'market-events.jsonl'; self.m=PaperMarket(self.path)
 def tearDown(self): self.tmp.cleanup()
 def test_issue_reserve_settle_and_replay(self):
  self.m.issue('seed:1','alice',20,'test fixture seed')
  self.m.reserve('bet:1:reserve','bet:1','alice',7,'self-wager:1')
  self.assertEqual(self.m.balances()['alice'],{'balance':20,'reserved':7,'available':13})
  self.m.settle('bet:1:settle','bet:1','bob')
  self.assertEqual(self.m.balances()['alice']['balance'],13)
  self.assertEqual(self.m.balances()['bob']['balance'],7)
  self.assertEqual(PaperMarket(self.path).balances(),self.m.balances())
 def test_idempotency_and_double_finalize(self):
  self.m.issue('i','a',10,'fixture'); self.m.reserve('r','offer:2','a',4,'peer-offer:2')
  self.m.reserve('r','offer:2','a',4,'peer-offer:2')
  with self.assertRaises(AccountingError): self.m.reserve('r','offer:2','a',5,'peer-offer:2')
  self.m.release('rel','offer:2')
  with self.assertRaises(AccountingError): self.m.release('rel2','offer:2')
 def test_overspend_and_concurrent_atomic_reservation(self):
  self.m.issue('seed','a',10,'job fixture'); results=[]
  def worker(i):
   try: PaperMarket(self.path).reserve(f'key{i}',f'res{i}','a',7,f'job:{i}'); results.append('ok')
   except AccountingError: results.append('no')
  ts=[threading.Thread(target=worker,args=(i,)) for i in range(2)]
  [t.start() for t in ts]; [t.join() for t in ts]
  self.assertCountEqual(results,['ok','no']); self.assertEqual(self.m.balances()['a']['available'],3)
 def test_void_and_csv_stale_formula_safe(self):
  self.m.issue('seed','=intruder',3,'fixture provenance')
  self.m.reserve('r','x','=intruder',2,'job:wager'); self.m.void('v','x')
  out=io.StringIO(); self.m.export_csv(out); self.assertIn("'=intruder",out.getvalue())
  self.assertTrue(self.m.csv_is_current(io.StringIO(out.getvalue())))
  self.m.issue('next','alice',1,'fixture'); self.assertFalse(self.m.csv_is_current(io.StringIO(out.getvalue())))
 def test_corrupt_tail_fails_closed(self):
  self.m.issue('i','a',1,'fixture')
  with self.path.open('ab') as f:f.write(b'{bad}\n')
  with self.assertRaises(CorruptJournal): PaperMarket(self.path)
 def test_bad_inputs_and_double_void(self):
  with self.assertRaises(AccountingError): self.m.issue('bad','a',1.2,'x')
  self.m.issue('i','a',1,'fixture'); self.m.reserve('r','z','a',1,'card:1'); self.m.void('v','z')
  with self.assertRaises(AccountingError): self.m.void('v2','z')

if __name__=='__main__': unittest.main()

class IntegratedMarketTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(); self.path=Path(self.tmp.name)/'j.jsonl'
 def tearDown(self): self.tmp.cleanup()
 def test_graph_uses_journal_and_references_existing_bet(self):
  from scripts.model_selection_market.market import MarketGraph, BetEntry
  g=MarketGraph(str(self.path)); g.issue_paper_points('seed','alice',8,'fixture seed')
  with self.assertRaises(ValueError): g.reserve_bet('r','rid','alice',2,'absent')
  b=g.place_bet(BetEntry(actor_class='itself',actor_id='alice',subject_kind='model',subject_id='m'))
  g.reserve_bet('r','rid','alice',2,b['entry_id'])
  g2=MarketGraph(str(self.path))
  self.assertEqual(g2.accounting_snapshot()['accounts']['alice']['reserved'],2)
  self.assertEqual(len(g2.accounting_snapshot()['events']),3)
  self.assertEqual(len(g2.bets),1)
 def test_conflicting_idempotency_invalid_owner_and_overflow(self):
  m=PaperMarket(self.path); m.issue('seed','a',10,'fixture')
  with self.assertRaises(AccountingError): m.issue('seed','b',10,'fixture')
  with self.assertRaises(AccountingError): m.issue('overflow','a',2**63,'fixture')
  with self.assertRaises(AccountingError): m.reserve('bad','x','',1,'bet:1')
 def test_owner_scoped_identity_and_snapshot_isolation(self):
  from scripts.model_selection_market.market import MarketGraph, BetEntry
  g=MarketGraph(str(self.path))
  a=g.place_bet(BetEntry('itself','model','m',actor_id='alice'))
  b=g.place_bet(BetEntry('itself','model','m',actor_id='bob'))
  self.assertNotEqual(a['entry_id'],b['entry_id'])
  snap=g.snapshot();snap['bets'][0]['subject']['id']='tampered'
  self.assertEqual(g.bets[0]['subject']['id'],'m')
 def test_persisted_offer_lifecycle_peer_and_job_scopes(self):
  from scripts.model_selection_market.market import MarketGraph, TradingCard, BetEntry
  g=MarketGraph(str(self.path));g.issue_paper_points('ia','alice',12,'test');g.issue_paper_points('ib','bob',12,'test')
  card=g.add_card(TradingCard('review','alice'))
  offer=g.offer_trade('offer-key',card['card_id'],'bob',at='2026-01-01T00:00:00Z')
  g.reserve_offer('offer-reserve','offer-r','alice',3,card['card_id'],offer['at'])
  g.settle('offer-settle','offer-r','bob')
  job=g.place_bet(BetEntry('job','job','task-1',actor_id='bob'))
  g.reserve_bet('job-reserve','job-r','bob',2,job['entry_id']);g.release('job-release','job-r')
  restarted=MarketGraph(str(self.path))
  self.assertTrue(any(x.get('action')=='offer' for x in restarted.cards[card['card_id']]['trade_log']))
  self.assertEqual(restarted.accounting_snapshot()['accounts']['alice']['balance'],9)
  with self.assertRaises(ValueError): restarted.reserve_bet('stale','stale-r','bob',1,'not-a-job')
 def test_reopen_after_durable_append_and_torn_tail(self):
  m=PaperMarket(self.path); m.issue('seed','a',5,'fixture')
  m.reserve('reserve','r','a',3,'job:1')
  # Re-open is the recovery path after a caller loses acknowledgement.
  again=PaperMarket(self.path); again.reserve('reserve','r','a',3,'job:1')
  self.assertEqual(again.balances()['a']['reserved'],3)
  with self.path.open('ab') as f: f.write(b'{"partial"')
  with self.assertRaises(CorruptJournal): PaperMarket(self.path)

 def test_graph_retry_and_peer_refresh_are_durable_and_idempotent(self):
  from scripts.model_selection_market.market import MarketGraph, TradingCard, BetEntry
  g1=MarketGraph(str(self.path)); g2=MarketGraph(str(self.path))
  card=g1.add_card(TradingCard('review','alice'))
  duplicate=g2.add_card(TradingCard('review','alice'))
  self.assertEqual(duplicate['card_id'],card['card_id'])
  self.assertEqual(len(g1.snapshot()['edges']),1)
  self.assertEqual(len(g2.snapshot()['cards']),1)
  offer=g1.offer_trade('stable-offer',card['card_id'],'bob',sha='abc')
  before=len(g1.accounting_snapshot()['events'])
  self.assertEqual(g2.offer_trade('stable-offer',card['card_id'],'bob',sha='abc')['at'],offer['at'])
  self.assertEqual(len(g1.accounting_snapshot()['events']),before)
  with self.assertRaises(AccountingError): g2.offer_trade('stable-offer',card['card_id'],'carol',sha='abc')
  self.assertEqual(len(g2.snapshot()['cards'][0]['trade_log']),1)
  bet=BetEntry('itself','model','model-1',actor_id='alice')
  first=g1.place_bet(bet); count=len(g1.accounting_snapshot()['events'])
  retry=g2.place_bet(BetEntry('itself','model','model-1',actor_id='alice'))
  self.assertEqual(retry,first)
  self.assertEqual(len(g1.accounting_snapshot()['events']),count)
  with self.assertRaises(AccountingError): g2.place_bet(BetEntry('itself','model','model-1',actor_id='alice',units=2))
  self.assertEqual(len(g2.snapshot()['bets']),1)


def _proc_reserve(path, i, q):
 try: PaperMarket(path).reserve(f"proc:{i}",f"r:{i}","owner",7,f"job:{i}"); q.put("ok")
 except AccountingError: q.put("no")

class DurableRecoveryTests(unittest.TestCase):
 def test_multiprocess_overspend(self):
  with tempfile.TemporaryDirectory() as d:
   p=str(Path(d)/"j");PaperMarket(p).issue("seed","owner",10,"test")
   q=multiprocessing.Queue(); ps=[multiprocessing.Process(target=_proc_reserve,args=(p,i,q)) for i in range(2)]
   [x.start() for x in ps];[x.join(10) for x in ps]
   self.assertCountEqual([q.get(timeout=2) for _ in ps],["ok","no"])
   self.assertEqual(PaperMarket(p).balances()["owner"]["available"],3)
 def test_restart_graph_and_corrupt_csv_values(self):
  from scripts.model_selection_market.market import MarketGraph, TradingCard, BetEntry
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"j";g=MarketGraph(str(p)); c=g.add_card(TradingCard("r","alice"));b=g.place_bet(BetEntry("itself","model","m",actor_id="alice"));g.issue_paper_points("i","alice",8,"seed")
   g2=MarketGraph(str(p));self.assertIn(c['card_id'],g2.cards);self.assertEqual(len(g2.bets),1)
   out=io.StringIO();g2._accounting.export_csv(out); text=out.getvalue().replace(',8,0,8,',',999,0,999,')
   self.assertFalse(g2._accounting.csv_is_current(io.StringIO(text)))
 def test_subprocess_durable_append_then_restart(self):
  with tempfile.TemporaryDirectory() as d:
   p=str(Path(d)/"j"); code="from scripts.model_selection_market.accounting import PaperMarket; import os; m=PaperMarket(%r);m.issue('issued','x',3,'crash');os._exit(9)"%p
   r=subprocess.run([sys.executable,'-c',code],cwd=os.getcwd());self.assertEqual(r.returncode,9)
   self.assertEqual(PaperMarket(p).balances()['x']['balance'],3)
