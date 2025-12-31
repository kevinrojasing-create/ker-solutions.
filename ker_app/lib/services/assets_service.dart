import 'package:ker_solutions/services/api_service.dart';
import 'package:ker_solutions/models/asset.dart';

class AssetsService {
  final ApiService _api = ApiService();

  Future<List<Asset>> getAssets({int? localId}) async {
    try {
      final endpoint = localId != null 
          ? '/assets/?local_id=$localId' 
          : '/assets/';
          
      final response = await _api.get(endpoint);
      if (response == null) return [];
      
      final List<dynamic> data = response;
      return data.map((json) => Asset.fromJson(json)).toList();
    } catch (e) {
      print('Error fetching assets: $e');
      rethrow;
    }
  }

  Future<Asset> createAsset(String name, int localId, {String? brand, String? model, String? status}) async {
    try {
      final response = await _api.post('/assets/', {
        'name': name,
        'local_id': localId,
        'brand': brand,
        'model': model,
        'status': status ?? 'operational',
      });
      return Asset.fromJson(response);
    } catch (e) {
      print('Error creating asset: $e');
      rethrow;
    }
  }

  Future<void> deleteAsset(int id) async {
    await _api.delete('/assets/$id');
  }
}
