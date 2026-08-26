import "../../ml/plaga_result.dart";
import "../../models/scan.dart";

/// Argumentos opcionales al abrir la pantalla de resultado tras un escaneo nuevo.
class ResultScreenArgs {
  final Scan scan;
  final List<PlagueCandidate>? topCandidates;

  const ResultScreenArgs({
    required this.scan,
    this.topCandidates,
  });
}
