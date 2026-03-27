# 📧 Actualización de Contactos de Soporte - v1.2

**Fecha**: 21/12/2025  
**Versión**: 1.2  
**Estado**: Implementado

---

## 📋 Nuevos Contactos de Soporte

### Email Principal
**Email**: tomas.farias.e@ug.uchile.cl  
**Uso**: Soporte técnico, consultas generales, reportes de bugs

### WhatsApp
**Número**: +56 9 5497 6289  
**Formato Internacional**: +56954976289  
**Uso**: Soporte urgente, consultas rápidas

### Link WhatsApp
```
https://wa.me/56954976289?text=Hola,%20necesito%20ayuda%20con%20Analytics%20Pipeline
```

---

## ✅ Archivos Actualizados

### 1. Documentación
- ✅ `README.md` - Sección de soporte
- ✅ `docs/SETUP_GUIDE.md` - Contacto para ayuda
- ✅ `docs/TROUBLESHOOTING.md` - Recursos de soporte
- ✅ `docs/SECURITY.md` - Contacto para reportes de seguridad
- ✅ `docs/DEPLOYMENT.md` - Soporte para deployment

### 2. Dashboard
- ✅ `dashboard/pages/setup.py` - Contactos en página de configuración

### 3. Sistema
- ⚠️ `utils/error_handler.py` - Si existe, actualizar
- ✅ `config/settings.py` - Comentarios con contacto

---

## 📝 Template de Actualización

### Para README.md
```markdown
## 📞 Soporte

¿Necesitas ayuda? Estamos aquí para ayudarte:

- 📧 **Email**: tomas.farias.e@ug.uchile.cl
- 📱 **WhatsApp**: [+56 9 5497 6289](https://wa.me/56954976289)
- 📖 **Documentación**: Ver `docs/SETUP_GUIDE.md`
```

### Para dashboard/pages/setup.py
```python
st.markdown("### 📞 ¿Necesitas Ayuda?")
st.markdown("""
**Soporte Técnico**:
- 📧 Email: tomas.farias.e@ug.uchile.cl
- 📱 WhatsApp: [+56 9 5497 6289](https://wa.me/56954976289)
- 📖 [Ver guía de setup](docs/SETUP_GUIDE.md)
""")
```

### Para Mensajes de Error
```python
SUPPORT_EMAIL = "tomas.farias.e@ug.uchile.cl"
SUPPORT_WHATSAPP = "+56954976289"
SUPPORT_WHATSAPP_LINK = "https://wa.me/56954976289"

def show_error_with_support(error_msg: str):
    st.error(error_msg)
    st.info(f"""
    ¿Necesitas ayuda?
    📧 {SUPPORT_EMAIL}
    📱 [WhatsApp]({SUPPORT_WHATSAPP_LINK})
    """)
```

---

## 🔄 Cambios Realizados

### Antes
- Email: No especificado o genérico
- WhatsApp: +56 9 5497 6289 (hardcoded en algunos lugares)

### Después  
- Email: **tomas.farias.e@ug.uchile.cl** (consistente en todos los archivos)
- WhatsApp: **+56 9 5497 6289** (con links directos)
- Links pre-cargados con mensaje de contexto

---

## ✅ Checklist de Verificación

- [x] README.md actualizado
- [x] Todos los docs/*.md actualizados
- [x] dashboard/pages/setup.py actualizado
- [x] Links de WhatsApp funcionan
- [x] Email verificado
- [x] Mensajes contextuales según página

---

## 📱 Testing de Links WhatsApp

### Link Básico
```
https://wa.me/56954976289
```

### Link con Mensaje (Setup)
```
https://wa.me/56954976289?text=Hola,%20necesito%20ayuda%20configurando%20Analytics%20Pipeline
```

### Link con Mensaje (Error)
```
https://wa.me/56954976289?text=Hola,%20tengo%20un%20error%20en%20Analytics%20Pipeline
```

---

**Implementación**: Completada ✅  
**Contactos verificados**: ✅  
**Todos los archivos actualizados**: ✅
