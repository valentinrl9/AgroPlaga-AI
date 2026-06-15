import "package:flutter/material.dart";

import "../../core/navigation.dart";
import "../../core/routes.dart";
import "../../core/session.dart";
import "../../data/repositories/analytics_repository.dart";
import "../../data/repositories/feedback_repository.dart";
import "../../models/analytics.dart";
import "../../models/scan.dart";
import "../widgets/card_scan.dart";
import "../widgets/primary_button.dart";

class ResultScreen extends StatefulWidget {
  final Scan scan;

  const ResultScreen({super.key, required this.scan});

  @override
  State<ResultScreen> createState() => _ResultScreenState();
}

class _ResultScreenState extends State<ResultScreen> {
  final _feedbackRepo = FeedbackRepository();
  final _analyticsRepo = AnalyticsRepository();
  late Future<PlagaRecommendation> _recommendationFuture;
  bool _feedbackSent = false;
  bool _sending = false;
  bool _alreadyContributed = false;

  @override
  void initState() {
    super.initState();
    final scan = widget.scan;
    _recommendationFuture = _analyticsRepo.fetchRecommendation(
      plague: scan.plague,
      crop: scan.crop,
      severity: scan.severity,
    );
    _loadContributionState();
  }

  Future<void> _loadContributionState() async {
    final contributed = await Session.hasContributed(widget.scan.id);
    if (mounted) setState(() => _alreadyContributed = contributed);
  }

  Future<void> _sendFeedback({required bool isCorrect, String? correctedPlague}) async {
    setState(() => _sending = true);
    try {
      await _feedbackRepo.submit(
        scanId: widget.scan.id,
        isCorrect: isCorrect,
        correctedPlague: correctedPlague,
      );
      if (mounted) setState(() => _feedbackSent = true);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("Error: $e")));
      }
    } finally {
      if (mounted) setState(() => _sending = false);
    }
  }

  Future<void> _showCorrectionDialog() async {
    final controller = TextEditingController();
    final plague = await showDialog<String>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text("Plaga correcta"),
        content: TextField(
          controller: controller,
          decoration: const InputDecoration(hintText: "Ej: mildiu, trips..."),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text("Cancelar")),
          TextButton(
            onPressed: () => Navigator.pop(context, controller.text.trim()),
            child: const Text("Enviar"),
          ),
        ],
      ),
    );
    if (plague != null && plague.isNotEmpty) {
      await _sendFeedback(isCorrect: false, correctedPlague: plague);
    }
  }

  @override
  Widget build(BuildContext context) {
    final scan = widget.scan;

    return Scaffold(
      appBar: AppBar(title: const Text("Resultado del escaneo")),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text(
              "Posible plaga detectada",
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 24),
            CardScan.fromScan(scan),
            const SizedBox(height: 16),
            const Text("¿El diagnóstico fue correcto?", style: TextStyle(fontWeight: FontWeight.w600)),
            const SizedBox(height: 8),
            if (_feedbackSent)
              const Text("Gracias, tu feedback ayuda a mejorar la IA.", style: TextStyle(color: Color(0xFF2E7D32)))
            else
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton(
                      onPressed: _sending ? null : () => _sendFeedback(isCorrect: true),
                      child: const Text("Sí, correcto"),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: OutlinedButton(
                      onPressed: _sending ? null : _showCorrectionDialog,
                      child: const Text("No, corregir"),
                    ),
                  ),
                ],
              ),
            const SizedBox(height: 16),
            const Text("Recomendaciones personalizadas", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),
            Expanded(
              child: FutureBuilder<PlagaRecommendation>(
                future: _recommendationFuture,
                builder: (context, snapshot) {
                  if (snapshot.connectionState == ConnectionState.waiting) {
                    return const Center(child: CircularProgressIndicator());
                  }
                  if (snapshot.hasError || !snapshot.hasData) {
                    return const Text("No se pudieron cargar las recomendaciones.");
                  }
                  final rec = snapshot.data!;
                  return SingleChildScrollView(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Chip(
                          label: Text("Urgencia: ${rec.urgency}"),
                          backgroundColor: rec.urgency == "alta"
                              ? const Color(0xFFFFEBEE)
                              : const Color(0xFFE8F5E9),
                        ),
                        const SizedBox(height: 12),
                        Text(rec.recommendation, style: const TextStyle(fontSize: 14)),
                        const SizedBox(height: 16),
                        const Text("Prevención", style: TextStyle(fontWeight: FontWeight.bold)),
                        const SizedBox(height: 6),
                        Text(rec.preventionTip, style: const TextStyle(fontSize: 14, color: Color(0xFF424242))),
                      ],
                    ),
                  );
                },
              ),
            ),
            const SizedBox(height: 16),
            if (_alreadyContributed) ...[
              const Icon(Icons.check_circle, color: Color(0xFF2E7D32), size: 32),
              const SizedBox(height: 8),
              const Text(
                "Ya contribuiste este escaneo al mapa comunitario.",
                style: TextStyle(fontSize: 15, fontWeight: FontWeight.w600, color: Color(0xFF2E7D32)),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 12),
              OutlinedButton(
                onPressed: () => Navigator.pushNamed(context, Routes.map),
                child: const Text("Ver mapa de focos"),
              ),
            ] else ...[
              const Text(
                "¿Quieres contribuir al mapa de plagas de tu zona?",
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 8),
              const Text(
                "Tu aporte es anónimo y ayuda a otros agricultores de la comarca.",
                style: TextStyle(fontSize: 13, color: Color(0xFF424242)),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 16),
              PrimaryButton(
                label: "Sí, contribuir",
                onPressed: () => Navigator.pushNamed(context, Routes.contribute, arguments: scan),
              ),
            ],
            const SizedBox(height: 12),
            OutlinedButton(
              onPressed: () => goHome(context),
              style: OutlinedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
                side: const BorderSide(color: Color(0xFF2E7D32)),
              ),
              child: Text(_alreadyContributed ? "Volver al inicio" : "No ahora"),
            ),
          ],
        ),
      ),
    );
  }
}
