# CCTV Response Cage

This directory is reserved for human responses emitted by an initiated CCTV board. A response path must be `_tv/responses/<screen>/<id>.md`, where the screen and identifier are controlled by the card contract rather than user-supplied paths.

## Current state

No response-consuming process is enabled. No interactive card in this ICM change set can alter provider routing, application behavior, a GitHub Action, a secret, a device, or a deployment.

## Future use gate

Before adding an interactive checkpoint, its owning ICM process must declare the card identifier, accepted response values, canonical source artifact, consuming process, human authority, and no-response behavior. The consumer must read the response only after the human has acted and must record its result in the canonical ICM artifact.
