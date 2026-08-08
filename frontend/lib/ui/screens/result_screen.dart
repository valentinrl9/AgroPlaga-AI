import "package:flutter/material.dart";

import "../../core/nexo_colors.dart";
import "../../core/navigation.dart";
import "../../core/routes.dart";
import "../../data/repositories/analytics_repository.dart";
import "../../data/repositories/feedback_repository.dart";
import "../../data/repositories/incident_repository.dart";
import "../../models/analytics.dart";
import "../../models/scan.dart";
import "../widgets/card_scan.dart";
import "../widgets/primary_button.dart";
import "../widgets/scan_validation_banner.dart";

class ResultScreen extends StatefulWidget {
  final Scan scan;

  const ResultScreen({super.key, required this.scan});

  @override
  State<ResultScreen> createState() => _ResultScreenState();
}

class _ResultScreenState extends State<ResultScreen> {
  final _feedbackRepo = FeedbackRepository();
  final _analyticsRepo = AnalyticsRepository();
  final _incidentRepo = IncidentRepository();
  late Future<PlagaRecommendation> _recommendationFuture;
  bool _feedbackSent = false;
  bool _sending = false;
  bool _openingIncident = false;
  bool _incidentOpened = false;
  String? _incidentError;

  bool get _isTrackablePlague {
    final plague = widget.scan.effectivePlague.trim().toLowerCase();
    return plague.isNotEmpty && plague != "sana";
  }

  @override
  void initState() {
    super.initState();
    final scan = widget.scan;
    _recommendationFuture = _analyticsRepo.fetchRecommendation(
      plague: scan.plague,
      crop: scan.crop,
      severity: scan.severity,
    );
  }

