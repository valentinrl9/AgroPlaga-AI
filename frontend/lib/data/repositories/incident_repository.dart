import "../api_client.dart";
import "../../models/pest_incident.dart";

class IncidentRepository {
  final ApiClient _client = ApiClient.instance;

  Future<List<PestIncident>> fetchIncidents({bool activeOnly = true}) async {
    final path = activeOnly ? "/api/v1/incidents?active_only=true" : "/api/v1/incidents?active_only=false";
    final list = await _client.getList(path);
    return list
        .map((item) => PestIncident.fromJson(Map<String, dynamic>.from(item as Map)))
        .toList();
  }

  Future<PestIncident> fetchIncident(int incidentId) async {
    final json = await _client.get("/api/v1/incidents/$incidentId");
    return PestIncident.fromJson(json);
  }

  Future<PestIncident> openFromScan(int scanId) async {
    final json = await _client.postAuth("/api/v1/incidents", {"scan_id": scanId});
    return PestIncident.fromJson(json);
  }

  Future<PestIncident> advance(int incidentId, {String? notes}) async {
    final json = await _client.patchAuth(
      "/api/v1/incidents/$incidentId/advance",
      {if (notes != null && notes.trim().isNotEmpty) "notes": notes.trim()},
    );
    return PestIncident.fromJson(json);
  }

  Future<PestIncident> prescribe(
    int incidentId, {
    required String registryNo,
    required double surfaceM2,
    String? notes,
  }) async {
    final json = await _client.patchAuth(
      "/api/v1/incidents/$incidentId/prescribe",
      {
        "registry_no": registryNo,
        "surface_m2": surfaceM2,
        if (notes != null && notes.trim().isNotEmpty) "notes": notes.trim(),
      },
    );
    return PestIncident.fromJson(json);
  }

  Future<PestIncident> applyTreatment(int incidentId, {bool ackUnverified = false, String? notes}) async {
    final json = await _client.patchAuth(
      "/api/v1/incidents/$incidentId/apply-treatment",
      {
        "ack_unverified": ackUnverified,
        if (notes != null && notes.trim().isNotEmpty) "notes": notes.trim(),
      },
    );
    return PestIncident.fromJson(json);
  }

  Future<PestIncident> startEvaluation(int incidentId) async {
    final json = await _client.patchAuth("/api/v1/incidents/$incidentId/start-evaluation", {});
    return PestIncident.fromJson(json);
  }

  Future<PestIncident> attachEvaluationScan(int incidentId, int evaluationScanId) async {
    final json = await _client.patchAuth(
      "/api/v1/incidents/$incidentId/evaluation-scan",
      {"evaluation_scan_id": evaluationScanId},
    );
    return PestIncident.fromJson(json);
  }

  Future<PestIncident> evaluate(
    int incidentId, {
    required bool improved,
    int? evaluationScanId,
    String? notes,
  }) async {
    final json = await _client.patchAuth(
      "/api/v1/incidents/$incidentId/evaluate",
      {
        "improved": improved,
        if (evaluationScanId != null) "evaluation_scan_id": evaluationScanId,
        if (notes != null && notes.trim().isNotEmpty) "notes": notes.trim(),
      },
    );
    return PestIncident.fromJson(json);
  }

  Future<PestIncident> close(int incidentId, {required String outcome, String? notes}) async {
    final json = await _client.patchAuth(
      "/api/v1/incidents/$incidentId/close",
      {
        "outcome": outcome,
        if (notes != null && notes.trim().isNotEmpty) "notes": notes.trim(),
      },
    );
    return PestIncident.fromJson(json);
  }
}
