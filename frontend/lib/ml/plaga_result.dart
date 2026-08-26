class PlagueCandidate {
  final String plague;
  final double confidence;

  const PlagueCandidate({
    required this.plague,
    required this.confidence,
  });

  String get confidencePercent => "${(confidence * 100).toStringAsFixed(0)}%";
}

class PlagaResult {
  final String plague;
  final double confidence;
  final int suggestedSeverity;
  final String modelVersion;
  final List<PlagueCandidate> topCandidates;

  const PlagaResult({
    required this.plague,
    required this.confidence,
    required this.suggestedSeverity,
    this.modelVersion = "v1.0",
    this.topCandidates = const [],
  });

  String get confidencePercent => "${(confidence * 100).toStringAsFixed(1)}%";

  List<PlagueCandidate> get displayCandidates {
    if (topCandidates.isNotEmpty) return topCandidates;
    return [PlagueCandidate(plague: plague, confidence: confidence)];
  }
}

List<PlagueCandidate> topCandidatesFromScores(
  List<double> scores,
  List<String> labels, {
  int count = 3,
}) {
  if (scores.isEmpty || labels.isEmpty) return const [];

  final ranked = List<_ScoredLabelIndex>.generate(
    scores.length,
    (index) => _ScoredLabelIndex(index: index, score: scores[index]),
  )..sort((a, b) => b.score.compareTo(a.score));

  final candidates = <PlagueCandidate>[];
  for (final entry in ranked) {
    if (entry.index >= labels.length) continue;
    final plague = labels[entry.index].trim().toLowerCase();
    if (plague.isEmpty) continue;
    if (candidates.any((c) => c.plague == plague)) continue;
    candidates.add(
      PlagueCandidate(
        plague: plague,
        confidence: entry.score.clamp(0.0, 1.0),
      ),
    );
    if (candidates.length >= count) break;
  }
  return candidates;
}

class _ScoredLabelIndex {
  final int index;
  final double score;

  const _ScoredLabelIndex({required this.index, required this.score});
}
