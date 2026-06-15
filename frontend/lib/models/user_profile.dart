class UserProfile {
  final int id;
  final String name;
  final String email;
  final String role;
  final int contributionCount;

  UserProfile({
    required this.id,
    required this.name,
    required this.email,
    required this.role,
    required this.contributionCount,
  });

  factory UserProfile.fromJson(Map<String, dynamic> json) {
    return UserProfile(
      id: json["id"] as int,
      name: json["name"] as String,
      email: json["email"] as String,
      role: json["role"] as String? ?? "farmer",
      contributionCount: json["contribution_count"] as int? ?? 0,
    );
  }

  bool get isTechOrAdmin => role == "tech" || role == "admin";
}
