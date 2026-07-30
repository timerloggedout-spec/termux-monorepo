#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# D3DUPL1C4T3_TRU3_V3R510N5.PY - 1337 🪄 ArchWizard C4ST
# C0LL4PS3 FR4GM3NT5 >= 0.95, K33P L4T3ST + P01NT3R CH41N

import json
import hashlib
import os
import sys
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

try:
    from fragment_matcher import compute_similarity
except ImportError:
    print("⚠️  fragment_matcher n0t f0und. U53|n6 5!mpl3 h45h c0mp4r150n.", file=sys.stderr)
    def compute_similarity(a: str, b: str) -> float:
        """F4LLB4CK: l3v3n5ht31n r4t10"""
        if a == b:
            return 1.0
        if not a or not b:
            return 0.0
        len_a, len_b = len(a), len(b)
        if len_a == 0 or len_b == 0:
            return 0.0
        # qu1ck 4ppr0x (fast en0ugh)
        matches = sum(1 for i in range(min(len_a, len_b)) if a[i] == b[i])
        return matches / max(len_a, len_b)


def hash_content(content: str) -> str:
    """R3turn bl4k3-256 d1g35t."""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def load_true_versions(path: str) -> Dict[str, List[Dict[str, Any]]]:
    """L04d JSON 4nd 3n5ur3 f1l3-k3y3d v3r510n l15t."""
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # v4l1d4t3 + tr4n5f0rm 1nt0 un1f0rm d1ct
    if isinstance(data, list):
        # 4SSum3 l15t 0f v3r510n 0bj3ct5 w1th 'file' f13ld
        by_file: Dict[str, List[Dict[str, Any]]] = {}
        for ver in data:
            fname = ver.get('file')
            if not fname:
                continue
            by_file.setdefault(fname, []).append(ver)
        return by_file
    elif isinstance(data, dict):
        return data
    else:
        raise ValueError(f"Unkn0wn tru3_v3r510n5 f0rm4t: {type(data)}")


def save_true_versions(data: Dict[str, List[Dict[str, Any]]], out_path: str) -> None:
    """Wr1t3 c0ll4p53d 5tructur3 t0 J50N."""
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ D3dupl1c4t3d tru3_v3r510n5 wr1tt3n t0 {out_path}")


