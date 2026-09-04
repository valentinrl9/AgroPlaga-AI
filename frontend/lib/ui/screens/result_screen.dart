import "package:flutter/material.dart";

import "../../core/nexo_colors.dart";
import "../../core/navigation.dart";
import "../../core/routes.dart";
import "../../data/repositories/activity_repository.dart";
import "../../data/repositories/analytics_repository.dart";
import "../../data/repositories/feedback_repository.dart";
import "../../data/repositories/incident_repository.dart";
import "../../data/repositories/scan_repository.dart";
import "../../models/analytics.dart";
import "../../models/scan.dart";
import "../../ml/plaga_result.dart";
import "../widgets/card_scan.dart";
import "../widgets/farmer_plague_selector.dart";
import "../widgets/low_confidence_banner.dart";
import "../widgets/official_attribution_line.dart";
import "../widgets/primary_button.dart";
import "../widgets/scan_validation_banner.dart";

class ResultScreen extends StatefulWidget {
  final Scan scan;
  final List<PlagueCandidate>? topCandidates;

  const ResultScreen({
    super.key,
    required this.scan,
    this.topCandidates,
  });

  @override
  State<ResultScreen> createState() => _ResultScreenState();
}

class _ResultScreenState extends State<ResultScreen> {
  final _feedbackRepo = FeedbackRepository();
  final _analyticsRepo = AnalyticsRepository();
  final _incidentRepo = IncidentRepository();
  final _scanRepo = ScanRepository();
  late Scan _scan;
  late Future<PlagaRecommendation> _recommendationFuture;
  String? _selectedPlague;
  bool _feedbackSent = false;
  bool _savingPlague = false;
  bool _plagueDirty = false;
  bool _sending = false;
  bool _openingIncident = false;
  bool _incidentOpened = false;
  int? _openedIncidentId;
  String? _incidentError;

  bool get _isTrackablePlague {
    final plague = _scan.effectivePlague.trim().toLowerCase();
    return plague.isNotEmpty && plague != "sana";
  }

  bool get _canEditPlague => !_scan.isVerifiedByTech && !_scan.isRejectedByTech;

  @override
  void initState() {
    super.initState();
    _scan = widget.scan;
    _selectedPlague = _scan.effectivePlague;
    _reloadRecommendations();
    _showScanGamificationToast();
  }

  Future<void> _showScanGamificationToast() async {
    try {
      final summary = await ActivityRepository().fetchSummary();
      if (!mounted) return;
      final v = summary.weeklyVigilance;
      final msg = v.completed
          ? "Reto semanal completado (${v.current}/${v.goal})"
          : "Reto semanal: ${v.current}/${v.goal} escaneo(s) esta semana";
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(msg),
          duration: const Duration(seconds: 3),
        ),
      );
    } catch (_) {}
  }

  void _reloadRecommendations() {
    _recommendationFuture = _analyticsRepo.fetchRecommendation(
      plague: _scan.effectivePlague,
      crop: _scan.crop,
      severity: _scan.severity,
    );
  }

  Future<void> _saveFarmerPlague() async {
    setState(() {
      _savingPlague = true;
      _incidentError = null;
    });
    try {
      final updated = await _scanRepo.setFarmerPlague(
        _scan.id,
        farmerPlague: farmerPlaguePayload(
          aiPlague: _scan.plague,
          selectedPlague: _selectedPlague,
        ),
      );
      if (!mounted) return;
      setState(() {
        _scan = updated;
        _selectedPlague = updated.effectivePlague;
        _plagueDirty = false;
        _reloadRecommendations();
      });
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text("Plaga actualizada. Tratamiento e incidencia usarán tu criterio."),
          backgroundColor: NexoColors.bioGreen,
        ),
      );
    } catch (error) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("Error: $error")));
    } finally {
      if (mounted) setState(() => _savingPlague = false);
    }
  }

  Future<void> _openIncident() async {
    setState(() {
      _openingIncident = true;
      _incidentError = null;
    });
    try {
      final incident = await _incidentRepo.openFromScan(_scan.id);
      if (!mounted) return;
      setState(() {
        _incidentOpened = true;
        _openedIncidentId = incident.id;
      });
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
        scanId: _scan.id,
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
    final scan = _scan;

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
            LowConfidenceBanner(confidence: scan.confidence),
            const SizedBox(height: 12),
            CardScan.fromScan(scan),
            const SizedBox(height: 16),
            if (_canEditPlague)
              PlagueSelectionHighlight(
                confidence: scan.confidence,
                child: FarmerPlagueSelector(
                  scan: scan,
                  selectedPlague: _selectedPlague,
                  topCandidates: widget.topCandidates,
                  enabled: !_savingPlague,
                  onChanged: (v) => setState(() {
                    _selectedPlague = v;
                    _plagueDirty = v?.trim().toLowerCase() != scan.effectivePlague.trim().toLowerCase();
                  }),
                ),
              ),
            if (_canEditPlague) ...[
              if (_plagueDirty || scan.hasFarmerOverride) ...[
                const SizedBox(height: 8),
                OutlinedButton(
                  onPressed: _savingPlague || !_plagueDirty ? null : _saveFarmerPlague,
                  child: Text(_savingPlague ? "Guardando plaga..." : "Guardar plaga elegida"),
                ),
              ],
              const SizedBox(height: 16),
            ] else if (scan.hasFarmerOverride) ...[
              Text(
                "Tu criterio: ${scan.effectivePlague} (IA: ${scan.plague})",
                style: const TextStyle(fontWeight: FontWeight.w600),
              ),
              const SizedBox(height: 16),
            ],
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
              key: ValueKey("${scan.effectivePlague}-${scan.severity}"),
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
                    OfficialAttributionLine(text: rec.displayAttribution),
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
              if (_incidentOpened) ...[
                const Text(
                  "Incidencia fitosanitaria abierta. Continúa el seguimiento en el CRM.",
                  style: TextStyle(color: NexoColors.bioGreen, fontWeight: FontWeight.w600),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 12),
                PrimaryButton(
                  label: "Abrir CRM de la incidencia",
                  onPressed: _openedIncidentId == null
                      ? null
                      : () => Navigator.pushNamed(
                            context,
                            Routes.incidentDetail,
                            arguments: _openedIncidentId,
                          ),
                ),
              ]
              else ...[
                PrimaryButton(
                  label: _openingIncident ? "Abriendo incidencia..." : "Abrir incidencia fitosanitaria",
                  onPressed: _openingIncident ? null : _openIncident,
                ),
                if (scan.farmId == null)
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
