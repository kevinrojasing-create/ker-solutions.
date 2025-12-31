class Local {
  final int id;
  final String name;
  final String address;
  final String? description;
  final int ownerId;
  final bool isActive;

  Local({
    required this.id,
    required this.name,
    required this.address,
    this.description,
    required this.ownerId,
    required this.isActive,
  });

  factory Local.fromJson(Map<String, dynamic> json) {
    return Local(
      id: json['id'],
      name: json['name'],
      address: json['address'],
      description: json['description'],
      ownerId: json['owner_id'],
      isActive: json['is_active'] ?? true,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'address': address,
      'description': description,
    };
  }
}
