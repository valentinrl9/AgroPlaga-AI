class AgriZone {
  final int id;
  final String sigpacCode;
  final String name;
  final String province;
  final String municipalityCode;
  final double lat;
  final double lon;

  AgriZone({
    required this.id,
    required this.sigpacCode,
    required this.name,
    required this.province,
    required this.municipalityCode,
    required this.lat,
    required this.lon,
  });

  factory AgriZone.fromJson(Map<String, dynamic> json) {
    return AgriZone(
      id: json["id"] as int,
      sigpacCode: json["sigpac_code"] as String,
      name: json["name"] as String,
      province: json["province"] as String,
      municipalityCode: json["municipality_code"] as String,
      lat: (json["lat"] as num).toDouble(),
      lon: (json["lon"] as num).toDouble(),
    );
  }
}
