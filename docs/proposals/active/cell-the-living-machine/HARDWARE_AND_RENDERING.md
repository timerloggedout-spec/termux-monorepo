# Hardware Tiers, Rendering and Mobile-First Delivery

## Priority
Low-tier Android and browser-capable devices are first-class targets. High-fidelity desktop rendering remains available through scalable asset quality and renderer tiers. The project preserves a single simulation and content model across device classes.

## Rendering architecture
The engine decision remains open pending a playable comparison. Godot is a strong initial candidate because its Compatibility renderer targets older mobile/desktop and web, Mobile provides a richer path for newer Vulkan/Metal devices, and Forward+ targets high-end desktop hardware. The final selection follows an instrumented prototype.

| Tier | Target | Rendering strategy | Content budget |
|---|---|---|---|
| L0 | Older Android, integrated graphics, web baseline | Compatibility renderer; baked lighting; simplified materials; low draw calls | Aggressive LOD, small textures, limited transparency and particles |
| L1 | Mainstream Android and low-power laptops | Compatibility or Mobile according to device capability | Instanced geometry, atlases, compressed textures, selective effects |
| L2 | Newer mobile, tablets and capable laptops | Mobile renderer | Richer materials, moderate shadows, selective post-processing |
| L3 | Desktop workstations and gaming systems | Forward+ or engine-equivalent high tier | High-detail geometry, advanced lighting, larger textures and effects |
| L4 | Studio / render-farm / visualization nodes | Offline high-quality Blender rendering and high-end engine capture | High-resolution scientific and cinematic assets |

## Mobile-first rules
- Keep simulation state and visual presentation separate.
- Use deterministic low-cost simulation for the interactive game loop.
- Provide baked, instanced and impostor representations for expensive structures.
- Stream large scientific structures and detailed assets on demand.
- Use progressive mesh levels, texture compression and platform-specific asset variants.
- Profile CPU, GPU, memory, thermal behavior, storage and network on physical devices.
- Preserve readability, input flexibility, text scaling and motion controls at every tier.
- Offer quality presets backed by measured device capability and user choice.
- Keep core exploration and saved projects usable offline after content download.

## Renderer compatibility evidence

Godot 4.7.2 is the provisional prototype lead. The documented Compatibility path supports OpenGL ES 3.0-class Android hardware and Android 7.0, and it is Godot's web renderer. The Mobile renderer uses Vulkan/Metal/Direct3D 12 and targets newer devices; Forward+ is the advanced desktop path. These are engine compatibility floors, not guaranteed performance results.

Unity 6 supports Android Vulkan and OpenGL ES 3.x paths, with automatic API fallback. Unreal's Android path can prefer Vulkan and retain OpenGL ES 3.2 as a fallback. Both remain comparison candidates for the same measured scenes.

Prototype tier mapping:
- L0: Godot Compatibility; OpenGL ES 3.0; baked lighting, reduced materials, strict draw-call/texture budgets.
- L1/L2: Godot Mobile; Vulkan-capable devices; measured shadows and post-processing.
- L3: Godot Forward+ or a validated Unity/Unreal path for desktop workstations.
- Browser: Godot Compatibility baseline, with separate browser-specific memory and download budgets.

Official engine references:
- Godot requirements: https://docs.godotengine.org/en/stable/about/system_requirements.html
- Godot renderer comparison: https://docs.godotengine.org/en/stable/tutorials/rendering/renderers.html
- Unity Android graphics APIs: https://docs.unity3d.com/Manual/class-PlayerSettingsAndroid.html
- Unreal mobile rendering: https://dev.epicgames.com/documentation/en-us/unreal-engine/performance-and-optimization-for-mobile-in-unreal-engine

## Performance gates
Set numeric budgets after measuring the first vertical slice on representative devices. Each benchmark records device model, OS, engine/runtime version, renderer, scene, resolution, thermal state, duration, frame-time percentiles, memory, load time, battery/energy observations and artifact hash.

The release gate uses p50/p95 frame time, memory ceilings, crash-free session rate, cold/warm load time, storage footprint and thermal throttling behavior. A desktop capture alone cannot establish mobile readiness.

## Scientific visualization tiers
- Interactive overview: simplified silhouettes and procedural/instanced structures.
- Mechanism detail: focused protein complexes and membrane machinery.
- Structural inspection: detailed atomic/residue views loaded as a specialist inspection layer.
- Offline showcase: high-quality Blender/Cycles renders and turntables for education, marketing and specialist review.

## AMD and NVIDIA acceleration
GPU-specific acceleration is an optional production capability. Runtime support falls back to the device's supported graphics path. AMD ROCm and NVIDIA CUDA/Omniverse workloads belong in studio, research, training and render infrastructure profiles; they remain separate from the low-tier client baseline.

## References
- https://docs.godotengine.org/en/stable/tutorials/rendering/renderers.html
- https://docs.godotengine.org/en/stable/about/system_requirements.html
- https://docs.godotengine.org/en/3.6/tutorials/platform/mobile_rendering_limitations.html
