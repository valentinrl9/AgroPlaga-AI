import "package:flutter/material.dart";

import "../../core/nexo_colors.dart";
import "../../data/repositories/siex_repository.dart";
import "../layout/mobile_layout.dart";
import "../widgets/nexo_lock_screen.dart";
import "../widgets/sigpac_siex_banner.dart";

class SiexModuleScreen extends StatefulWidget {
  final bool isActive;

  const SiexModuleScreen({super.key, this.isActive = true});

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

  @override
  void didUpdateWidget(SiexModuleScreen oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.isActive && !oldWidget.isActive) {
      _load();
    }
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final unlocked = await _repo.hasAccess();
      if (!unlocked) {
        if (mounted) {
          setState(() {
            _unlocked = false;
            _loading = false;
          });
        }
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

  bool get _hasPendingSigpac =>
      _entries.any((e) => (e as Map<String, dynamic>)["status"] == "pendiente_sigpac");

  String _statusLabel(String status) {
    switch (status) {
      case "validado":
        return "Validado";
      case "pendiente_validacion":
        return "Pendiente perito";
      case "pendiente_sigpac":
        return "Pendiente SIGPAC";
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
      case "pendiente_sigpac":
        return NexoColors.techCyan;
      case "rechazado":
        return NexoColors.errorRed;
      default:
        return NexoColors.techCyan;
    }
  }

  Widget _emptyState() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.description_outlined, size: 48, color: NexoColors.textSecondary),
            const SizedBox(height: 16),
            const Text(
              "Aún no hay actuaciones en tu cuaderno.",
              textAlign: TextAlign.center,
              style: TextStyle(fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 12),
            const Text(
              "Al registrar un tratamiento desde una incidencia o desde Field, "
              "la entrada SIEX aparece aquí automáticamente.\n\n"
              "Si acabas de tratar, pulsa actualizar (↻).",
              textAlign: TextAlign.center,
              style: TextStyle(color: NexoColors.textSecondary, fontSize: 13),
            ),
            const SizedBox(height: 16),
            const SigpacSiexBanner(),
          ],
        ),
      ),
    );
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
          ? MobileLayout.errorState(error: _error!, onRetry: _load)
          : _entries.isEmpty
              ? _emptyState()
              : ListView.builder(
                  padding: MobileLayout.scrollPadding(context),
                  itemCount: _entries.length + (_hasPendingSigpac ? 1 : 0),
                  itemBuilder: (context, i) {
                    if (_hasPendingSigpac && i == 0) {
                      return const Padding(
                        padding: EdgeInsets.only(bottom: 12),
                        child: SigpacSiexBanner(
                          message:
                              "Hay entradas con SIGPAC pendiente. Edita la finca correspondiente "
                              "en «Mis fincas» e indica el código del recinto invernadero.",
                        ),
                      );
                    }
                    final entryIndex = _hasPendingSigpac ? i - 1 : i;
                    final e = _entries[entryIndex] as Map<String, dynamic>;
                    final status = e["status"] as String? ?? "registrado";
                    final pendingSigpac = status == "pendiente_sigpac";
                    return Card(
                      margin: const EdgeInsets.only(bottom: 12),
                      child: ExpansionTile(
                        title: Text(e["product_name"] as String? ?? "Tratamiento"),
                        subtitle: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              "${e["plague"]} · ${e["crop"]} · SIGPAC ${e["sigpac_code"]}",
                            ),
                            if (pendingSigpac) ...[
                              const SizedBox(height: 4),
                              const Text(
                                "Añade el SIGPAC del recinto en «Mis fincas» para completar el cuaderno.",
                                style: TextStyle(fontSize: 12, color: NexoColors.warningAmber),
                              ),
                            ],
                          ],
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
