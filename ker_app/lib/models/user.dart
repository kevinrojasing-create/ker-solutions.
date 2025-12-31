class User {
  final int id;
  final String email;
  final String fullName;
  final String role;
  final String? companyName;
  final String plan;

  User({
    required this.id,
    required this.email,
    required this.fullName,
    required this.role,
    this.companyName,
    required this.plan,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'],
      email: json['email'],
      fullName: json['full_name'],
      role: json['role'] ?? 'staff',
      companyName: json['company_name'],
      plan: json['plan'] ?? 'digital',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
      'full_name': fullName,
      'role': role,
      'company_name': companyName,
      'plan': plan,
    };
  }
  
  bool get hasIoTUsers => plan == 'monitor_360';
  bool get hasAiFeatures => plan == 'expert' || plan == 'monitor_360';
}
