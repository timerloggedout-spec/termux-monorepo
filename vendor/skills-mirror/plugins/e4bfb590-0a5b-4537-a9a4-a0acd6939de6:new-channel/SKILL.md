---
description: 유튜브 채널 운영 폴더를 새로 만든다 (channel.json, OPERATIONS.md, state.json)
argument-hint: '[폴더 이름]'
allowed-tools: Read, Write, Bash(mkdir:*), Bash(cp:*), Bash(ls:*), AskUserQuestion
---

새 유튜브 채널용 운영 폴더를 만든다. 폴더 이름: `$ARGUMENTS` (비어 있으면 사용자에게 묻는다).

1. 대상 폴더가 이미 있고 `channel.json`이 들어 있으면 덮어쓰지 말고 멈춘다.
2. 사용자에게 아래를 한 번에 묻는다. 모르는 항목은 비워 두고 나중에 채우라고 안내한다.
   - 채널 이름, 핸들, 언어
   - 주제와 톤 (예: "세계 뉴스 해설, 차분하고 근거 중심")
   - 형식: 롱폼 길이/주기, 쇼츠 길이/주기
   - 음성 도구와 voice_id (예: ElevenLabs, MiniMax, Higgsfield)
   - 화면 도구와 스타일
3. 폴더 구조를 만든다:
   ```
   <폴더>/channel.json  OPERATIONS.md  state.json
   <폴더>/research/  content/  production/  runs/
   ```
   `${CLAUDE_PLUGIN_ROOT}/templates/`의 파일을 복사하고 `{{...}}` 자리표시자를 답변으로 채운다.
   `authorization.daily_upload`와 `additional_payments`는 false로 둔다. 사용자가 명시적으로 허락할 때만 바꾼다.
4. 만든 파일 목록과 다음 단계를 짧게 알려 준다:
   - OPERATIONS.md를 읽고 채널에 맞게 문장을 고칠 것
   - 첫 회차는 `/ai-youtube-os:daily <폴더>`로 업로드 없이 만들어 볼 것
