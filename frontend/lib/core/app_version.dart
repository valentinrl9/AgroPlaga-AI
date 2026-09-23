/// Visible en la app. Tiene que coincidir con `version` de pubspec.yaml
/// y con `landing/ayuda/version.json` (el número después del + es versionCode).
const String appVersionLabel = "V2.1.3";
const int appVersionCode = 8;

/// El aviso de actualización consulta este archivo, no el servidor de la API.
const String appUpdateManifestUrl = "https://agroplaga.es/ayuda/version.json";
