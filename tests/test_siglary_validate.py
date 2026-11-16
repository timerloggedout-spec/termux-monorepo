from __future__ import annotations
import json, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"scripts/siglary"),str(ROOT/"scripts/ci")]
import siglary_validate as s
from do_statement_policy import classify_instruction,is_imperative_subject,subject_action_verb

class SiglaryTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name)
  (self.root/"scripts/siglary").mkdir(parents=True); (self.root/"docs/proposals/active/notation-sets").mkdir(parents=True)
  (self.root/"scripts/siglary/issued_glyphs.json").write_text(json.dumps({"schema":"siglary-issued-glyphs/v1","source":{"path":"matrice.md","section":"GLYPHS","source_commit":"abc1234"},"glyphs":["👁","🧾","⚖","⚖✓","🟢","🔴","🟡"]}),encoding="utf-8")
  (self.root/s.MATRICE).write_text("### repo (shorthand_repo)\n\n| Chord | Term |\n|---|---|\n| mrg | merge |\n\n### DoE (shorthand_doe)\n\n| Chord | Term |\n|---|---|\n| prf | proof |\n",encoding="utf-8")
 def tearDown(self): self.tmp.cleanup()
 def rules(self): return s.load_glyphs(self.root/"scripts/siglary/issued_glyphs.json"),s.load_domains(self.root)
 def test_n_marker_value_rejected_json_yaml_and_skill_block(self):
  self.assertEqual(s.data_findings('{"state":"N∅"}',"x.json")[0]["rule"],"N-IN-DATA")
  self.assertEqual(s.data_findings("state: NOT_ESTABLISHED\n","x.yaml")[0]["rule"],"N-IN-DATA")
  f=chr(96)*3; self.assertEqual(s.data_blocks(f+"json\n{\"state\":\"N∅\"}\n"+f,"SKILL.md")[0]["rule"],"N-IN-DATA")
 def test_n_marker_prose_or_key_not_data_value(self):
  self.assertEqual(s.data_findings('{"N∅":"chat marker"}',"x.json"),[])
  self.assertEqual(s.data_findings("N∅ is chat-only, not a value.","x.yaml"),[])
 def test_issued_and_unissued_glyphs(self):
  self.assertEqual(s.glyph_clusters("🟢🔴🟡"),["🟢","🔴","🟡"])
  self.assertEqual(s.glyph_clusters("⚖✓"),["⚖✓"])
  g,d=self.rules(); self.assertEqual(s.text_findings("Use 🧬.","SKILL.md","skills",g,d)[0]["rule"],"UNISSUED-GLYPH")
 def test_code_and_quoted_prior_art_are_exempt(self):
  g,d=self.rules(); f=chr(96)*3
  self.assertEqual(s.text_findings("> prior art 🧬\n\n"+f+"python\nx='🧬'\n"+f,"SKILL.md","skills",g,d),[])
 def test_class_misuse_and_unregistered_operator(self):
  g,d=self.rules(); self.assertEqual(s.text_findings("Operators are glyphs.","x","skills",g,d)[0]["rule"],"CLASS-MISUSE")
  self.assertEqual(s.text_findings("operator: ⊕","x","skills",g,d)[0]["rule"],"UNREGISTERED-OPERATOR")
  self.assertEqual(s.text_findings("operator: ∧","x","skills",g,d),[])
 def test_chord_requires_registered_named_domain(self):
  g,d=self.rules(); self.assertEqual(s.text_findings("chord: mrg","x","skills",g,d)[0]["rule"],"UNRESOLVED-CHORD")
  self.assertEqual(s.text_findings("chord: mrg shorthand_doe","x","skills",g,d)[0]["rule"],"UNRESOLVED-CHORD")
  self.assertEqual(s.text_findings("chord: mrg shorthand_repo","x","skills",g,d),[])
 def test_receipt_adjacency(self):
  g,d=self.rules(); self.assertEqual(s.text_findings("state: PROMOTED\nno receipt","comment","github_collaboration",g,d)[0]["rule"],"RECEIPT-ADJACENCY")
  self.assertEqual(s.text_findings("state: PROMOTED\nreceipt: https://example.invalid/1","comment","github_collaboration",g,d),[])
 def test_claude_reference_is_required(self):
  (self.root/"CLAUDE.md").write_text("General instructions\n",encoding="utf-8")
  self.assertEqual(s.census(self.root,["CLAUDE.md"])["state"],"FAIL")
 def test_empty_census_is_inconclusive(self): self.assertEqual(s.census(self.root,[])["state"],"INCONCLUSIVE")
 def test_doe_structured_record_requires_receipt(self):
  bad=s.structured_receipt_findings('{"state":"PROMOTED"}',"ops/doe/receipt.json")
  good=s.structured_receipt_findings('{"state":"PROMOTED","receipt_id":"abc"}',"ops/doe/receipt.json")
  self.assertEqual(bad[0]["rule"],"RECEIPT-ADJACENCY")
  self.assertEqual(good,[])
 def test_doe_structured_record_requires_receipt(self):
  bad=s.structured_receipt_findings('{"state":"PROMOTED"}',"ops/doe/receipt.json")
  good=s.structured_receipt_findings('{"state":"PROMOTED","receipt_id":"abc"}',"ops/doe/receipt.json")
  self.assertEqual(bad[0]["rule"],"RECEIPT-ADJACENCY")
  self.assertEqual(good,[])
 def test_principle_five_remains_est_review_not_hard(self):
  g,d=self.rules(); f=s.text_findings("SIGLARY-FLAG: ambiguous token","skill","skills",g,d)
  self.assertEqual(f[0]["severity"],"EST")
  report=s.census(self.root,[],{"pull_request":{"title":"plain title","body":"SIGLARY-FLAG: ambiguous token"}},"pull_request")
  self.assertEqual(report["state"],"REVIEW")
  self.assertEqual(report["est_violations"],1)
 def test_event_surface_inventory(self):
  self.assertEqual(len(s.event_surfaces({"review":{"body":"DO: inspect"}},"pull_request_review")),1)
  self.assertEqual(len(s.event_surfaces({"release":{"name":"v1","body":"DO: publish"}},"release")),2)
 def test_exemptions_and_idempotent_feed(self):
  self.assertEqual(s.exemption("ops/x/ledger.jsonl","{}"),"E1")
  self.assertEqual(s.exemption("tests/fixtures/x.json","{}"),"E4")
  self.assertEqual(s.exemption("docs/ops/generated/x.json","{}"),"E5")
  self.assertEqual(s.exemption("exports/chat-transcripts/x.md","{}"),"E6")
  p=self.root/"feed.jsonl"; row={"receipt_id":"same"}; self.assertTrue(s.append_feed(p,row)); self.assertFalse(s.append_feed(p,row))

class DoPolicyTests(unittest.TestCase):
 def test_direct_and_explicit_do_pass(self):
  self.assertEqual(classify_instruction("Create the artifact."),"natural_imperative")
  self.assertEqual(classify_instruction("DO: create the artifact."),"explicit_do")
 def test_prohibitions_remain_constraints(self):
  for x in ("Do not overwrite the standard.","Never expose credentials.","- Avoid leaking secrets."): self.assertEqual(classify_instruction(x),"constraint")
 def test_hedging_fails(self):
  for x in ("We should update the gate.","It might be useful to add tests.","- Perhaps we should reconcile."): self.assertEqual(classify_instruction(x),"hedged")
 def test_commit_subjects(self):
  self.assertTrue(is_imperative_subject("fix(siglary): accept export in commit subjects"))
  self.assertTrue(is_imperative_subject("ci: DO: enforce the hard gate"))
  self.assertEqual(subject_action_verb("backup relay: export archive"),"export")
  self.assertFalse(is_imperative_subject("fix(ci): action-first vocabulary"))

if __name__=="__main__": unittest.main()
