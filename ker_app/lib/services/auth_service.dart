import 'package:ker_solutions/services/api_service.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:ker_solutions/models/user.dart';
import 'dart:convert';

class AuthService {
  final ApiService _api = ApiService();
  final _storage = const FlutterSecureStorage();

  Future<User?> login(String email, String password) async {
    try {
      final response = await _api.post('/auth/login', {
        'email': email,
        'password': password,
      });

      if (response != null && response['access_token'] != null) {
        await _storage.write(key: 'jwt_token', value: response['access_token']);
        
        if (response['user'] != null) {
           final user = User.fromJson(response['user']);
           // Optionally store user data securely or just return it
           await _storage.write(key: 'user_data', value: jsonEncode(user.toJson()));
           return user;
        }
      }
      return null;
    } catch (e) {
      print('Login error: $e');
      rethrow;
    }
  }

  Future<void> register(String fullName, String email, String password, String companyName, String plan) async {
    await _api.post('/auth/register', {
      'full_name': fullName,
      'email': email,
      'password': password,
      'company_name': companyName,
      'role': 'owner',
      'plan': plan,
    });
  }

  Future<void> logout() async {
    await _storage.delete(key: 'jwt_token');
    await _storage.delete(key: 'user_data');
  }

  Future<User?> getCurrentUser() async {
    final userData = await _storage.read(key: 'user_data');
    if (userData != null) {
      try {
        return User.fromJson(jsonDecode(userData));
      } catch (e) {
        return null;
      }
    }
    return null;
  }
}
