import 'package:ker_solutions/services/api_service.dart';
import 'package:ker_solutions/models/local.dart';

class LocalesService {
  final ApiService _api = ApiService();

  Future<List<Local>> getLocales() async {
    try {
      final response = await _api.get('/locales/');
      if (response == null) return [];
      
      final List<dynamic> data = response;
      return data.map((json) => Local.fromJson(json)).toList();
    } catch (e) {
      print('Error fetching locales: $e');
      rethrow;
    }
  }

  Future<Local> createLocal(String name, String address, String description) async {
    try {
      final response = await _api.post('/locales/', {
        'name': name,
        'address': address,
        'description': description,
      });
      return Local.fromJson(response);
    } catch (e) {
      print('Error creating local: $e');
      rethrow;
    }
  }

  Future<void> deleteLocal(int id) async {
    await _api.delete('/locales/$id');
  }
}
