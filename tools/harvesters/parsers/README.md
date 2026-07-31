# Harvesters: Parsers

This directory is intended to host session-export parsing and diagnostic scripts that operate on
previously-exported session data (JSON, cookies exports, transcripts). These scripts are NOT
intended to capture credentials from running browsers. They assume you already have exports stored
locally and are used to transform or analyze those exports.

Usage
- Place export files into a local directory and run the parser scripts against them.
- Parsers should never attempt to fetch credentials from live browsers or remote hosts.

Examples
- diag-mistral.cjs: inspects exported cookie files and page state to help diagnose login status.
