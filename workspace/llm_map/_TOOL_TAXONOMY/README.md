# Tool Taxonomy for LLM Agents

**Snapshot:** 3,388 tools · 104 tags · 25 roles  
**Last tracked snapshot commit:** 2026-07-30T06:47:18Z (`ee1807049fd93d087bc14055b2ae6cbffb5dbf82`)

## Table of Contents

### Roles (pre-curated tool profiles)

| Role | Tools |
|---|---:|
| `android_reverser` | 109 tools |
| `apk_reverse_engineer` | 109 tools |
| `archwiz` | 167 tools |
| `ast_hash_agent` | 48 tools |
| `c_cpp_developer` | 173 tools |
| `data_scientist` | 19 tools |
| `debugger` | 16 tools |
| `devops_engineer` | 74 tools |
| `forensic_analyst` | 117 tools |
| `fortran_developer` | 8 tools |
| `full_stack_dev` | 26 tools |
| `llm_agent_dev` | 34 tools |
| `lua_developer` | 58 tools |
| `php_developer` | 49 tools |
| `python_developer` | 91 tools |
| `python_package_dev` | 92 tools |
| `recon_agent` | 268 tools |
| `rust_developer` | 34 tools |
| `security_researcher` | 62 tools |
| `shell_power_user` | 189 tools |
| `synthegration_dev` | 56 tools |
| `system_architect` | 7 tools |
| `termux_operator` | 154 tools |
| `web_frontend_dev` | 55 tools |
| `web_reverse_engineer` | 54 tools |

Load any role with: `cat roles/<name>.json | jq '.tools'`

### Tags

alias_tools, archwiz, ast_tools, bc_tools, benchmarking, binary_analysis, c_cpp, compression, custom_tools, data_formats, database, development, file_search, font_rendering, forensics, fortran, gflags_tools, glib_tools, gnome_tools, graphics, gstreamer_tools, gtk3_tools, gtk4_tools, gtk_tools, hardware_info, harmony_hub, hashing, image_tools, javascript, libacl_tools, libassuan_tools, libavif_tools, libbs2b_tools, libcaca_tools, libcairo_tools, libcanberra_tools, libcap_tools, libcurl_tools, libdav1d_tools, libde265_tools, libdisplay_tools, libfyaml_tools, libgcrypt_tools, libgit2_tools, libgpg_tools, libhyphen_tools, libidn2_tools, libksba_tools, libnotify_tools, libnpth_tools, libnspr_tools, libnss_tools, libpng_tools, libpsl_tools, librsvg_tools, libsecret_tools, libtasn1_tools, libvmaf_tools, libvte_tools, libwayland_tools, libwebp_tools, libwnck_tools, libxfce4ui_tools, libxfce4util_tools, libxkbcommon_tools, libxml2_tools, libxmlb_tools, libxslt_tools, libzip_tools, libzmq_tools, lilv_tools, llm_orchestration, lua, lua52_tools, lua54_tools, lua55_tools, multimedia, network_tools, obconf_tools, other, package_management, perl, php, printing, python, python_toolchain, recon_intel, ref_templates_tools, reverse_engineering, rust, science, security, shell_customization, shell_environment, synthegration, system_monitor, system_utility, terminal_multiplexer, termux_api, text_processing, unknown_tools, virtualization, x11_utils, xfce_tools

---

## Quick Start for an LLM

1. **ToC** → `cat TOOL_TAXONOMY.json | jq '.metadata'`
2. **Pick a role** → `cat roles/<name>.json`
3. **Find a tool** → `taxfind <name>`
4. **Get tool JSON** → `taxapply <name>`
5. **See what changed** → `taxdiff`

---

## Methods (full command reference)

| Method | Command |
|---|---|
| Table of Contents | `jq '.metadata' TOOL_TAXONOMY.json` |
| List roles | `jq '.metadata.roles' TOOL_TAXONOMY.json` |
| Get role tools | `jq '.tools' roles/<name>.json` |
| Search tool | `taxfind <name>` |
| Get tool JSON | `taxapply <name>` |
| See changes | `taxdiff` |
| Create role | `taxtool --add-role <name>` |
| Update index | `taxtool` |
| Fast role refresh | `taxrefactor` |

## Snapshot provenance

- `all_tools.jsonl` contains 3,388 valid JSONL records with 243 distinct package/source groups.
- `TOOL_TAXONOMY.json` reports 3,388 tools, 104 tags and 25 roles.
- `categories/` contains 103 generated category views; `roles/` contains 25 role JSON files plus directory metadata.
- `REPO_INFO` records `NO_REMOTE`. This snapshot documents a local Termux environment at the tracked commit; it does not establish current tool installation or authorization.
- `build_tool_taxonomy.sh` invokes Termux package and local environment scanners. Run it only in the intended Termux environment after reviewing its source.