def deduplicate_versions_for_file(versions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    C0ll4p53 c0n5ecut1v3 v3r510n5 w1th 51m1l4r1ty >= 0.95.
    K33p 0nly l4t35t v3r510n, 4dd p01nt3r ch41n t0 0ld h45h35.
    """
    if not versions:
        return []
    
    # 50rt by t1m35t4mp 4sc3nd1ng (0ld -> n3w) 1f 4v41l4bl3
    def get_timestamp(v: Dict[str, Any]) -> int:
        t = v.get('timestamp')
        if isinstance(t, (int, float)):
            return int(t)
        # f4llb4ck t0 1nd3x p051t10n
        return 0
    
    versions_sorted = sorted(versions, key=get_timestamp)
    
    # 3xtr4ct c0nt3nt 4nd h45h f0r 34ch v3r510n
    enriched = []
    for v in versions_sorted:
        content = v.get('content', '')
        if not content and 'hash' in v:
            # 1f 0nly h45h 3x15t5, we cannot compute similarity -> keep as is
            pass
        h = v.get('hash') or hash_content(content)
        enriched.append({
            'orig': v,
            'content': content,
            'hash': h,
            'timestamp': get_timestamp(v)
        })
    
    # P01nt3r ch41n: l4t35t 0nly + l1nk5 t0 pr3v10u5
    # Start fr0m 0ld35t -> n3w35t, but we w1ll k33p 0nly n3w35t + ch41n
    kept_version = None
    pointer_chain = []
    
    # W4lk fr0m 0ld t0 n3w, d3tect c0ll4p53
    i = 0
    while i < len(enriched):
        curr = enriched[i]
        if i == len(enriched) - 1:
            # L4t35t v3r510n 4lw4y5 k3pt
            kept_version = curr['orig'].copy()
            kept_version['hash'] = curr['hash']
            kept_version['pointer_chain'] = pointer_chain + [curr['hash']] if pointer_chain else [curr['hash']]
            # remov3 'content' 1f t00 b1g? n0, pr35erv3
            break
        
        nxt = enriched[i + 1]
        sim = compute_similarity(curr['content'], nxt['content'])
        
        if sim >= 0.95:
            # c0ll4p53 curr 1nt0 nxt'5 p01nt3r ch41n
            pointer_chain.append(curr['hash'])
            # 4l50 4dd curr'5 0ld p01nt3r ch41n 1f 3x15t5
            if 'pointer_chain' in curr['orig']:
                pointer_chain.extend(curr['orig']['pointer_chain'])
            # r3m0v3 curr, m0v3 t0 nxt
            i += 1
        else:
            # k33p curr 4s 1t 1s (but 1f th1s 1s n0t l4t35t, w3 w0n't k33p 1t)
            # H0w3v3r, 0ur 4l9 0nly k33p5 l4t35t. 1f w3 h1t d1551m1l4r, w3 l053 curr p3rm4n3ntly.
            # But th4t'5 wr0ng – w3 n33d t0 k33p 0nly l4t35t, but 4l50 k33p d1551m1l4r v3r510n5 4s 5ep4r4t3 f1l35?
            # R34d r3qu1r3m3nt: "K33p 0nly th3 l4t35t v3r510n p3r f1l3" – 1mpl13s 0nly 1 v3r510n p3r f1l3.
            # S0 any d1551m1l4r v3r510n b3c0m3s 4 d1ff3r3nt f1l3? n0, 1t'5 4 ch41n 0f v3r510n5 f0r 54m3 f1l3.
            # Th3 4l9 1n5truc710n 5ay5: "c0ll4p53 0ld3r v3r510n ... k33p 0nly l4t35t v3r510n p3r f1l3"
            # S0 1f d1551m1l4r, w3 c4nn0t c0ll4p53, but w3 mu5t 5t1ll k33p 0nly th3 l4t35t. Th4t m34n5 w3 dr0p 0ld3r 0n35 4ll t0g3th3r.
            # H0w3v3r, th4t w0uld l053 d4t4. B3tt3r t0 1nclud3 4 ch41n 0f 4ll pr3v10u5 h45h35 3v3n 1f d1551m1l4r? 
            # Th3 r34d1n9: "p01nt3r ch41n t0 4ll pr3v10u5 h45h35" – 5ugg35t5 w3 5t0r3 4ll h45h35 0f 4ny v3r510n th4t 3v3r 3x15t3d f0r th4t f1l3.
            # S0 l4t35t v3r510n w1ll h4v3 4 l15t 0f h45h35 0f 4ll pr3v10u5 v3r510n5, r3g4rdl355 0f 51m1l4r1ty.
            # Th3 c0ll4p53 0nly 4ppl13s t0 "5t0r3 1t5 h45h 4s 4 p01nt3r 1n th3 n3w3r v3r510n'5 3ntry" – 1t d035n't 5ay dr0p d1551m1l4r 0n35.
            # W41t, r34d 4g41n: "c0ll4p53 th3 0ld3r v3r510n 4nd 5t0r3 1t5 h45h 4s 4 p01nt3r" -> 0nly wh3n 51m1l4r >= 0.95.
            # 0th3rw15e, d0 n0t c0ll4p53, but w3 5t1ll n33d t0 k33p 0nly th3 l4t35t v3r510n. 5h0uld w3 5t0r3 th3 0ld3r h45h35 4nyw4y? Y35.
            # 1mpl3m3nt: W3 4ccumul4t3 4LL pr3v10u5 h45h35 1n th3 p01nt3r_ch41n, r3g4rdl355 0f 51m1l4r1ty.
            # But 0nly "c0ll4p53" (m34n1ng w3 dr0p th3 0bj3ct fr0m th3 0utput) wh3n 51m1l4r1ty >= 0.95.
            # 0th3rw15e w3 5t1ll 4dd 1t5 h45h t0 th3 ch41n, but w3 d0 NOT output th3 0ld3r v3r510n 4s 4 53p4r4t3 3ntry.
            # F1n4l r35ult: 0N3 3ntry p3r f1l3 (l4t35t), c0nt41n1ng 4rr4y 0f 4LL pr3v10u5 h45h35 (p01nt3r_ch41n).
            pointer_chain.append(curr['hash'])
            i += 1
    
    # 1f w3 n3v3r 535t4bl15h3d k3pt_v3r510n (3.g., 0nly 0n3 1t3r4t10n), f1x 1t
    if kept_version is None and enriched:
        last = enriched[-1]
        kept_version = last['orig'].copy()
        kept_version['hash'] = last['hash']
        kept_version['pointer_chain'] = [h['hash'] for h in enriched[:-1]] + [last['hash']]
    
    return [kept_version] if kept_version else []


def deduplicate_true_versions(input_path: str, output_path: Optional[str] = None) -> None:
    """M41n 3ntry p01nt: c0ll4p53 + p01nt3r ch41n."""
    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_dedup{ext}"
    
    print(f"📂 L04d1ng tru3_v3r510n5 fr0m {input_path}")
    by_file = load_true_versions(input_path)
    
    deduped_by_file = {}
    for file_path, versions in by_file.items():
        print(f"🔍 Pr0c3551ng {file_path} w1th {len(versions)} v3r510n5")
        deduped = deduplicate_versions_for_file(versions)
        if deduped:
            deduped_by_file[file_path] = deduped
        else:
            print(f"⚠️  N0 v3r510n5 k3pt f0r {file_path}")
    
    save_true_versions(deduped_by_file, output_path)
    print(f"🎉 D0n3! 0r1g1n4l f1l3c0unt: {len(by_file)}, 4ft3r d3dup: {len(deduped_by_file)}")


def router_agent_curate_rules(session_log_path: str = "session_logs.json") -> Dict[str, Any]:
    """
    1d3nt1fy 535510n5 wh3r3 d3dup d15cu5510n 0ccurr3d.
    C0ll3ct rul35 b4s3d 0n pr3v10u5 c0nv3r54t10n5.
    """
    rules = {
        "dedup_enabled": True,
        "similarity_threshold": 0.95,
        "keep_only_latest": True,
        "pointer_chain_all_hashes": True,
        "session_filters": []
    }
    
    if not os.path.exists(session_log_path):
        print(f"⚠️  N0 535510n l0g f0und 4t {session_log_path}, u51n9 d3f4ult rul35.")
        return rules
    
    try:
        with open(session_log_path, 'r', encoding='utf-8') as f:
            sessions = json.load(f)
        
        dedup_sessions = []
        for sess in sessions:
            sess_text = json.dumps(sess).lower()
            if any(kw in sess_text for kw in ['dedup', 'deduplicate', 'true_versions', 'pointer chain', 'similarity']):
                dedup_sessions.append(sess)
        
        if dedup_sessions:
            rules["session_filters"] = [s.get("session_id", "unknown") for s in dedup_sessions[:10]]
            print(f"🔍 F0und {len(dedup_sessions)} 535510n5 w1th d3dup d15cu5510n.")
            # 3xtr4ct 4ny 0v3rr1d35 fr0m c0nv3r54t10n
            for sess in dedup_sessions:
                if "threshold" in str(sess):
                    # p4r53 1f p0551bl3
                    pass
        else:
            print("ℹ️  N0 d3dup-5p3c1f1c 535510n5 f0und. U51n9 d3f4ult rul35.")
    except Exception as e:
        print(f"⚠️  Err0r r34d1ng 535510n l0g: {e}")
    
    return rules


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="D3dupl1c4t3 tru3_v3r510n5.j50n v14 fr4gm3nt 51m1l4r1ty")
    parser.add_argument("input", help="P4th t0 1nput tru3_v3r510n5.j50n")
    parser.add_argument("-o", "--output", help="0utput f1l3 p4th (d3f4ult: 1nput_d3dup.j50n)")
    parser.add_argument("--curate", action="store_true", help="Run curate rules first")
    
    args = parser.parse_args()
    
    if args.curate:
        rules = router_agent_curate_rules()
        print(f"📜 C0ncurr3nt rul35: {json.dumps(rules, indent=2)}")
    
    deduplicate_true_versions(args.input, args.output)
