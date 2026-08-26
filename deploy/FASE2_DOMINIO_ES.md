# Fase 2 — Dominio principal `agroplaga.es`

**Actualizado:** 26 ago 2026

Dominio principal: **`https://agroplaga.es`**.  
Legacy **`agroplaga-ai.farm`**: la API sigue activa (APK antigua); landing y panel redirigen a `.es`.

---

## 1. En el VPS (tú)

```bash
cd ~/AgroPlaga-AI
git pull origin nexoagro
```

Edita **`deploy/pilot.env`** (solo una línea):

```bash
API_DOMAIN=agroplaga.es
```

Reinicia Caddy (y landing si cambió):

```bash
docker compose -f docker-compose.pilot.yml --env-file deploy/pilot.env -p agroplaga up -d --force-recreate caddy
```

Comprueba:

```bash
curl -sI https://agroplaga.es/panel/ | head -n 1
curl -sI https://agroplaga-ai.farm/ | head -n 1          # debe ser 301 → .es
curl -sI https://agroplaga-ai.farm/api/v1/auth/login | head -n 1   # debe llegar al backend (405/422 OK)
```

---

## 2. Nueva APK (en tu PC)

```bash
cd frontend
flutter build apk --release --dart-define=API_BASE_URL=https://agroplaga.es
```

Instala en móviles piloto. La APK antigua (`.farm`) **sigue funcionando** mientras `/api` en `.farm` esté activo.

---

## 3. Comunicación pilotos

- Web y panel: **`https://agroplaga.es`**
- Peritos: bookmark **`https://agroplaga.es/panel/`**
- Agricultores: instalar APK nueva cuando la repartas

---

## 4. Más adelante (Fase 3)

Cuando todos tengan APK con `.es`:

- Quitar bloque legacy en `deploy/Caddyfile` o redirect total `.farm` → `.es`
- No renovar dominio `.farm` en Namecheap al caducar
