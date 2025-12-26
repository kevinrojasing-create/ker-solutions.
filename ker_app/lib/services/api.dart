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
    if (kIsWeb) return "http://127.0.0.1:8000";
    // IP Local detectada: 192.168.1.104
    // Usamos esta IP para que el celular físico pueda ver el backend
    return "http://192.168.1.104:8000"; 
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

  Future<void> submitTicket(String description, String priority) async {
    // Mock submission
    await Future.delayed(Duration(seconds: 1));
    return; 
  }
}
