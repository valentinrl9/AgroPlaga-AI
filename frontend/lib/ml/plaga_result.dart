class PlagaResult {
  final String plague;
  final double confidence;
  final int suggestedSeverity;
  final String modelVersion;

  const PlagaResult({
    required this.plague,
    required this.confidence,
    required this.suggestedSeverity,
    this.modelVersion = "v1.0",
  });

  String get confidencePercent => "${(confidence * 100).toStringAsFixed(1)}%";
}
