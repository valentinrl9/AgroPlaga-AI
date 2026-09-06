class OfficialSource {
  final String id;
  final String kind;
  final String kindLabel;
  final String issuer;
  final String title;
  final String? url;
  final String? note;

  OfficialSource({
    required this.id,
    required this.kind,
    required this.kindLabel,
    required this.issuer,
    required this.title,
    this.url,
    this.note,
  });

  factory OfficialSource.fromJson(Map<String, dynamic> json) {
    return OfficialSource(
      id: json["id"] as String? ?? "",
      kind: json["kind"] as String? ?? "orientation",
      kindLabel: json["kind_label"] as String? ?? "Fuente",
      issuer: json["issuer"] as String? ?? "",
      title: json["title"] as String? ?? "",
      url: json["url"] as String?,
      note: json["note"] as String?,
    );
  }

  bool get isOfficial =>
      kind == "official_protocol" || kind == "official_bulletin" || kind == "official_registry";
}
