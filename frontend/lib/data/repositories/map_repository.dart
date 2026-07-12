import "../api_client.dart";
import "../../models/heatmap_cell.dart";
import "../../models/outbreak_event.dart";
import "outbreak_event_repository.dart";

class MapFilters {
  final int hours;
  final int minSeverity;
  final String? plague;
  final bool validatedOnly;

  const MapFilters({
    this.hours = 168,
    this.minSeverity = 1,
    this.plague,
    this.validatedOnly = false,
  });

  Map<String, String> get queryParams => {
        "hours": hours.toString(),
        "min_severity": minSeverity.toString(),
        if (plague != null && plague!.isNotEmpty) "plague": plague!,
        if (validatedOnly) "validated_only": "true",
      };

  @override
  bool operator ==(Object other) =>
      other is MapFilters &&
      other.hours == hours &&
      other.minSeverity == minSeverity &&
      other.plague == plague &&
      other.validatedOnly == validatedOnly;

  @override
  int get hashCode => Object.hash(hours, minSeverity, plague, validatedOnly);
}

class MapRepository {
  final OutbreakEventRepository _events = OutbreakEventRepository();
  final ApiClient _client = ApiClient.instance;

  Future<List<OutbreakEvent>> fetchOutbreaks({MapFilters? filters}) {
    return _events.fetchEvents(
      plague: filters?.plague,
      hours: filters?.hours,
      minSeverity: filters?.minSeverity,
    );
  }

  Future<List<HeatmapCell>> fetchHeatmap({MapFilters? filters}) async {
    final params = (filters ?? const MapFilters()).queryParams;
    final query = params.entries.map((e) => "${e.key}=${Uri.encodeComponent(e.value)}").join("&");
    final response = await _client.get("/api/v1/heatmap?$query");
    final cells = response["cells"];
    if (cells is List) {
      return cells
          .map((item) => HeatmapCell.fromJson(Map<String, dynamic>.from(item as Map)))
          .toList();
    }
    return [];
  }
}
