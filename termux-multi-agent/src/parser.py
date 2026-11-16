import re

def parse_compiler_logs(raw_stderr, language):
    condensed_errors = []
    if language in ['js', 'mjs']:
        matches = re.findall(r'(ReferenceError|TypeError|SyntaxError): (.*?)\n', raw_stderr)
        for err_type, message in matches:
            condensed_errors.append(f"[{err_type}] -> {message}")
    elif language == 'rs':
        matches = re.findall(r'error\[E\d+\]: (.*?)\n\s+--> (.*?):(\d+):(\d+)', raw_stderr)
        for desc, file, line, col in matches:
            condensed_errors.append(f"[RustError] {desc} (File: {file} Line: {line})")
    elif language == 'py':
        matches = re.findall(r'(\w+Error): (.*?)\n', raw_stderr)
        for err_type, message in matches:
            condensed_errors.append(f"[PythonError] {err_type}: {message}")
    return "\n".join(condensed_errors) if condensed_errors else "Execution Status: Clear compilation."