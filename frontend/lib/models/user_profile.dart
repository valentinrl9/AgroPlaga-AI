class UserProfile {
  final int id;
  final String name;
  final String email;
  final String role;
  final int contributionCount;
  final bool hasFieldPremium;
  final bool hasClimateModule;
  final bool hasSiexEnterprise;

  UserProfile({
    required this.id,
    required this.name,
    required this.email,
    required this.role,
    required this.contributionCount,
    this.hasFieldPremium = false,
    this.hasClimateModule = false,
    this.hasSiexEnterprise = false,
  });

  factory UserProfile.fromJson(Map<String, dynamic> json) {
    return UserProfile(
      id: json["id"] as int,
      name: json["name"] as String,
      email: json["email"] as String,
      role: json["role"] as String? ?? "farmer",
      contributionCount: json["contribution_count"] as int? ?? 0,
      hasFieldPremium: json["has_field_premium"] as bool? ?? false,
      hasClimateModule: json["has_climate_module"] as bool? ?? false,
      hasSiexEnterprise: json["has_siex_enterprise"] as bool? ?? false,
    );
  }

  bool get isTechOrAdmin => role == "tech" || role == "admin";
}
