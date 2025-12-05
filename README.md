<h1 align="center">🎬 CineHub: Aplicación Web para la Planificación Personalizada de Rutinas de Películas y Series</h1>

<hr>

<h2>1. <b>Descripción del Proyecto</b></h2>

<p>
Esta aplicación web es una solución práctica para facilitar la gestión del entretenimiento. La aplicación no solo permitirá explorar y almacenar información de películas y series, sino también planificar rutinas personalizadas y obtener reportes analíticos que reflejen los hábitos de visualización.
</p>

<h2>2. Funcionalidades Principales</h2>
<ul>
  <li>Diseñar un módulo de rutinas que permita a los usuarios planificar su consumo audiovisual en diferentes periodos.</li>
  <li>Recolectar y almacenar valoraciones personales y hábitos de consumo.</li>
  <li>Generar reportes dinámicos sobre preferencias y patrones de visualización a partir de los datos registrados.</li>
</ul>

<h2>3. Lógica de Negocio</h2>
<ul>
  <li>El correo  del usuario es único → no pueden existir usuarios duplicados.</li>
  <li>Todos los modelos utilizan eliminación lógica (*Soft Delete*) mediante los campos `is_active` y `deleted_at`.</li>
  <li>Un usuario solo puede crear una valoración activa por cada título.</li>
</ul>

<h2>4. Modelos</h2>

<h3> Usuario</h3>

<table>
  <tr><th>Campo</th><th>Tipo</th><th>Descripción</th></tr>
  <tr><td>id_usuario</td><td>int (PK)</td><td>Llave primaria</td></tr>
  <tr><td>nombre</td><td>String</td><td>Nombre completo del usuario</td></tr>
  <tr><td>correo</td><td>String</td><td>Correo electrónico (Único)</td></tr>
  <tr><td>clave</td><td>String</td><td>Contraseña hasheada</td></tr>
  <tr><td>is_active</td><td>bool</td><td>Estado de eliminación lógica</td></tr>
  <tr><td>deleted_at</td><td>datetime</td><td>Fecha de eliminación (Soft Delete)</td></tr>
</table>

<h3>PeliculaSerie</h3>

<table>
  <tr><th>Campo</th><th>Tipo</th><th>Descripción</th></tr>
  <tr><td>id_titulo</td><td>int (PK)</td><td>Llave primaria</td></tr>
  <tr><td>titulo</td><td>String</td><td>Título del contenido (Único)</td></tr>
  <tr><td>genero</td><td>String</td><td>Género principal</td></tr>
  <tr><td>anio_estreno</td><td>int</td><td>Año de lanzamiento</td></tr>
  <tr><td>duracion</td><td>int</td><td>Duración en minutos/temporadas</td></tr>
  <tr><td>is_active</td><td>bool</td><td>Estado de eliminación lógica</td></tr>
  <tr><td>deleted_at</td><td>datetime</td><td>Fecha de eliminación (Soft Delete)</td></tr>
</table>

<h3>Valoración</h3>

<table>
  <tr><th>Campo</th><th>Tipo</th><th>Descripción</th></tr>
  <tr><td>id_valoracion</td><td>int (PK)</td><td>Llave primaria</td></tr>
  <tr><td>puntuacion</td><td>float</td><td>Puntuación de 1.0 a 5.0</td></tr>
  <tr><td>comentario</td><td>String</td><td>Reseña textual del usuario</td></tr>
  <tr><td>fecha</td><td>date</td><td>Fecha de la valoración</td></tr>
  <tr><td>id_usuario_FK</td><td>int</td><td>Llave foránea → Usuario</td></tr>
  <tr><td>id_titulo_FK</td><td>int</td><td>Llave foránea → PeliculaSerie</td></tr>
</table>

<h3>Rutina</h3>

<table>
  <tr><th>Campo</th><th>Tipo</th><th>Descripción</th></tr>
  <tr><td>id_rutina</td><td>int (PK)</td><td>Llave primaria</td></tr>
  <tr><td>nombre</td><td>String</td><td>Nombre de la rutina</td></tr>
  <tr><td>fecha_inicio</td><td>date</td><td>Fecha de inicio</td></tr>
  <tr><td>fecha_fin</td><td>date</td><td>Fecha de finalización</td></tr>
  <tr><td>id_usuario_FK</td><td>int</td><td>Llave foránea → Usuario</td></tr>
  <tr><td>id_titulo_FK</td><td>int</td><td>Llave foránea → PeliculaSerie</td></tr>
</table>

<h3>Relaciones entre Modelos</h3>
<ul>
  <li>Un Usuario puede tener muchas Valoraciones y muchas Rutinas (Relación 1:N).</li>
  <li>Una Película/Serie puede tener muchas Valoraciones y muchas Rutinas (Relación 1:N).</li>
</ul>

