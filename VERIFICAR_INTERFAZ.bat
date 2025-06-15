@echo off
echo ==========================================
echo    🔍 VERIFICADOR DE INTERFAZ
echo ==========================================
echo.

echo 🌐 Abriendo Frontend Lovable en navegador...
echo.
echo ✅ Si ves esta interfaz MODERNA:
echo    🎨 Colores azul médico y diseño limpio
echo    📊 Dashboard con tarjetas de estadísticas  
echo    🧠 Saludo personalizado "¡Bienvenido Dr.!"
echo    ⚡ Sección "Acciones Rápidas"
echo    📚 "Planes de Estudio Recientes"
echo.
echo ❌ Si ves interfaz antigua:
echo    🔄 Presiona Ctrl+F5 para refrescar cache
echo    🗂️ Verifica que uses: http://localhost:3000
echo    ⚠️  NO uses: http://127.0.0.1:3000
echo.
echo 🔧 Depuración:
echo    • Verifica que ambos servicios estén corriendo
echo    • Backend en puerto 8000
echo    • Frontend Lovable en puerto 3000
echo.

timeout 3 >nul 2>&1

start "Verificar Lovable" http://localhost:3000

echo 📱 Se abrió http://localhost:3000 en tu navegador
echo.
echo 💡 Si la interfaz sigue igual:
echo    1. Cierra el navegador completamente
echo    2. Ejecuta PROBAR_FRONTEND_LOVABLE.bat
echo    3. Espera a que aparezca "ready" en terminal
echo    4. Abre http://localhost:3000 de nuevo
echo.

pause