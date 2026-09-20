# E-Mercato 🛒

!Bienvenido a mi proyecto de Django para el master de Conquer Blocks!

E-Mercato es una plataforma de comercio electrónico minimalista desarrollada con Python y Django. Este proyecto está diseñado para ofrecer una experiencia de usuario fluida, permitiendo la exploración del catálogo, gestión del carrito de compras y creación de pedidos, respaldado por un sistema robusto de control de inventario y un panel de administración personalizado.

## Características Principales
* **Navegación Intuitiva:** Listado de productos y vistas de detalle organizadas por categorías.
* **Carrito de Compras Optimizado:** Gestión de productos a través de sesiones, permitiendo a los usuarios agregar y remover ítems antes de autenticarse, con devolución y descuento dinámico de stock.
* **Flujo de Pedidos:** Creación de órdenes de compra seguras que registran el precio exacto del producto en el momento de la transacción.
* **Panel de Gestión (Vendedor):** Una interfaz exclusiva para usuarios administrativos que filtra compras pagadas y permite actualizar el estado logístico de cada pedido (Pendiente, Procesando, Enviado, Entregado).

## Acceso y Pruebas (Superusuario)

Si deseas evaluar el proyecto, agregar productos al catálogo o probar el flujo de cambio de estados en el panel de vendedor, puedes acceder al sistema utilizando las credenciales de administrador preconfiguradas en el entorno.

Dirígete a la ruta `/admin` (o inicia sesión directamente en la tienda si la interfaz lo permite) e ingresa los siguientes datos[cite: 6]:

* **Usuario:** `admin`
* **Correo:** `admin@correo.com`
* **Contraseña:** `tu_contraseña_segura`

### ¿Cómo agregar productos de prueba?
1. Inicia sesión con el superusuario proporcionado.
2. Navega al panel nativo de Django (`/admin`).
3. En la sección de la aplicación `Store`, selecciona **Products** y haz clic en "Añadir".
4. Completa los detalles del producto (no olvides asignar una categoría y un valor mayor a cero en el stock) y guárdalo. 
5. Regresa a la vista principal de la tienda para ver tus productos listados y listos para ser comprados.
