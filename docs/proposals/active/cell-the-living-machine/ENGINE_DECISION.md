# Engine Evaluation and Provisional Prototype Decision

## Decision

Use **Godot 4.7.2 as the first prototype candidate**, with the Compatibility renderer as the low-tier Android/browser baseline and the Mobile renderer as the higher-tier mobile path. Keep the engine choice provisional until the same factory-cell and membrane scenes pass the physical-device benchmark matrix.

The engine-neutral factory-cell reference kernel remains the behavior contract. Engine-specific code consumes the same scenario inputs and produces comparable metrics and replay snapshots.

## Why Godot leads the first prototype

Godot's current renderer model provides three clear tiers:

- Compatibility: OpenGL-based; targets older mobile, older desktop and web; supports OpenGL ES 3.0-class mobile hardware and Android 7.0 in the documented compatibility path.
- Mobile: Vulkan/Metal/Direct3D 12 path for newer mobile and desktop hardware; supports richer rendering with a smaller feature set than Forward+.
- Forward+: high-end desktop rendering and advanced visual features.

Godot's stable system requirements document low-end mobile export targets and a separate web target. Its Android download page currently lists Godot 4.7.2 and minimum OpenGL ES 3.0-compatible hardware. These make Godot a strong first candidate for the low-tier baseline.

Official references:
- https://docs.godotengine.org/en/stable/about/system_requirements.html
- https://docs.godotengine.org/en/stable/tutorials/rendering/renderers.html
- https://godotengine.org/download/android/

## Comparison set

| Candidate | Strengths for this product | Evaluation focus |
|---|---|---|
| Godot 4.7.2 | Compatibility renderer for older mobile and web; Mobile renderer for newer devices; open engine; GDScript/C# options; straightforward glTF workflow. | Confirm large scene, molecular visualization, UI complexity, mobile thermal behavior and asset pipeline. |
| Unity 6 + URP | Mature Android deployment; Vulkan and OpenGL ES 3.x graphics paths; broad ecosystem and tooling. | Compare low-tier memory, build size, runtime overhead, licensing/terms and team workflow. |
| Unreal Engine 5 | High-end rendering, robust 3D tools and mobile renderer with device profiles. | Validate low-tier package size, memory, frame time, shader complexity and development overhead. |
| Browser runtime | Immediate reach and easy sharing; useful for lightweight exploration and portfolio viewers. | WebGL2/WebGPU compatibility, memory, download size, mobile browser stability and offline support. |

## Prototype benchmark

Build the same two scenes in the leading candidate:
1. Industrial factory cell: input storage, transport, processor, power, sensor, output inspection and live metrics.
2. Biological membrane: one membrane, three mechanisms, source-linked labels and a bounded state-transition simulation.

Measure on physical low-tier Android, mainstream Android, current Android, low-power laptop and desktop workstation. Record device, OS, engine, renderer, resolution, scene hash, frame-time p50/p95, memory, cold/warm load, thermal behavior, battery/energy observations, package size and crash-free session results.

## Visual quality strategy

Blender supplies high-fidelity authoring, scientific visualization, animation and offline renders. Runtime assets are exported as optimized glTF/GLB; OpenUSD is used for studio interchange and digital-twin composition. A single source asset produces mobile LODs, baked lighting, atlases and compressed textures; standard real-time PBR assets; specialist structural-detail assets; and high-resolution offline renders and turntables.

This separates visual-authorship quality from the minimum runtime hardware tier.

## Exit criteria for final engine selection

1. Both scenes run on the low-tier Compatibility target with acceptable frame-time, memory, startup and thermal behavior.
2. The same deterministic scenario results match the reference kernel.
3. Blender-to-engine import and asset validation are reproducible.
4. Touch, accessibility, UI scaling and offline exploration pass on physical devices.
5. The selected engine supports the release, contribution, licensing and long-term maintenance model.

Until these gates pass, Godot is the prototype lead and the engine selection remains provisional.
