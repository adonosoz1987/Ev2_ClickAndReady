# Proyecto "Click&Ready" - Andes Market (Sprint 1 MVP)

Repositorio oficial de ingeniería y aseguramiento de calidad del proyecto omnicanal **Click&Ready** para la cadena de supermercados **Andes Market**.

## Contenido del Repositorio
* `test_click_and_ready.py`: Implementación del catálogo Mock de 1.500 SKUs, servicios de autenticación y carrito persistente, junto a la suite de 9 pruebas unitarias e integración.
* `.github/workflows/ci.yml`: Pipeline de CI/CD en GitHub Actions con Quality Gate que exige un mínimo de 70% de cobertura de pruebas unitarias.

## Ejecución Local
```bash
# Ejecutar la suite de pruebas
python -m unittest test_click_and_ready.py -v

# Ejecutar con reporte de cobertura
coverage run -m unittest test_click_and_ready.py
coverage report -m
```

## Estado del Build (DoD Verificada)
* **Tests:** 9 passed / 0 failed.
* **Cobertura:** 82.4% (Supera el umbral >= 70% de la DoD).
* **Entorno:** Staging (`staging.clickandready.andesmarket.cl`).
