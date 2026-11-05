# Proyecto "Click&Ready" - Andes Market (Sprint 1 MVP)

Repositorio oficial de aseguramiento de calidad e ingeniería de software para el MVP **Click&Ready** de **Andes Market**.

El objetivo del Sprint 1 es validar el flujo inicial de autenticación, catálogo con 1.500 SKUs vía API Mock y gestión de carrito persistente en ambiente de staging previo al periodo de alta demanda de Fiestas Patrias.

---

## Estado del Build y Quality Gate (DoD Verificada)
- **Pipeline CI/CD:** GitHub Actions (`ci.yml`) en estado **Passing / Green**.
- **Pruebas Automatizadas:** 9 passed / 0 failed (0.024s).
- **Cobertura de Código:** **90%** (supera el umbral mínimo no negociable >= 70% estipulado en la Definition of Done).
- **Defectos Críticos:** 0 defectos P0/P1 abiertos.
- **Ambiente de Despliegue:** Staging (`[https://staging.clickandready.andesmarket.cl](https://staging.clickandready.andesmarket.cl)`).

---

## Trazabilidad de Historias del Sprint 1 (DoD Compliance)

| PBI | Descripción | Alcance Técnico | Cobertura | Estado DoD |
| :---: | :--- | :--- | :---: | :---: |
| **PBI-01** | Registro e Inicio de Sesión | Validación de correo, hashing de clave y emisión de JWT seguro | 88% | **Done** |
| **PBI-02** | Búsqueda y Catálogo ERP | Catálogo mockeado de 1.500 SKUs, búsqueda predictiva y filtros | 86% | **Done** |
| **PBI-03** | Carrito de Compras | Persistencia en sesión, validación de stock y cálculo de IVA | 93% | **Done** |

---

## Ejecución Local de Pruebas

Para replicar localmente la suite de pruebas y el reporte de cobertura:

# 1. Clonar el repositorio
git clone https://github.com/adonosoz1987/Ev2_ClickAndReady.git
cd Ev2_ClickAndReady

# 2. Instalar dependencias
pip install coverage pytest

# 3. Ejecutar pruebas unitarias e integración
python -m unittest test_click_and_ready.py -v

# 4. Generar reporte de cobertura
coverage run -m unittest test_click_and_ready.py
coverage report -m