import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:ker_solutions/config/app_config.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class ApiService {
  final _storage = const FlutterSecureStorage();
  
  Future<Map<String, String>> _getHeaders() async {
    String? token = await _storage.read(key: 'jwt_token');
    return {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      if (token != null) 'Authorization': 'Bearer $token',
    };
  }

  Future<dynamic> get(String endpoint) async {
    final headers = await _getHeaders();
    final url = Uri.parse('${AppConfig.baseUrl}$endpoint');
    
    print('GET request to: $url');
    
    try {
      final response = await http.get(url, headers: headers);
      return _handleResponse(response);
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  Future<dynamic> post(String endpoint, dynamic data) async {
    final headers = await _getHeaders();
    final url = Uri.parse('${AppConfig.baseUrl}$endpoint');
    
    print('POST request to: $url');
    print('Data: ${jsonEncode(data)}');
    
    try {
      final response = await http.post(
        url,
        headers: headers,
        body: jsonEncode(data),
      );
      return _handleResponse(response);
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  Future<dynamic> put(String endpoint, dynamic data) async {
    final headers = await _getHeaders();
    final url = Uri.parse('${AppConfig.baseUrl}$endpoint');
    
    try {
      final response = await http.put(
        url,
        headers: headers,
        body: jsonEncode(data),
      );
      return _handleResponse(response);
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  Future<dynamic> delete(String endpoint) async {
    final headers = await _getHeaders();
    final url = Uri.parse('${AppConfig.baseUrl}$endpoint');
    
    try {
      final response = await http.delete(url, headers: headers);
      if (response.statusCode == 204 || response.statusCode == 200) {
        return true;
      } else {
        return _handleResponse(response);
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  dynamic _handleResponse(http.Response response) {
    if (response.statusCode >= 200 && response.statusCode < 300) {
      if (response.body.isEmpty) return null;
      return jsonDecode(response.body);
    } else {
      String errorMessage = 'Error ${response.statusCode}';
      try {
        final body = jsonDecode(response.body);
        if (body is Map && body.containsKey('detail')) {
          errorMessage = body['detail'];
        }
      } catch (_) {}
      
      print('API Error: $errorMessage');
      throw Exception(errorMessage);
    }
  }
}
