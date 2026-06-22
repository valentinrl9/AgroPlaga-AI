# Códigos del piloto Lean — reparto personal (no compartir en grupos)

**Caducidad:** 15 ago 2026 · **Usos:** 1 por código  
**Registro:** app → Regístrate → código + email + contraseña  
**URL API:** `https://agroplaga-ai.farm` (ya incluida en la APK piloto)

---

## Agricultores (rol: farmer)

| # | Código | Destinatario (anotar nombre) |
|---|--------|------------------------------|
| 1 | `PLG-PILOT-F01` | |
| 2 | `PLG-PILOT-F02` | |
| 3 | `PLG-PILOT-F03` | |
| 4 | `PLG-PILOT-F04` | |
| 5 | `PLG-PILOT-F05` | |
| 6 | `PLG-PILOT-F06` | |
| 7 | `PLG-PILOT-F07` | |

---

## Técnicos / peritos (rol: tech — validación + panel web)

| # | Código | Destinatario |
|---|--------|--------------|
| 1 | `PLG-PILOT-T01` | |
| 2 | `PLG-PILOT-T02` | |

---

## Cooperativa (rol: tech — panel web + validación)

| # | Código | Destinatario |
|---|--------|--------------|
| 1 | `PLG-PILOT-C01` | |

---

## Mensaje tipo WhatsApp

```
AgroPlaga AI — piloto
1) Instala la APK que te envío
2) Regístrate con TU código personal (solo vale 1 vez):
   Código: PLG-PILOT-F0X
3) Email y contraseña que recuerdes
4) Cualquier duda: [tu teléfono]
No compartas el código con nadie.
```

---

## Auditoría (admin)

- Swagger: `https://agroplaga-ai.farm/docs`
- `GET /api/v1/admin/invites` — estado de códigos
- `GET /api/v1/admin/users` — quién se registró

Tras desplegar con `PILOT_SEED_INVITES=true`, los códigos se cargan solos al arrancar el backend (solo si la tabla está vacía).
