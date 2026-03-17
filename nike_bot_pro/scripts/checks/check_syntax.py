#!/usr/bin/env python
"""Validar sintaxis del worker"""
import ast
import sys

try:
    with open('runtime/worker.py', 'r') as f:
        code = f.read()
    
    ast.parse(code)
    print("✅ runtime/worker.py - SYNTAX VALID")
    sys.exit(0)
except SyntaxError as e:
    print(f"❌ SYNTAX ERROR: {e}")
    sys.exit(1)
