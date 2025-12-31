class Asset {
  final int id;
  final String name;
  final int localId;
  final String? brand;
  final String? model;
  final String? serialNumber;
  final String status;
  final String? qrCode;
  final int healthScore;

  Asset({
    required this.id,
    required this.name,
    required this.localId,
    this.brand,
    this.model,
    this.serialNumber,
    required this.status,
    this.qrCode,
    this.healthScore = 100,
  });

  factory Asset.fromJson(Map<String, dynamic> json) {
    return Asset(
      id: json['id'],
      name: json['name'],
      localId: json['local_id'],
      brand: json['brand'],
      model: json['model'],
      serialNumber: json['serial_number'],
      status: json['status'],
      qrCode: json['qr_code'],
      healthScore: json['health_score'] ?? 100,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'local_id': localId,
      'brand': brand,
      'model': model,
      'serial_number': serialNumber,
      'status': status,
      'health_score': healthScore,
    };
  }
}
