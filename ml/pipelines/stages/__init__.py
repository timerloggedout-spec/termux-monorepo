from ml.pipelines.stages.bind import stage_bind
from ml.pipelines.stages.command_center import stage_command_center
from ml.pipelines.stages.evaluate import stage_evaluate
from ml.pipelines.stages.export import stage_export
from ml.pipelines.stages.features import stage_features
from ml.pipelines.stages.ingest import stage_ingest
from ml.pipelines.stages.monitor import stage_monitor
from ml.pipelines.stages.recon import stage_recon
from ml.pipelines.stages.train import stage_train

STAGES = [
    ("recon", stage_recon),
    ("ingest", stage_ingest),
    ("features", stage_features),
    ("train", stage_train),
    ("evaluate", stage_evaluate),
    ("bind", stage_bind),
    ("export", stage_export),
    ("monitor", stage_monitor),
    ("command_center", stage_command_center),
]
