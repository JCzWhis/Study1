# ⚡ Quickstart - MedStudy Pro

## 🎯 **Inicio Rápido en 1 Comando**

Esta carpeta contiene scripts para iniciar MedStudy Pro en un solo comando, sin necesidad de configuración manual.

## 🚀 **Scripts Disponibles**

### **Windows**
```bash
START_MEDSTUDY.bat
```
- Inicia automáticamente Django backend
- Lanza React frontend
- Configura Ollama si es necesario
- Abre navegador en la aplicación

### **Linux/Mac**
```bash
./start_medstudy.sh
```
- Script equivalente para sistemas Unix
- Configuración automática de permisos
- Gestión de puertos y servicios

## 📋 **Qué Hace el Script**

1. **Verificación de Dependencias**
   - Verifica Python 3.11+
   - Verifica Node.js 16+
   - Verifica Ollama instalado

2. **Configuración Automática**
   - Activa entorno virtual Django
   - Instala dependencias faltantes
   - Configura base de datos
   - Descarga modelo Gemma2 si es necesario

3. **Inicio de Servicios**
   - Django backend (puerto 8000)
   - React frontend (puerto 3000)
   - Ollama service
   - Health checks automáticos

4. **Apertura de Browser**
   - Abre automáticamente http://localhost:3000
   - Dashboard listo para usar

## 🔧 **Solución de Problemas**

### Error: Python no encontrado
```bash
# Instalar Python 3.11+ desde python.org
# O usar package manager del sistema
```

### Error: Ollama no disponible
```bash
# Windows/Mac: Descargar desde ollama.ai
# Linux: curl https://ollama.ai/install.sh | sh
```

### Error: Puerto ocupado
```bash
# Cambiar puertos en scripts si es necesario
# Backend: puerto 8001
# Frontend: puerto 3001
```

## 📞 **Soporte**

Si el quickstart no funciona:
1. Verificar logs en `/medstudy_app/logs/`
2. Ejecutar diagnosis: `python manage.py check`
3. Consultar documentación completa en `/docs/`

---

**¡Con un comando tienes MedStudy Pro funcionando! 🚀**