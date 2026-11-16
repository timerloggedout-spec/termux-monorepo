# routed-dispatch — evidence packets

One JSON per scored dispatch: the committed evidence packet the ATES judge
consumed (PR, gates, merge state, task, diff summary), written by the
fan-out's score phase beside the record it scored. Evaluators consume only
committed evidence — the packet of record lives here.
