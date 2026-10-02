# Ancestor-push workflow noise

A push of an already-reachable ancestor can schedule that commit's workflow file without moving the branch tip. Run `37071088656` and its siblings on `0b135032108bc0cb5ceda8a62cc1f2638fcf55f5` are this class: zero-job filename failures, tip stayed `20cfd74ea7f99a664098d695f808756409fd6e3b`.

`actions-run-watcher` classifies `compare(sha...branch).status == ahead` and `jobs.total_count == 0` as `ancestor_push_noise` and does not open an incident. A failure that executed jobs is still notified.

Ruleset `master-no-rewind` (id 24394235) remains the ref-update control. This classifier is notification hygiene, not a bypass.
