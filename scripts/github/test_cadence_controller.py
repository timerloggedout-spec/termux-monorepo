import datetime as dt
import unittest
import cadence_controller as c

class CadenceTests(unittest.TestCase):
 def test_headroom_selects_adaptive_intervals(self):
  self.assertEqual(c.interval_hours(90,100),3)
  self.assertEqual(c.interval_hours(60,100),6)
  self.assertEqual(c.interval_hours(30,100),12)
  self.assertEqual(c.interval_hours(10,100),24)
 def test_not_due_until_persisted_deadline(self):
  state={'next_due_at':'2026-10-30T12:00:00+00:00'}
  now=dt.datetime.fromisoformat('2026-10-30T11:00:00+00:00')
  self.assertFalse(c.should_run(state,now))
  self.assertTrue(c.should_run(state,now,force=True))
 def test_next_state_uses_receipt_rate_limit(self):
  doc={'g4_runtime_receipt':{'observed_at':'2026-10-30T10:00:00+00:00','rate_limit_after':{'remaining':90,'limit':100},'workflow':{'run_id':42,'attempt':1}}}
  state=c.next_state(doc)
  self.assertEqual(state['last_interval_hours'],3)
  self.assertEqual(state['next_due_at'],'2026-10-30T13:00:00+00:00')

if __name__=='__main__': unittest.main()
