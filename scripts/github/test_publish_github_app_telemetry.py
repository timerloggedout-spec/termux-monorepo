import unittest
from unittest.mock import patch
import urllib.error
import publish_github_app_telemetry as p

class PublisherTests(unittest.TestCase):
 def sample(self):
  return {'g4_runtime_receipt': {'observed_at':'2026-10-30T10:00:00+00:00','mint_outcome':'success','workflow':{'run_id':123,'attempt':2,'head_sha':'a'*40}}}
 def test_rejects_run_identity_mismatch(self):
  with self.assertRaisesRegex(ValueError,'identity'): p.publish(self.sample(),'token','owner/repo',123,1)
 def test_rejects_timezone_without_offset(self):
  d=self.sample(); d['g4_runtime_receipt']['observed_at']='2026-10-30T10:00:00'
  with self.assertRaisesRegex(ValueError,'timezone'): p.publish(d,'token','owner/repo',123,2)
 def test_refuses_existing_observation(self):
  error=urllib.error.HTTPError('https://api.github.com',422,'exists',{},None)
  with patch.object(p.urllib.request,'urlopen',side_effect=error):
   with self.assertRaisesRegex(RuntimeError,'HTTP 422'): p.publish(self.sample(),'token','owner/repo',123,2)

if __name__=='__main__': unittest.main()
