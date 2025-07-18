#!/usr/bin/env python3
"""
Comprehensive whitespace fixer for Klipper code standards.
This script fixes common whitespace issues in Python and C files.
"""

import os
import re
import sys
import argparse


def fix_python_line(line, line_num):
    """Fix a single Python line to meet Klipper standards."""
    original_line = line
    
    # Remove trailing whitespace
    line = line.rstrip()
    
    # Skip certain types of lines that are hard to break
    if (line.strip().startswith('#') or 
        line.strip().startswith('"""') or 
        line.strip().startswith("'''") or
        '"""' in line or
        "'''" in line):
        return line
    
    # If line is not too long, return as-is
    if len(line) <= 80:
        return line
    
    # Get indentation
    indent = len(line) - len(line.lstrip())
    indent_str = line[:indent]
    
    # Try various strategies to break long lines
    fixed_line = try_break_string_concat(line, indent_str)
    if fixed_line != line:
        return fixed_line
    
    fixed_line = try_break_function_args(line, indent_str)
    if fixed_line != line:
        return fixed_line
    
    fixed_line = try_break_operators(line, indent_str)
    if fixed_line != line:
        return fixed_line
    
    fixed_line = try_break_list_dict(line, indent_str)
    if fixed_line != line:
        return fixed_line
    
    # If we can't break it nicely, return original
    return line


def try_break_string_concat(line, indent_str):
    """Try to break string concatenation."""
    if ' + ' in line and ('"' in line or "'" in line):
        # Look for string concatenation patterns
        parts = line.split(' + ')
        if len(parts) > 1:
            # Check if we can break after a string
            for i in range(len(parts) - 1):
                if ('"' in parts[i] or "'" in parts[i]):
                    left = ' + '.join(parts[:i+1])
                    right = ' + '.join(parts[i+1:])
                    if len(left) <= 80:
                        return left + ' +\n' + indent_str + '    ' + right
    return line


def try_break_function_args(line, indent_str):
    """Try to break long function calls."""
    # Look for function calls with multiple arguments
    if '(' in line and ')' in line and ', ' in line:
        # Find the function call
        paren_start = line.find('(')
        paren_end = line.rfind(')')
        
        if paren_start != -1 and paren_end != -1:
            before_paren = line[:paren_start + 1]
            args_part = line[paren_start + 1:paren_end]
            after_paren = line[paren_end:]
            
            # Split arguments
            args = []
            current_arg = ''
            paren_depth = 0
            quote_char = None
            
            for char in args_part:
                if char in ['"', "'"] and quote_char is None:
                    quote_char = char
                elif char == quote_char:
                    quote_char = None
                elif char == '(' and quote_char is None:
                    paren_depth += 1
                elif char == ')' and quote_char is None:
                    paren_depth -= 1
                elif char == ',' and paren_depth == 0 and quote_char is None:
                    args.append(current_arg.strip())
                    current_arg = ''
                    continue
                
                current_arg += char
            
            if current_arg.strip():
                args.append(current_arg.strip())
            
            # Try to break the arguments
            if len(args) > 1:
                # Break after the opening parenthesis
                result = before_paren + '\n'
                for i, arg in enumerate(args):
                    if i == 0:
                        result += indent_str + '    ' + arg
                    else:
                        result += ',\n' + indent_str + '    ' + arg
                result += after_paren
                
                # Check if this improves line length
                max_line_len = max(len(l) for l in result.split('\n'))
                if max_line_len <= 80:
                    return result
    
    return line


def try_break_operators(line, indent_str):
    """Try to break on logical operators."""
    operators = [' and ', ' or ', ' if ', ' else ']
    
    for op in operators:
        if op in line:
            # Find the best place to break
            parts = line.split(op)
            if len(parts) > 1:
                # Try breaking after each operator
                for i in range(len(parts) - 1):
                    left = op.join(parts[:i+1])
                    right = op.join(parts[i+1:])
                    if len(left) <= 80:
                        continuation_indent = indent_str + '       '
                        return left + op.strip() + '\n' + continuation_indent + right
    
    return line


def try_break_list_dict(line, indent_str):
    """Try to break lists or dictionaries."""
    if '[' in line and ']' in line and ', ' in line:
        # Handle list literals
        bracket_start = line.find('[')
        bracket_end = line.rfind(']')
        
        if bracket_start != -1 and bracket_end != -1:
            before_bracket = line[:bracket_start + 1]
            list_content = line[bracket_start + 1:bracket_end]
            after_bracket = line[bracket_end:]
            
            # Split list items
            items = [item.strip() for item in list_content.split(',')]
            
            if len(items) > 1:
                result = before_bracket + '\n'
                for i, item in enumerate(items):
                    if item:  # Skip empty items
                        if i == 0:
                            result += indent_str + '    ' + item
                        else:
                            result += ',\n' + indent_str + '    ' + item
                result += '\n' + indent_str + after_bracket
                
                # Check if this improves line length
                max_line_len = max(len(l) for l in result.split('\n'))
                if max_line_len <= 80:
                    return result
    
    return line


def fix_c_line(line, line_num):
    """Fix a single C line to meet Klipper standards."""
    # Remove trailing whitespace
    line = line.rstrip()
    
    # Skip preprocessor directives and comments
    if (line.strip().startswith('#') or 
        line.strip().startswith('//') or
        line.strip().startswith('/*')):
        return line
    
    # For C files, we're more conservative about line breaking
    # Just remove trailing whitespace for now
    return line


def fix_file_whitespace(file_path):
    """Fix whitespace issues in a single file."""
    if not os.path.exists(file_path):
        return False
    
    print(f"Processing {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        print(f"Warning: Could not read {file_path} as UTF-8, skipping")
        return False
    
    fixed_lines = []
    is_python = file_path.endswith('.py')
    is_c = file_path.endswith('.c') or file_path.endswith('.h')
    
    for line_num, line in enumerate(lines, 1):
        # Remove newline for processing
        line = line.rstrip('\n\r')
        
        if is_python:
            fixed_line = fix_python_line(line, line_num)
        elif is_c:
            fixed_line = fix_c_line(line, line_num)
        else:
            # For other files, just remove trailing whitespace
            fixed_line = line.rstrip()
        
        # Handle multi-line results
        if '\n' in fixed_line:
            fixed_lines.extend(fixed_line.split('\n'))
        else:
            fixed_lines.append(fixed_line)
    
    # Remove trailing empty lines
    while fixed_lines and fixed_lines[-1] == '':
        fixed_lines.pop()
    
    # Add exactly one newline at the end
    if fixed_lines:
        fixed_lines.append('')
    
    # Write the fixed content
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(fixed_lines))
        return True
    except Exception as e:
        print(f"Error writing {file_path}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Fix whitespace issues in files to meet Klipper standards"
    )
    parser.add_argument(
        'files', 
        nargs='+', 
        help='Files to fix'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )
    
    args = parser.parse_args()
    
    success_count = 0
    total_count = len(args.files)
    
    for file_path in args.files:
        if fix_file_whitespace(file_path):
            success_count += 1
            if args.verbose:
                print(f"✓ Fixed {file_path}")
        else:
            if args.verbose:
                print(f"✗ Failed to fix {file_path}")
    
    print(f"Fixed {success_count}/{total_count} files")
    return 0 if success_count == total_count else 1


if __name__ == "__main__":
    sys.exit(main()) 