  Future<void> _openIncident() async {
    setState(() {
      _openingIncident = true;
      _incidentError = null;
    });
    try {
      await _incidentRepo.openFromScan(widget.scan.id);
      if (!mounted) return;
      setState(() => _incidentOpened = true);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text("Incidencia abierta. Aparece en el mapa comunitario de tu municipio."),
          backgroundColor: NexoColors.bioGreen,
        ),
      );
    } catch (error) {
      if (!mounted) return;
      setState(() => _incidentError = error.toString());
    } finally {
      if (mounted) setState(() => _openingIncident = false);
    }
  }

  Future<void> _sendUsefulnessFeedback({required bool isHelpful}) async {
    setState(() => _sending = true);
    try {
      await _feedbackRepo.submit(
        scanId: widget.scan.id,
        isCorrect: isHelpful,
        comment: isHelpful ? "util_orientacion" : "no_confianza_utilidad",
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

  @override
  Widget build(BuildContext context) {
    final scan = widget.scan;

    return Scaffold(
      appBar: AppBar(title: const Text("Resultado del escaneo")),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text(
              "Orientación automática",
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 6),
            const Text(
              "No sustituye al técnico. Si dudas, consulta con tu asesor.",
              style: TextStyle(fontSize: 13, color: NexoColors.textSecondary),
            ),
            const SizedBox(height: 20),
            ScanValidationBanner(scan: scan),
            const SizedBox(height: 12),
            CardScan.fromScan(scan),
            const SizedBox(height: 16),
            const Text(
              "¿Te resultó útil este diagnóstico?",
              style: TextStyle(fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 4),
            const Text(
              "No hace falta que sepas el nombre exacto de la plaga.",
              style: TextStyle(fontSize: 12, color: NexoColors.textSecondary),
            ),
            const SizedBox(height: 8),
            if (_feedbackSent)
              const Text(
                "Gracias. Tu opinión nos ayuda a mejorar la app.",
                style: TextStyle(color: NexoColors.bioGreen),
              )
            else
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton(
                      onPressed: _sending ? null : () => _sendUsefulnessFeedback(isHelpful: true),
                      child: const Text("Sí, me orienta"),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: OutlinedButton(
                      onPressed: _sending ? null : () => _sendUsefulnessFeedback(isHelpful: false),
                      child: const Text("No, no me fío"),
                    ),
                  ),
                ],
              ),
            const SizedBox(height: 16),
            const Text("Recomendaciones personalizadas", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),
            FutureBuilder<PlagaRecommendation>(
              future: _recommendationFuture,
              builder: (context, snapshot) {
                if (snapshot.connectionState == ConnectionState.waiting) {
                  return const Padding(
                    padding: EdgeInsets.symmetric(vertical: 24),
                    child: Center(child: CircularProgressIndicator()),
                  );
                }
                if (snapshot.hasError || !snapshot.hasData) {
                  return const Text("No se pudieron cargar las recomendaciones.");
                }
                final rec = snapshot.data!;
                return Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Chip(
                      label: Text("Urgencia: ${rec.urgency}"),
                      backgroundColor: rec.urgency == "alta"
                          ? NexoColors.errorRed.withValues(alpha: 0.18)
                          : NexoColors.bioGreen.withValues(alpha: 0.18),
                    ),
                    const SizedBox(height: 12),
                    Text(rec.recommendation, style: const TextStyle(fontSize: 14)),
                    const SizedBox(height: 16),
                    const Text("Prevención", style: TextStyle(fontWeight: FontWeight.bold)),
                    const SizedBox(height: 6),
                    Text(rec.preventionTip, style: const TextStyle(fontSize: 14, color: NexoColors.textPrimary)),
                  ],
                );
              },
            ),
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: NexoColors.bioGreen.withValues(alpha: 0.12),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Text(
                "Participas en el mapa comunitario anónimo según aceptaste al registrarte. "
                "Las incidencias fitosanitarias abiertas alimentarán el mapa de calor.",
                style: TextStyle(fontSize: 13, color: NexoColors.textPrimary),
                textAlign: TextAlign.center,
              ),
            ),
            const SizedBox(height: 12),
            OutlinedButton(
              onPressed: () => Navigator.pushNamed(context, Routes.map),
              child: const Text("Ver mapa de focos"),
            ),
            if (_isTrackablePlague) ...[
              const SizedBox(height: 12),
              if (_incidentOpened)
                const Text(
                  "Incidencia fitosanitaria abierta. Sigue el seguimiento en Mis incidencias.",
                  style: TextStyle(color: NexoColors.bioGreen, fontWeight: FontWeight.w600),
                  textAlign: TextAlign.center,
                )
              else ...[
                PrimaryButton(
                  label: _openingIncident ? "Abriendo incidencia..." : "Abrir incidencia fitosanitaria",
                  onPressed: _openingIncident ? null : _openIncident,
                ),
                if (widget.scan.farmId == null)
                  const Padding(
                    padding: EdgeInsets.only(top: 8),
                    child: Text(
                      "Vincula el escaneo a una finca con municipio para abrir incidencia.",
                      style: TextStyle(fontSize: 12, color: NexoColors.warningAmber),
                      textAlign: TextAlign.center,
                    ),
                  ),
                if (_incidentError != null)
                  Padding(
                    padding: const EdgeInsets.only(top: 8),
                    child: Text(
                      _incidentError!,
                      style: const TextStyle(color: NexoColors.errorRed, fontSize: 12),
                      textAlign: TextAlign.center,
                    ),
                  ),
              ],
            ],
            const SizedBox(height: 12),
            if (!scan.isRejectedByTech)
              OutlinedButton(
                onPressed: () => Navigator.pushNamed(context, Routes.registerTreatment, arguments: scan),
                child: Text(
                  scan.isVerifiedByTech
                      ? "Registrar tratamiento (carencia)"
                      : "Registrar bajo mi responsabilidad",
                ),
              )
            else
              const Text(
                "Registro de tratamiento deshabilitado para escaneos rechazados.",
                style: TextStyle(color: NexoColors.errorRed, fontSize: 13),
                textAlign: TextAlign.center,
              ),
            if (scan.isUnverified) ...[
              const SizedBox(height: 8),
              const Text(
                "Recomendado: comparte el escaneo con el perito y espera validación antes de tratar.",
                style: TextStyle(fontSize: 12, color: NexoColors.warningAmber),
                textAlign: TextAlign.center,
              ),
            ],
            const SizedBox(height: 12),
            OutlinedButton(
              onPressed: () => goHome(context),
              style: OutlinedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
                side: const BorderSide(color: NexoColors.bioGreen),
              ),
              child: Text("Volver al inicio"),
            ),
            const SizedBox(height: 8),
          ],
        ),
      ),
    );
  }
}
