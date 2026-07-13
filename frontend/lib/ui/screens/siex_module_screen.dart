import "package:flutter/material.dart";

import "../../core/nexo_colors.dart";
import "../../data/repositories/siex_repository.dart";
import "../widgets/nexo_lock_screen.dart";

class SiexModuleScreen extends StatefulWidget {
  const SiexModuleScreen({super.key});

  @override
  State<SiexModuleScreen> createState() => _SiexModuleScreenState();
}

class _SiexModuleScreenState extends State<SiexModuleScreen> {
  final _repo = SiexRepository();
  bool _loading = true;
  bool _unlocked = false;
  List<dynamic> _entries = [];
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final unlocked = await _repo.hasAccess();
      if (!unlocked) {
        if (mounted) setState(() {
          _unlocked = false;
          _loading = false;
        });
        return;
      }
      final entries = await _repo.fetchEntries();
      if (!mounted) return;
      setState(() {
        _unlocked = true;
        _entries = entries;
        _loading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.toString();
        _loading = false;
      });
    }
  }

  String _statusLabel(String status) {
    switch (status) {
      case "validado":
        return "Validado";
      case "pendiente_validacion":
        return "Pendiente perito";
      case "rechazado":
        return "Rechazado";
      default:
        return "Registrado";
    }
  }

  Color _statusColor(String status) {
    switch (status) {
      case "validado":
        return NexoColors.bioGreen;
      case "pendiente_validacion":
        return NexoColors.warningAmber;
      case "rechazado":
        return NexoColors.errorRed;
      default:
        return NexoColors.techCyan;
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }
    if (!_unlocked) {
      return const Scaffold(
        body: NexoLockScreen(
          moduleName: "NEXO SIEX",
          isB2C: true,
          message:
              "Digitaliza tu cuaderno de campo con validez normativa. Contrata el módulo SIEX o solicita alta en tu cooperativa.",
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text("NEXO SIEX"),
        actions: [IconButton(icon: const Icon(Icons.refresh), onPressed: _load)],
      ),
      body: _error != null
          ? Center(child: Text(_error!, style: const TextStyle(color: NexoColors.errorRed)))
          : _entries.isEmpty
              ? const Center(
                  child: Padding(
                    padding: EdgeInsets.all(24),
                    child: Text(
                      "Aún no hay actuaciones en tu cuaderno.\n\n"
                      "Registra un tratamiento fitosanitario desde Field (con finca SIGPAC) "
                      "y aparecerá aquí automáticamente.",
                      textAlign: TextAlign.center,
                    ),
                  ),
                )
              : ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: _entries.length,
                  itemBuilder: (context, i) {
                    final e = _entries[i] as Map<String, dynamic>;
                    final status = e["status"] as String? ?? "registrado";
                    return Card(
                      margin: const EdgeInsets.only(bottom: 12),
                      child: ExpansionTile(
                        title: Text(e["product_name"] as String? ?? "Tratamiento"),
                        subtitle: Text(
                          "${e["plague"]} · ${e["crop"]} · SIGPAC ${e["sigpac_code"]}",
                        ),
                        trailing: Chip(
                          label: Text(_statusLabel(status), style: const TextStyle(fontSize: 11)),
                          backgroundColor: _statusColor(status).withValues(alpha: 0.2),
                        ),
                        children: [
                          Padding(
                            padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(e["que_se_hizo"] as String? ?? "", style: const TextStyle(fontSize: 13)),
                                const SizedBox(height: 10),
                                Text(
                                  e["justificacion"] as String? ?? "",
                                  style: const TextStyle(fontSize: 12, color: NexoColors.textSecondary),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    );
                  },
                ),
    );
  }
}
