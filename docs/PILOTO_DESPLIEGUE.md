# Piloto Lean — despliegue 24/7

Guía para exponer AgroPlaga AI en internet (HTTPS) y repartir la APK a early adopters.

**Requisitos:** VPS Linux (Ubuntu 22.04+, 2 GB RAM), dominio o subdominio, puertos 80/443 abiertos.

---

## 1. Contratar VPS y dominio

| Proveedor (ejemplos) | Coste orientativo |
|----------------------|-------------------|
| Hetzner, DigitalOcean, IONOS | 5–12 €/mes |
| Dominio `.com` / `.es` | ~10 €/año |

1. Crea el VPS (Ubuntu 22.04).
2. En tu DNS, registro **A**: `api.tudominio.com` → **IP pública del VPS**.
3. Espera 5–30 min a que propague el DNS.

---

## 2. Preparar el servidor

Conéctate por SSH:

```bash
ssh root@IP_DEL_VPS
```

Instala Docker:

```bash
apt update && apt upgrade -y
apt install -y git ca-certificates curl
curl -fsSL https://get.docker.com | sh
```

Clona el repo:

```bash
git clone https://github.com/valentinrl9/AgroPlaga-AI.git
cd AgroPlaga-AI
```

Configura secretos:

```bash
cp deploy/pilot.env.example deploy/pilot.env
nano deploy/pilot.env
```

**Obligatorio cambiar:**

- `API_DOMAIN` → tu subdominio real (ej. `api.agroplaga.es`)
- `POSTGRES_PASSWORD` → contraseña larga aleatoria
- `SECRET_KEY` → mínimo 32 caracteres aleatorios
- `ADMIN_EMAIL` / `ADMIN_PASSWORD` → credenciales admin del piloto

Despliega:

```bash
chmod +x deploy/setup-pilot.sh
./deploy/setup-pilot.sh
```

Comprueba:

```bash
curl -sI https://api.tudominio.com/docs | head -n 1
# HTTP/2 200
```

Desde el móvil (datos, no Wi‑Fi de casa): abre `https://api.tudominio.com/docs` en el navegador.

---

## 2b. Panel web B2B (cooperativas / técnicos)

Tras el despliegue, el panel queda en:

**`https://TU_DOMINIO/panel/`**

(ej. `https://agroplaga-ai.farm/panel/`)

Login con cuenta **rol `tech` o `admin`** (mismo email/contraseña que la app).

### Usuario maestro (entrevistas)

Añade en `deploy/pilot.env` (no subas este archivo a GitHub):

```env
MASTER_EMAIL=valentinruizleon@gmail.com
MASTER_PASSWORD=12345678
MASTER_NAME=Valentín Ruiz León
```

Reinicia el backend para crear/actualizar la cuenta:

```bash
docker compose -f docker-compose.pilot.yml --env-file deploy/pilot.env -p agroplaga up -d --build backend
```

Comprueba el panel:

```bash
curl -sI https://agroplaga-ai.farm/panel/ | head -n 1
```

---

## 3. Compilar APK del piloto (en tu PC)

```powershell
cd frontend
flutter build apk --release --dart-define=API_BASE_URL=https://api.tudominio.com
```

APK: `frontend/build/app/outputs/flutter-apk/app-release.apk`

Distribución: Drive, WhatsApp o USB. Cada agricultor instala manualmente (origen desconocido).

**Primera apertura:** Login → *Configurar servidor API* solo si el build no llevaba `--dart-define`. Con la URL fija en el build, entra directo a registro/login.

---

## 4. Operación del piloto

### Arrancar / parar

```bash
cd AgroPlaga-AI
docker compose -f docker-compose.pilot.yml --env-file deploy/pilot.env up -d
docker compose -f docker-compose.pilot.yml --env-file deploy/pilot.env down
```

### Ver logs

```bash
docker compose -f docker-compose.pilot.yml --env-file deploy/pilot.env logs -f backend
```

### Copia de seguridad BD (semanal recomendada)

```bash
docker compose -f docker-compose.pilot.yml --env-file deploy/pilot.env \
  exec -T db pg_dump -U plagaia plagaia_db > backup_$(date +%F).sql
```

### Actualizar código

```bash
git pull
docker compose -f docker-compose.pilot.yml --env-file deploy/pilot.env -p agroplaga up -d --build
```

La landing pública queda en **`https://TU_DOMINIO/`** (raíz). Panel en `/panel/`.

Mensajes del formulario de contacto: `GET /api/v1/admin/contact-inquiries` (admin).

---

## 5. Seguridad mínima del piloto

- No subas `deploy/pilot.env` a git.
- Cambia `ADMIN_PASSWORD` tras el primer acceso.
- Firewall: solo 22 (SSH), 80 y 443.
- PostgreSQL **no** expuesto a internet (solo red Docker interna).

---

## 6. Alternativa sin dominio propio

Si aún no tienes dominio, puedes usar **Cloudflare Tunnel** (HTTPS gratis con subdominio `*.trycloudflare.com` o tu zona en Cloudflare). Es más frágil para un piloto largo; mejor un subdominio fijo.

---

## 7. Registro cerrado (invitaciones piloto)

En el VPS, `deploy/pilot.env` debe incluir:

```env
REGISTRATION_MODE=invite_only
PILOT_SEED_INVITES=true
```

Al arrancar, se cargan **10 códigos** (7 agricultores + 2 técnicos + 1 cooperativa) si la tabla está vacía. Lista para reparto: [deploy/PILOTO_CODIGOS.md](../deploy/PILOTO_CODIGOS.md).

**APK:** recompila con el campo de invitación en registro:

```powershell
cd frontend
flutter build apk --release --dart-define=API_BASE_URL=https://agroplaga-ai.farm
```

Auditoría (login admin en `/docs`):

- `GET /api/v1/admin/invites` — códigos usados o pendientes
- `GET /api/v1/admin/users` — cuentas registradas

---

## 8. Siguiente paso: candidatos

Con el servidor estable:

1. Recluta 5–6 agricultores/técnicos (El Ejido, Dalías, etc.).
2. Instala la APK y crea cuenta (o registro guiado).
3. Mide 4–6 semanas: escaneos/semana, contribuciones al mapa, retención.
4. Decisión: **perseverar** o **pivotar**.

Ver también: [ROADMAP_LEAN.md](ROADMAP_LEAN.md).

---

## Desarrollo local vs piloto

| Entorno | Comando | URL |
|---------|---------|-----|
| Local (LAN) | `docker compose up --build` | `http://192.168.x.x:8000` |
| Piloto 24/7 | `./deploy/setup-pilot.sh` | `https://api.tudominio.com` |
