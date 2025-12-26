import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter/foundation.dart';

// --- Domain Models ---

class Asset {
  final String id;
  final String name;
  final String category;
  final double usageHours;
  final DateTime lastMaintenance;

  Asset({
    required this.id,
    required this.name,
    required this.category,
    required this.usageHours,
    required this.lastMaintenance,
  });

  factory Asset.fromJson(Map<String, dynamic> json) {
    return Asset(
      id: json['id'],
      name: json['name'],
      category: json['category'],
      usageHours: json['usage_hours_per_day'] ?? 0.0,
      lastMaintenance: DateTime.parse(json['last_maintenance']),
    );
  }
}

class AssetHealth {
  final String assetId;
  final double healthScore;
  final double failureProb;
  final String status;
  final String colorCode;

  AssetHealth({
    required this.assetId,
    required this.healthScore,
    required this.failureProb,
    required this.status,
    required this.colorCode,
  });

  factory AssetHealth.fromJson(Map<String, dynamic> json) {
    return AssetHealth(
      assetId: json['asset_id'],
      healthScore: json['health_score'],
      failureProb: json['failure_probability'],
      status: json['status'],
      colorCode: json['color_code'],
    );
  }
}

class DashboardStatus {
  final String overallColor;
  final String message;
  final List<AssetHealth> details;

  DashboardStatus({required this.overallColor, required this.message, required this.details});

  factory DashboardStatus.fromJson(Map<String, dynamic> json) {
    var list = json['details'] as List;
    List<AssetHealth> healthList = list.map((i) => AssetHealth.fromJson(i)).toList();
    return DashboardStatus(
      overallColor: json['overall_color'],
      message: json['message'],
      details: healthList,
    );
  }
}

// --- Service Layer ---

class ApiService {
  // Use 10.0.2.2 for Android Emulator to access localhost
  // Use localhost for Web
  static String get baseUrl {
    // ☁️ URL de Producción (Render)
    return "https://ker-solutions.onrender.com"; 
  }

  Future<List<Asset>> getAssets() async {
    final response = await http.get(Uri.parse('$baseUrl/assets'));
    if (response.statusCode == 200) {
      List jsonResponse = json.decode(utf8.decode(response.bodyBytes));
      return jsonResponse.map((item) => Asset.fromJson(item)).toList();
    } else {
      throw Exception('Failed to load assets');
    }
  }

  Future<DashboardStatus> getDashboardStatus() async {
    final response = await http.get(Uri.parse('$baseUrl/dashboard/status'));
    if (response.statusCode == 200) {
      return DashboardStatus.fromJson(json.decode(utf8.decode(response.bodyBytes)));
    } else {
      throw Exception('Failed to load dashboard status');
    }
  }

  Future<void> createAsset({
    required String id,
    required String name,
    required String category,
    required DateTime installDate,
    required DateTime lastMaintenance,
    required double usageHoursPerDay,
    required int maintenanceIntervalDays,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/assets'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({
        'id': id,
        'name': name,
        'category': category,
        'install_date': installDate.toIso8601String(),
        'last_maintenance': lastMaintenance.toIso8601String(),
        'usage_hours_per_day': usageHoursPerDay,
        'maintenance_interval_days': maintenanceIntervalDays,
      }),
    );
    
    if (response.statusCode != 201) {
      final error = json.decode(utf8.decode(response.bodyBytes));
      throw Exception(error['detail'] ?? 'Failed to create asset');
    }
  }

  Future<void> createTicket({
    required String description,
    required String priority,
    String? imageBase64,
    String? assetId,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/tickets'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({
        'description': description,
        'priority': priority,
        'image_base64': imageBase64,
        'asset_id': assetId,
      }),
    );
    
    if (response.statusCode != 201) {
      final error = json.decode(utf8.decode(response.bodyBytes));
      throw Exception(error['detail'] ?? 'Failed to create ticket');
    }
  }
}

