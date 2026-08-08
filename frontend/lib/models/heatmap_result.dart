import "../../models/heatmap_cell.dart";

class HeatmapResult {
  final List<HeatmapCell> cells;
  final int hours;
  final bool historicalEnabled;
  final int maxHours;
  final List<int> allowedHours;

  HeatmapResult({
    required this.cells,
    required this.hours,
    required this.historicalEnabled,
    required this.maxHours,
    required this.allowedHours,
  });
}
