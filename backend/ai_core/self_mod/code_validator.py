import re


class CodeValidator:
    """Validates generated code before applying"""

    @staticmethod
    def validate(code: str, file_path: str) -> dict:
        """Complete validation"""

        errors = []
        warnings = []

        # Check not empty
        if not code or len(code.strip()) < 10:
            errors.append("Code is empty or too short")
            return {"valid": False, "errors": errors, "warnings": warnings}

        # Check no markdown blocks
        if code.strip().startswith('```') or '```' in code[-50:]:
            errors.append("Code contains markdown blocks")

        # File-specific validation
        if file_path.endswith('.tsx') or file_path.endswith('.ts'):
            result = CodeValidator._validate_tsx(code)
            errors.extend(result['errors'])
            warnings.extend(result['warnings'])
        elif file_path.endswith('.py'):
            result = CodeValidator._validate_python(code)
            errors.extend(result['errors'])
            warnings.extend(result['warnings'])

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "line_count": code.count('\n') + 1,
        }

    @staticmethod
    def _validate_tsx(code: str) -> dict:
        """Validate TSX/TS code"""
        errors = []
        warnings = []

        # Check for common typos in imports (AI mistakes)
        common_typos = {
            "'eact'": "'react'",
            '"eact"': '"react"',
            "'ext/": "'next/",
            '"ext/': '"next/',
            "'act'": "'react'",
            '"act"': '"react"',
            "'eact-dom'": "'react-dom'",
            '"eact-dom"': '"react-dom"',
            "'ext-dom'": "'react-dom'",
            "from 'eact": "from 'react",
            'from "eact': 'from "react',
        }

        for bad, good in common_typos.items():
            if bad in code:
                errors.append(f"Typo detected: {bad} should be {good}")

        # Check react import exists if using hooks
        if any(hook in code for hook in ['useState', 'useEffect', 'useRef', 'useMemo', 'useCallback']):
            if "from 'react'" not in code and 'from "react"' not in code:
                errors.append("Missing React import for hooks")

        # Check for export default (client components)
        if 'export default' not in code:
            errors.append("Missing 'export default' statement")

        # Check for balanced braces
        open_braces = code.count('{')
        close_braces = code.count('}')
        if open_braces != close_braces:
            errors.append(f"Unbalanced braces: {open_braces} '{{' vs {close_braces} '}}'")

        # Check for balanced parens
        open_parens = code.count('(')
        close_parens = code.count(')')
        if open_parens != close_parens:
            errors.append(f"Unbalanced parens: {open_parens} '(' vs {close_parens} ')'")

        # Check JSX tags are balanced
        if '<div' in code:
            open_divs = len(re.findall(r'<div[\s>]', code))
            close_divs = code.count('</div>')
            self_closing = len(re.findall(r'<div[^>]*/>', code))
            if open_divs != (close_divs + self_closing):
                warnings.append("Potential unbalanced div tags")

        if '<main' in code:
            open_mains = len(re.findall(r'<main[\s>]', code))
            close_mains = code.count('</main>')
            if open_mains != close_mains:
                errors.append("Unbalanced <main> tags")

        if '<form' in code:
            open_forms = len(re.findall(r'<form[\s>]', code))
            close_forms = code.count('</form>')
            self_closing = len(re.findall(r'<form[^>]*/>', code))
            if open_forms != (close_forms + self_closing):
                errors.append("Unbalanced <form> tags")

        if '<button' in code:
            open_btns = len(re.findall(r'<button[\s>]', code))
            close_btns = code.count('</button>')
            self_closing = len(re.findall(r'<button[^>]*/>', code))
            if open_btns != (close_btns + self_closing):
                warnings.append("Potential unbalanced button tags")

        # Check for 'use client' if using hooks
        if any(hook in code for hook in ['useState', 'useEffect', 'useRouter']):
            if "'use client'" not in code and '"use client"' not in code:
                errors.append("Uses hooks but missing 'use client' directive")

        # Check for return statement in functions
        if 'export default function' in code:
            if 'return' not in code:
                errors.append("Component missing return statement")

        # Check imports are complete (from 'somewhere')
        import_lines = re.findall(r'^import\s+.*', code, re.MULTILINE)
        for line in import_lines:
            if 'from' in line:
                # Check has quotes around the module
                if not re.search(r"from\s+['\"].+['\"]", line):
                    errors.append(f"Malformed import: {line[:60]}")

        # Check next/navigation imports
        if 'useRouter' in code and "next/navigation" not in code:
            errors.append("useRouter used but 'next/navigation' not imported")

        # Ends properly
        stripped = code.strip()
        if not stripped.endswith('}') and not stripped.endswith(';') and not stripped.endswith(')'):
            warnings.append("File may be incomplete (unusual ending)")

        return {"errors": errors, "warnings": warnings}

    @staticmethod
    def _validate_python(code: str) -> dict:
        """Validate Python code"""
        errors = []
        warnings = []

        try:
            compile(code, '<string>', 'exec')
        except SyntaxError as e:
            errors.append(f"Syntax error at line {e.lineno}: {e.msg}")

        for open_c, close_c in [('(', ')'), ('[', ']'), ('{', '}')]:
            if code.count(open_c) != code.count(close_c):
                errors.append(f"Unbalanced {open_c}{close_c}")

        return {"errors": errors, "warnings": warnings}

    @staticmethod
    def compare_with_original(new_code: str, original_code: str) -> dict:
        """Compare new code with original for sanity check"""

        original_lines = original_code.count('\n') + 1
        new_lines = new_code.count('\n') + 1

        warnings = []

        if original_lines > 20 and new_lines < original_lines * 0.3:
            warnings.append(f"New code much smaller ({new_lines} vs {original_lines} lines)")

        if 'import' in original_code and 'import' not in new_code:
            warnings.append("Original had imports but new code doesn't")

        return {"warnings": warnings}