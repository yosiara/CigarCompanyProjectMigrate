import sys

for path in sys.path:
    print(path)

try:
    import odoo
    print(f"Ubicación: {odoo.__file__}")
except ImportError as e:
    print(f"\n Error en la importación de odoo")