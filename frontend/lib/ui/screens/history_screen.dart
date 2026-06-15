import "package:flutter/material.dart";

import "../../core/auth_redirect.dart";
import "../../core/routes.dart";
import "../../core/session.dart";
import "../../data/repositories/scan_repository.dart";
import "../../models/scan.dart";
import "../widgets/primary_button.dart";
import "../widgets/severity_badge.dart";

class HistoryScreen extends StatefulWidget {
  const HistoryScreen({super.key});

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  final ScanRepository _scanRepository = ScanRepository();
  late Future<List<Scan>> _scansFuture;
  Set<int> _contributedIds = {};

  @override
  void initState() {
    super.initState();
    _scansFuture = _loadScans();
  }

  Future<List<Scan>> _loadScans() async {
    _contributedIds = await Session.contributedScanIds;
    return _scanRepository.fetchScans();
  }

  void _reload() {
    setState(() {
      _scansFuture = _loadScans();
    });
  }

  String _formatDate(DateTime? date) {
    if (date == null) return "";
    return "${date.day.toString().padLeft(2, "0")}/${date.month.toString().padLeft(2, "0")}/${date.year}";
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Historial de escaneos"),
        actions: [
          IconButton(
            icon: const Icon(Icons.insights),
            tooltip: "Mi analítica",
            onPressed: () => Navigator.pushNamed(context, Routes.analytics),
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text("Tus escaneos recientes", style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            const Text(
              "Toca un escaneo para ver recomendaciones personalizadas.",
              style: TextStyle(color: Color(0xFF424242)),
            ),
            const SizedBox(height: 16),
            Expanded(
              child: FutureBuilder<List<Scan>>(
                future: _scansFuture,
                builder: (context, snapshot) {
                  if (snapshot.connectionState == ConnectionState.waiting) {
                    return const Center(child: CircularProgressIndicator());
                  }
                  if (snapshot.hasError) {
                    if (AuthRedirect.isUnauthorized(snapshot.error!)) {
                      return const Center(child: Text("Sesión expirada. Redirigiendo al login..."));
                    }
                    return Center(child: Text("Error: ${snapshot.error}"));
                  }

                  final scans = snapshot.data ?? [];
                  if (scans.isEmpty) {
                    return Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          const Icon(Icons.eco_outlined, size: 48, color: Color(0xFF2E7D32)),
                          const SizedBox(height: 12),
                          const Text("Aún no tienes escaneos."),
                          const SizedBox(height: 16),
                          PrimaryButton(
                            label: "Hacer primer escaneo",
                            onPressed: () => Navigator.pushNamed(context, Routes.scan),
                          ),
                        ],
                      ),
                    );
                  }

                  return ListView.separated(
                    itemCount: scans.length,
                    separatorBuilder: (_, __) => const SizedBox(height: 8),
                    itemBuilder: (context, index) {
                      final scan = scans[index];
                      return Card(
                        child: ListTile(
                          title: Text(scan.plague, style: const TextStyle(fontWeight: FontWeight.bold)),
                          subtitle: Text(
                            "${scan.crop} · ${(scan.confidence * 100).toStringAsFixed(0)}% conf."
                            "${scan.createdAt != null ? " · ${_formatDate(scan.createdAt)}" : ""}",
                          ),
                          trailing: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              if (_contributedIds.contains(scan.id))
                                const Padding(
                                  padding: EdgeInsets.only(right: 8),
                                  child: Icon(Icons.map, size: 18, color: Color(0xFF2E7D32)),
                                ),
                              SeverityBadge(severity: scan.severity),
                            ],
                          ),
                          onTap: () => Navigator.pushNamed(context, Routes.result, arguments: scan),
                        ),
                      );
                    },
                  );
                },
              ),
            ),
            PrimaryButton(label: "Actualizar", onPressed: _reload),
          ],
        ),
      ),
    );
  }
}
