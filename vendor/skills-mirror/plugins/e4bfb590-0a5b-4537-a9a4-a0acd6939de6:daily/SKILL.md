---
description: 오늘 회차를 OPERATIONS.md 순서대로 제작한다 (중복 제작 방지 포함)
argument-hint: '<채널 폴더>'
---

채널 폴더 `$ARGUMENTS`에서 오늘 회차를 만든다.

1. `channel-operations` 스킬의 원칙을 따른다.
2. `$ARGUMENTS/OPERATIONS.md`를 처음부터 끝까지 읽고, 그 문서의 "시작 전 확인"을 먼저 수행한다.
   오늘 슬롯이 이미 채워져 있으면 그 사실만 보고하고 끝낸다.
3. 문서의 7단계를 순서대로 수행한다. 각 단계가 끝날 때마다 `runs/YYYY-MM-DD/manifest.json`에 결과 파일 경로와 상태를 기록한다.
4. 음성·영상 생성 도구가 이 환경에 연결돼 있지 않으면 대본, 장면 목록(`scenes.json`), 생성 프롬프트까지만 만들고
   "사람이 해야 할 일" 목록으로 정리해 멈춘다. 없는 도구를 쓴 것처럼 보고하지 않는다.
5. `channel.json`의 `authorization.daily_upload`가 false면 업로드하지 않고 최종 파일 경로만 알려 준다.
6. 마지막에 `state.json`을 갱신하고, 오늘 한 일 / 쓴 크레딧 / 막힌 점을 3줄 이내로 보고한다.
