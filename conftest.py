"""conftest.py — configuración global de pytest."""
import os
import sys

# Asegura que src/ esté en el path para todos los tests
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
