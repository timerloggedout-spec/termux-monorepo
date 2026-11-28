# Visual Production Pipeline and Blender MCP

## Production architecture
Blender is the high-quality authoring, scientific visualization, animation, procedural modeling and offline-rendering tool. The game engine consumes optimized, versioned assets. The same source asset may produce high-detail workstation output and mobile-ready derivatives.

Pipeline: source data → Blender scene → validated asset build → glTF/USD interchange → engine import → device-tier derivatives → visual QA → release manifest.

## Blender MCP selection
Primary candidate: DCC-MCP Blender adapter — https://github.com/dcc-mcp/dcc-mcp-blender

The adapter embeds a Streamable HTTP MCP server in Blender and provides typed tools for scene inspection, modeling, mesh/UV operations, rigging, materials, rendering, interchange, validation and asset-pipeline manifests. Its repository documents a DCC-MCP CLI and agent skill workflow. The project pins candidate release v0.2.30 at source commit 5a9d7d489ebf0d6af5c5e3166453eeee5a7fce66 (PyPI package dcc-mcp-blender==0.2.30; wheel SHA-256 2b0b3cd491e139fd7c01cd7859bb8155a7e7115e05c76b1f306db0856f285d4e). Upstream CI lists Blender 4.5 LTS and 5.2 targets. The repository setup guide is tools/blender-mcp/README.md; local installation and live-session verification remain pending.

Secondary candidate: MCP for Blender — https://github.com/ahujasid/mcp-for-blender

This widely used community integration identifies itself as a third-party Blender integration. Its socket server has no authentication or encryption and can execute Python in Blender; safe mode and localhost-only binding are required considerations. It remains a fallback where typed DCC-MCP coverage is unavailable.

No Blender-project-published official MCP server is assumed. Both integrations are third-party tools with independent licenses, security models and release cadences.

## Repository integration
The repository maintains a versioned Blender tool profile in GAME_DEVELOPMENT_TOOL_PROFILES.json; this setup and security runbook; an asset build manifest schema; Blender background-mode validation scripts; CI checks for glTF/GLB structure, file size, transforms, scale, materials, animation clips and provenance; optional MCP client configuration templates under tools/blender-mcp/.

The repository records tool versions and configuration templates. Each developer installs the adapter in their local Blender/MCP host. Credentials, machine-specific endpoints and local paths remain in local configuration or approved secret stores.

## DCC-MCP developer setup

The game repository pins the adapter in tools/blender-mcp/manifest.yaml and provides the developer setup in tools/blender-mcp/README.md.
1. Install Blender and the DCC-MCP Blender adapter from its official release/extension distribution.
2. Install the DCC-MCP CLI using the upstream installation instructions.
3. Enable the adapter in Blender and launch a local Blender session.
4. Run dcc-mcp-cli list and verify that the session reports dcc_type=blender.
5. Use dcc-mcp-cli search --query "<task>" --dcc-type blender to discover a typed tool.
6. Use dcc-mcp-cli describe <tool-slug> before invoking a tool.
7. Inspect the scene, make one coherent edit, render a preview and inspect the result.
8. Run validation and save the editable Blender source plus approved interchange artifacts.

Official setup details: https://github.com/dcc-mcp/dcc-mcp-blender

## Safe operating profile
- Bind the Blender adapter to loopback by default.
- Use typed tool operations and approved skills for routine modeling and rendering.
- Scope file access to the active project workspace and approved asset roots.
- Treat imported scripts, scene files, textures and external assets as untrusted until reviewed.
- Use a dedicated Blender process for automated jobs and preserve a clean baseline file.
- Record every scene revision, tool version, source asset, output checksum and validation result.
- Require human review before external publication, paid asset acquisition or fabrication handoff.

## Scientific visualization
Molecular Nodes is a candidate Blender extension for structure-aware visualization. Structural accessions, chain/entity identifiers, coordinate revision and source evidence travel with the asset manifest. The asset pipeline records whether a model is experimentally determined or computationally predicted and preserves method, resolution/confidence and construct context.

## Render and export profiles
- Mobile asset profile: low polygon count, baked lighting, atlas textures, limited transparency, compressed textures and LODs.
- Standard real-time profile: optimized PBR materials, rigged animations and glTF delivery.
- Scientific-detail profile: source-faithful structures with selective atom/residue visibility and interactive inspection.
- Cinematic profile: Blender Cycles/Eevee output, layered passes and approved post-processing.

## Verification
A Blender-produced asset passes when the source scene is saved, its build manifest resolves, geometry and scale checks pass, materials and animation references resolve, target-engine import succeeds, device-tier derivatives exist, and a rendered image is reviewed. A successful script exit alone is insufficient visual evidence.
