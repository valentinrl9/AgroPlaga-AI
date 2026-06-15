import "package:flutter/material.dart";
import "package:http/http.dart" as http;

import "../../core/api_config.dart";
import "../widgets/primary_button.dart";

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  late final TextEditingController _urlController;
  bool _testing = false;
  bool _saving = false;
  String? _status;

  @override
  void initState() {
    super.initState();
    _urlController = TextEditingController(text: ApiConfig.baseUrl);
  }

  @override
  void dispose() {
    _urlController.dispose();
    super.dispose();
  }

  Future<bool> _pingServer(String baseUrl) async {
    final uri = Uri.parse("${ApiConfig.normalize(baseUrl)}/docs");
    final response = await http.get(uri).timeout(const Duration(seconds: 8));
    return response.statusCode == 200;
  }

  Future<void> _testConnection() async {
    setState(() {
      _testing = true;
      _status = null;
    });
    try {
      final ok = await _pingServer(_urlController.text);
      if (!mounted) return;
      setState(() {
        _status = ok ? "Conexión correcta con el servidor." : "El servidor respondió con error.";
      });
    } catch (_) {
      if (!mounted) return;
      setState(() {
        _status = "No se pudo conectar. Comprueba la IP, Wi‑Fi y que Docker esté activo.";
      });
    } finally {
      if (mounted) setState(() => _testing = false);
    }
  }

  Future<void> _save() async {
    setState(() {
      _saving = true;
      _status = null;
    });
    try {
      final normalized = ApiConfig.normalize(_urlController.text);
      await ApiConfig.save(normalized);
      if (!mounted) return;
      setState(() {
        _urlController.text = normalized;
        _status = "URL guardada. No hace falta reinstalar la app.";
      });
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  Future<void> _reset() async {
    await ApiConfig.reset();
    if (!mounted) return;
    setState(() {
      _urlController.text = ApiConfig.baseUrl;
      _status = "Restaurada la URL por defecto.";
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Ajustes")),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text(
              "Servidor API",
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            const Text(
              "En móvil físico usa la IP de tu PC en la misma Wi‑Fi, por ejemplo http://192.168.1.104:8000",
              style: TextStyle(color: Color(0xFF424242)),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _urlController,
              decoration: const InputDecoration(
                labelText: "URL del backend",
                hintText: "http://192.168.1.104:8000",
                border: OutlineInputBorder(),
              ),
              keyboardType: TextInputType.url,
              autocorrect: false,
            ),
            const SizedBox(height: 12),
            if (_status != null)
              Text(
                _status!,
                style: TextStyle(
                  color: _status!.startsWith("Conexión") || _status!.startsWith("URL")
                      ? const Color(0xFF2E7D32)
                      : const Color(0xFFC62828),
                ),
              ),
            const SizedBox(height: 16),
            PrimaryButton(
              label: _testing ? "Comprobando..." : "Probar conexión",
              onPressed: _testing ? null : _testConnection,
            ),
            const SizedBox(height: 10),
            PrimaryButton(
              label: _saving ? "Guardando..." : "Guardar",
              onPressed: _saving ? null : _save,
            ),
            const SizedBox(height: 10),
            OutlinedButton(onPressed: _reset, child: const Text("Restaurar por defecto")),
          ],
        ),
      ),
    );
  }
}
