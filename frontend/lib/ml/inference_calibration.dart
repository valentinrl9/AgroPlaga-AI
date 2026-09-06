import "plaga_result.dart";

/// Ajusta scores crudos del modelo para reflejar incertidumbre real en campo.
class InferenceCalibration {
  InferenceCalibration._();

  /// Margen mínimo top1−top2 para confiar en la predicción principal.
  static const minTopMargin = 0.12;

  /// Confianza máxima mostrada cuando el margen es bajo.
  static const cappedConfidenceWhenAmbiguous = 0.38;

  static PlagaResult apply({
    required List<double> scores,
    required List<String> labels,
    required String modelVersion,
    required int suggestedSeverity,
    int topCount = 3,
  }) {
    final candidates = topCandidatesFromScores(scores, labels, count: topCount);
    if (candidates.isEmpty) {
      throw StateError("inferencia sin candidatos");
    }

    final sorted = List<double>.from(scores)..sort((a, b) => b.compareTo(a));
    final top1Score = sorted.isNotEmpty ? sorted.first : 0.0;
    final top2Score = sorted.length > 1 ? sorted[1] : 0.0;
    final margin = (top1Score - top2Score).clamp(0.0, 1.0);

    final rawConfidence = candidates.first.confidence;
    final ambiguous = rawConfidence < ScanInferenceThresholds.lowConfidence ||
        margin < minTopMargin;

    final displayConfidence = ambiguous
        ? rawConfidence.clamp(0.0, cappedConfidenceWhenAmbiguous)
        : rawConfidence;

    return PlagaResult(
      plague: candidates.first.plague,
      confidence: displayConfidence,
      rawConfidence: rawConfidence,
      topMargin: margin,
      needsConfirmation: ambiguous,
      suggestedSeverity: suggestedSeverity,
      modelVersion: modelVersion,
      topCandidates: candidates,
    );
  }
}
