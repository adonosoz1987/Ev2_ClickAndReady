
import unittest
import json
import re
import time

# --- 1. SIMULACIÓN DE CAPA DE DOMINIO Y API MOCK (ANDES MARKET) ---

class MockERPDatabase:
    """Simula el catálogo de 1.500 SKUs del ERP corporativo de Andes Market."""
    def __init__(self):
        self.products = []
        categories = ["Carnes y Parrilla", "Bebidas y Licores", "Lácteos y Frescos", "Abarrotes", "Panadería"]
        # Generamos los 1.500 SKUs
        for i in range(1, 1501):
            cat = categories[i % len(categories)]
            self.products.append({
                "sku": f"SKU-{i:04d}",
                "name": f"Producto Andes {i} {cat}",
                "category": cat,
                "price": 1000 + (i * 15),
                "stock": 50 + (i % 30),
                "active": True
            })

    def search(self, query=None, category=None, limit=20):
        results = self.products
        if category:
            results = [p for p in results if p["category"].lower() == category.lower()]
        if query:
            q = query.lower()
            results = [p for p in results if q in p["name"].lower() or q in p["sku"].lower()]
        return results[:limit]


class AuthService:
    """PBI-01: Servicio de Registro y Autenticación con JWT simulado."""
    def __init__(self):
        self.users = {}

    def register(self, email, password):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return {"status": 400, "error": "Email inválido"}
        if len(password) < 8 or not any(c.isdigit() for c in password) or not any(c.isupper() for c in password):
            return {"status": 400, "error": "Contraseña no cumple requisitos de seguridad"}
        if email in self.users:
            return {"status": 409, "error": "Usuario ya existe"}
        
        self.users[email] = {
            "password_hash": f"bcrypt$12${hash(password)}",
            "created_at": time.time()
        }
        return {"status": 201, "message": "Usuario registrado exitosamente"}

    def login(self, email, password):
        user = self.users.get(email)
        if not user or user["password_hash"] != f"bcrypt$12${hash(password)}":
            return {"status": 401, "error": "Credenciales inválidas"}
        # Token JWT simulado
        token = f"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.user_{email[:4]}.sig"
        return {"status": 200, "token": token, "email": email}


class CartService:
    """PBI-03: Servicio de Carrito de Compras Persistente con cálculo de IVA."""
    IVA_RATE = 0.19

    def __init__(self, erp_db):
        self.erp_db = erp_db
        self.sessions = {}  # Simula Redis

    def add_or_update_item(self, session_id, sku, quantity):
        if quantity <= 0:
            return {"status": 400, "error": "Cantidad debe ser mayor a 0"}
        
        # Validar existencia en catálogo ERP
        product = next((p for p in self.erp_db.products if p["sku"] == sku), None)
        if not product:
            return {"status": 404, "error": "Producto no encontrado"}
        if product["stock"] < quantity:
            return {"status": 400, "error": "Stock insuficiente"}

        if session_id not in self.sessions:
            self.sessions[session_id] = {}

        self.sessions[session_id][sku] = {
            "name": product["name"],
            "unit_price": product["price"],
            "quantity": quantity
        }
        return {"status": 200, "cart": self.get_cart(session_id)}

    def remove_item(self, session_id, sku):
        if session_id in self.sessions and sku in self.sessions[session_id]:
            del self.sessions[session_id][sku]
        return {"status": 200, "cart": self.get_cart(session_id)}

    def get_cart(self, session_id):
        items = self.sessions.get(session_id, {})
        subtotal = sum(item["unit_price"] * item["quantity"] for item in items.values())
        iva = round(subtotal * self.IVA_RATE)
        total = subtotal + iva
        return {
            "session_id": session_id,
            "items": items,
            "subtotal": subtotal,
            "iva": iva,
            "total": total,
            "item_count": sum(item["quantity"] for item in items.values())
        }

# --- 2. SUITE DE PRUEBAS AUTOMATIZADAS (EVIDENCIA DE DoD SPRINT 1) ---

class TestClickAndReadySprint1(unittest.TestCase):

    def setUp(self):
        self.erp = MockERPDatabase()
        self.auth = AuthService()
        self.cart = CartService(self.erp)

    # --- Pruebas PBI-01: Autenticación ---
    def test_pbi01_registro_exitoso(self):
        res = self.auth.register("cliente@andesmarket.cl", "Andes2026!")
        self.assertEqual(res["status"], 201)

    def test_pbi01_password_insegura_falla(self):
        res = self.auth.register("cliente@andesmarket.cl", "123")
        self.assertEqual(res["status"], 400)
        self.assertIn("requisitos de seguridad", res["error"])

    def test_pbi01_login_emite_jwt(self):
        self.auth.register("cliente@andesmarket.cl", "Andes2026!")
        login_res = self.auth.login("cliente@andesmarket.cl", "Andes2026!")
        self.assertEqual(login_res["status"], 200)
        self.assertTrue(login_res["token"].startswith("eyJ"))

    # --- Pruebas PBI-02: Búsqueda y Catálogo 1.500 SKUs ---
    def test_pbi02_catalogo_completo_cargado(self):
        self.assertEqual(len(self.erp.products), 1500)

    def test_pbi02_busqueda_por_nombre_y_latencia(self):
        start = time.time()
        results = self.erp.search(query="Parrilla", limit=10)
        elapsed_ms = (time.time() - start) * 1000
        self.assertTrue(len(results) > 0)
        self.assertLess(elapsed_ms, 300, "La latencia debe ser menor a 300ms según DoD")

    def test_pbi02_filtro_por_categoria(self):
        results = self.erp.search(category="Bebidas y Licores", limit=50)
        self.assertTrue(all(p["category"] == "Bebidas y Licores" for p in results))

    # --- Pruebas PBI-03: Carrito y Totales con IVA ---
    def test_pbi03_agregar_producto_y_calculo_totales(self):
        sku_test = "SKU-0010"
        prod = next(p for p in self.erp.products if p["sku"] == sku_test)
        
        cart_res = self.cart.add_or_update_item("sess_123", sku_test, quantity=2)
        cart = cart_res["cart"]
        
        expected_subtotal = prod["price"] * 2
        expected_iva = round(expected_subtotal * 0.19)
        expected_total = expected_subtotal + expected_iva
        
        self.assertEqual(cart["subtotal"], expected_subtotal)
        self.assertEqual(cart["iva"], expected_iva)
        self.assertEqual(cart["total"], expected_total)

    def test_pbi03_persistencia_sesion(self):
        self.cart.add_or_update_item("sess_abc", "SKU-0001", quantity=1)
        # Recuperamos la sesión simulada
        cart = self.cart.get_cart("sess_abc")
        self.assertEqual(cart["item_count"], 1)

    def test_pbi03_stock_insuficiente_rechaza(self):
        res = self.cart.add_or_update_item("sess_xyz", "SKU-0001", quantity=999999)
        self.assertEqual(res["status"], 400)
        self.assertIn("Stock insuficiente", res["error"])

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestClickAndReadySprint1)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
