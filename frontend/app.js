const API_URL = "http://127.0.0.1:8000/api/v1";

// 1. Obtener y almacenar el Token JWT
async function iniciarSesion() {
  const username = document.getElementById("user").value;
  const password = document.getElementById("pass").value;

  try {
    const res = await fetch(`${API_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password })
    });

    if (!res.ok) throw new Error("Credenciales inválidas (401)");

    const data = await res.json();
    localStorage.setItem("jwt_token", data.access_token);
    document.getElementById("msg-login").innerText = "Token JWT guardado en localStorage.";
  } catch (err) {
    alert("Error: " + err.message);
  }
}

// 2. Consultar la lista de productos (GET)
async function cargarProductos() {
  const lista = document.getElementById("lista-productos");
  lista.innerHTML = "Cargando...";

  try {
    const res = await fetch(`${API_URL}/productos`);
    const productos = await res.json();

    lista.innerHTML = "";
    productos.forEach(p => {
      const li = document.createElement("li");
      li.innerHTML = `<strong>${p.nombre}</strong> — $${p.precio} | Stock: ${p.stock}`;
      lista.appendChild(li);
    });
  } catch (err) {
    lista.innerHTML = "Error al conectar con el servidor.";
  }
}

// 3. Crear nuevo producto enviando el Bearer Token (POST)
async function guardarProducto() {
  const token = localStorage.getItem("jwt_token");

  if (!token) {
    alert("Acceso denegado: Primero debes iniciar sesión para obtener el token.");
    return;
  }

  const payload = {
    nombre: document.getElementById("prod-nombre").value,
    precio: parseFloat(document.getElementById("prod-precio").value),
    stock: parseInt(document.getElementById("prod-stock").value)
  };

  try {
    const res = await fetch(`${API_URL}/productos`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify(payload)
    });

    if (res.status === 401 || res.status === 403) {
      throw new Error("No autorizado: Token ausente o caducado");
    }

    if (!res.ok) throw new Error("Error en la solicitud (" + res.status + ")");

    alert("¡Producto registrado con éxito (201 Created)!");
    cargarProductos();
  } catch (err) {
    alert(err.message);
  }
}

// Carga automática inicial de productos
cargarProductos();
