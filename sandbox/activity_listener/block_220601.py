', m.get('content',''), re.DOTALL):
        code = match.group(1).strip()
        if len(code) >= 30: manifest.append({'conversation_id': SID, 'message_role': m.get('role','user').upper(), 'message_timestamp': m.get('inserted_at', 0), 'code': code, 'code_hash': hashlib.sha256(code.encode()).hexdigest()[:16]})
out_dir = HOME / f'storage/downloads/synthegration_exports/{SID}'
out_dir.mkdir(parents=True, exist_ok=True)
(out_dir / 'manifest.json').write_text(json.dumps(manifest))
print(f'{len(manifest)} blocks exported.')
PYEOF