<h2>5. Mapa de Endpoints</h2>
<table>

  <tr><th>Método</th><th>Endpoint</th><th>Descripción</th><th>Modelo Relacionado</th></tr>

 <tr><td>POST</td><td>/web/usuarios/</td><td>Registrar un nuevo usuario</td><td>Usuario</td></tr>
    <tr><td>GET</td><td>/web/usuarios/</td><td>Listar todos los usuarios activos</td><td>Usuario</td></tr>
    <tr><td>GET</td><td>/web/usuarios/eliminados</td><td>Listar usuarios eliminados (Soft Delete)</td><td>Usuario</td></tr>
    <tr><td>GET</td><td>/web/usuarios/correo/{correo}</td><td>Buscar usuario por correo electrónico</td><td>Usuario</td></tr>
    <tr><td>GET</td><td>/web/usuarios/{id_usuario}</td><td>Obtener detalles de un usuario por ID</td><td>Usuario</td></tr>
    <tr><td>PUT</td><td>/web/usuarios/{id_usuario}</td><td>Actualizar datos de un usuario</td><td>Usuario</td></tr>
    <tr><td>DELETE</td><td>/web/usuarios/{id_usuario}</td><td>Eliminar un usuario (Lógico)</td><td>Usuario</td></tr>
     <tr><td>POST</td><td>/titulos/</td><td>Crear una nueva película o serie</td><td>PeliculaSerie</td></tr>
    <tr><td>GET</td><td>/titulos/</td><td>Listar todos los títulos activos</td><td>PeliculaSerie</td></tr>
    <tr><td>GET</td><td>/titulos/eliminados</td><td>Listar títulos eliminados</td><td>PeliculaSerie</td></tr>
    <tr><td>GET</td><td>/titulos/nombre/{nombre}</td><td>Buscar título por nombre exacto</td><td>PeliculaSerie</td></tr>
    <tr><td>GET</td><td>/titulos/{id_titulo}</td><td>Obtener título por ID (incluye relaciones)</td><td>PeliculaSerie</td></tr>
    <tr><td>PUT</td><td>/titulos/{id_titulo}</td><td>Actualizar información de un título</td><td>PeliculaSerie</td></tr>
    <tr><td>DELETE</td><td>/titulos/{id_titulo}</td><td>Eliminar un título (Lógico)</td><td>PeliculaSerie</td></tr>
    <tr><td>POST</td><td>/valoraciones/</td><td>Registrar una nueva valoración</td><td>Valoracion</td></tr>
    <tr><td>GET</td><td>/valoraciones/</td><td>Listar todas las valoraciones activas</td><td>Valoracion</td></tr>
    <tr><td>GET</td><td>/valoraciones/eliminadas</td><td>Listar valoraciones eliminadas</td><td>Valoracion</td></tr>
    <tr><td>GET</td><td>/valoraciones/{id_valoracion}</td><td>Obtener valoración por ID</td><td>Valoracion</td></tr>
    <tr><td>PUT</td><td>/valoraciones/{id_valoracion}</td><td>Actualizar puntuación o comentario</td><td>Valoracion</td></tr>
    <tr><td>DELETE</td><td>/valoraciones/{id_valoracion}</td><td>Eliminar una valoración (Lógico)</td><td>Valoracion</td></tr>
    <tr><td>POST</td><td>/rutinas/</td><td>Crear una nueva rutina de visualización</td><td>Rutina</td></tr>
    <tr><td>GET</td><td>/rutinas/</td><td>Listar todas las rutinas activas</td><td>Rutina</td></tr>
    <tr><td>GET</td><td>/rutinas/eliminadas</td><td>Listar rutinas eliminadas</td><td>Rutina</td></tr>
    <tr><td>GET</td><td>/rutinas/nombre/{nombre}</td><td>Buscar rutina por nombre</td><td>Rutina</td></tr>
    <tr><td>GET</td><td>/rutinas/{id_rutina}</td><td>Obtener rutina por ID</td><td>Rutina</td></tr>
    <tr><td>PUT</td><td>/rutinas/{id_rutina}</td><td>Actualizar fechas o nombre de rutina</td><td>Rutina</td></tr>
    <tr><td>DELETE</td><td>/rutinas/{id_rutina}</td><td>Eliminar una rutina (Lógico)</td><td>Rutina</td></tr>
     <tr><td>GET</td><td>/web/estadisticas</td><td>Vista: Dashboard de métricas y reportes</td><td>General</td></tr>

</table>

 
<h2>7. Tecnologías Utilizadas</h2>
<ul>
  <li>Python 3.13</li>
  <li>FastAPI (Framework de Python)</li>
  <li>SQLModel / SQLAlchemy (ORM)</li>
  <li>PostgreSQL (Base de Datos con Render)</li>
  <li>Jinja2 (Templating para Web UI)</li>
  <li>Supabase (Para Auth y Storage de imágenes)</li>
  <li> Despliegue: Render</li>
  <li>Uvicorn (Servidor ASGI)</li>
</ul>

<h2>8. Acceso al Swagger</h2>
<p>
Puedes acceder a la documentación interactiva de la API en el siguiente enlace:<br>
<a href="https://project-movies-5joh.onrender.com" target="_blank">
  🔗 Click aqui para visualizar el sistema
</a>
</p>
