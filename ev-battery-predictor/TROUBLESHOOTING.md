# Guía de Solución de Problemas - EV Battery Predictor

## Problemas Comunes y Soluciones

### 1. Error 500 en Endpoint de Métricas (/predictions/metrics/{model_id})

**Síntoma:** Error 500 Internal Server Error al obtener métricas del modelo

**Causas Posibles:**
- El modelo no tiene datos suficientes para calcular métricas
- Error en el procesamiento de características del modelo
- Valores infinitos o NaN en los datos de prueba
- Incompatibilidad entre características entrenadas y datos de prueba

**Soluciones Aplicadas:**
1. **Validación mejorada de datos:** Se agregó validación para asegurar datos suficientes
2. **Manejo de valores infinitos:** Se reemplazan valores infinitos con NaN y luego con 0
3. **Función safe_float:** Se agregó función para validar que todos los valores sean finitos
4. **Manejo de errores robusto:** Retorna valores None en lugar de fallar completamente

**Cómo Verificar la Solución:**
```bash
# Reiniciar el backend
docker-compose restart backend

# Verificar logs
docker-compose logs backend --tail=20

# Probar endpoint de métricas desde frontend
# Ir a Predictions → Seleccionar modelo → Generate Forecast
```

### 2. Frontend No Se Conecta al Backend

**Síntoma:** Error de conexión CORS o red en el frontend

**Soluciones:**
1. Verificar que backend esté corriendo:
   ```bash
   docker-compose ps
   ```

2. Verificar configuración de CORS en backend (`backend/app/main.py`)

3. Verificar variable de entorno en frontend:
   ```
   REACT_APP_API_URL=http://localhost:8000
   ```

### 3. Errores de Autenticación

**Síntoma:** Error 401 Unauthorized en requests

**Soluciones:**
1. Verificar que el token JWT esté siendo enviado correctamente
2. Verificar que el token no haya expirado
3. Limpiar localStorage del navegador:
   ```javascript
   localStorage.clear()
   ```

### 4. Modelos No Se Entrenan Correctamente

**Síntoma:** Modelos quedan en estado "Not Trained" o fallan durante entrenamiento

**Soluciones:**
1. **Datos insuficientes:** Asegurar al menos 5 puntos de datos
2. **Validar rango de SOH:** Values debe estar entre 0-100%
3. **Verificar columnas requeridas:** Al menos state_of_health debe estar presente
4. **Revisar logs del backend:**
   ```bash
   docker-compose logs backend | grep -i error
   ```

### 5. Problemas con Docker

**Síntoma:** Contenedores no inician o fallan

**Soluciones:**
1. **Limpiar recursos de Docker:**
   ```bash
   docker-compose down -v
   docker system prune -f
   ```

2. **Reconstruir imágenes:**
   ```bash
   docker-compose build --no-cache
   ```

3. **Verificar puertos disponibles:**
   - Frontend: 3000
   - Backend: 8000
   - PostgreSQL: 5432
   - Redis: 6379

### 6. Problemas de Predicciones

**Síntoma:** Errores al generar pronósticos SOH

**Verificaciones:**
1. **Modelo entrenado:** Verificar que el modelo tenga is_trained=True
2. **Datos de entrenamiento:** Al menos 10 puntos de datos para predicciones confiables
3. **Parámetros válidos:**
   - prediction_steps: Entre 1 y 2000
   - time_step_days: Entre 1 y 365

### 7. Problemas de Rendimiento

**Síntoma:** Aplicación lenta o timeouts

**Optimizaciones:**
1. **Limitar datos de prueba:** Usar solo los últimos registros para métricas
2. **Optimizar consultas de DB:** Agregar índices si es necesario
3. **Reducir pasos de predicción:** Usar menos prediction_steps para pruebas

## Comandos Útiles para Debugging

### Backend
```bash
# Ver logs en tiempo real
docker-compose logs backend --follow

# Ejecutar comando en contenedor backend
docker-compose exec backend python -c "import app.ml.models; print('ML module loaded')"

# Conectar a la base de datos
docker-compose exec db psql -U evuser -d evbattery
```

### Frontend
```bash
# Ver logs del frontend
docker-compose logs frontend --tail=50

# Reconstruir solo frontend
docker-compose build frontend
```

### Base de Datos
```sql
-- Verificar datos en la DB
SELECT COUNT(*) FROM battery_data;
SELECT COUNT(*) FROM ml_models WHERE is_trained = true;
SELECT COUNT(*) FROM vehicles;
```

## Monitoreo de Estado

### Verificar Servicios
```bash
# Estado de todos los servicios
docker-compose ps

# Verificar salud de la DB
docker-compose exec db pg_isready -U evuser

# Verificar conectividad de Redis
docker-compose exec redis redis-cli ping
```

### URLs de Verificación
- Frontend: http://localhost:3000
- Backend API Docs: http://localhost:8000/docs
- Backend Health: http://localhost:8000/api/v1/ (debería devolver info de la API)

## Logs Importantes a Revisar

1. **Errores de TensorFlow:** Normales, se pueden ignorar los warnings sobre GPU
2. **Errores de CORS:** Revisar configuración en main.py
3. **Errores de JWT:** Verificar configuración de tokens
4. **Errores de SQL:** Problemas con migraciones o datos

## Contacto para Soporte

Si los problemas persisten:
1. Revisar logs detallados con `docker-compose logs`
2. Verificar versiones de dependencias en `requirements.txt` y `package.json`
3. Asegurar que todos los puertos estén disponibles
4. Verificar configuración de variables de entorno
