import 'package:flutter/material.dart';
import 'package:ker_solutions/models/asset.dart';
import 'package:ker_solutions/models/local.dart';
import 'package:ker_solutions/services/assets_service.dart';
import 'package:ker_solutions/services/locales_service.dart';

class AssetsScreen extends StatefulWidget {
  final int? initialLocalId;

  const AssetsScreen({super.key, this.initialLocalId});

  @override
  State<AssetsScreen> createState() => _AssetsScreenState();
}

class _AssetsScreenState extends State<AssetsScreen> {
  final AssetsService _assetsService = AssetsService();
  final LocalesService _localesService = LocalesService();
  
  late Future<List<Asset>> _assetsFuture;
  List<Local> _availableLocales = [];
  int? _selectedLocalFilter;

  @override
  void initState() {
    super.initState();
    _selectedLocalFilter = widget.initialLocalId;
    _loadLocales();
    _refreshAssets();
  }

  Future<void> _loadLocales() async {
    try {
      final locales = await _localesService.getLocales();
      if (mounted) {
        setState(() {
          _availableLocales = locales;
        });
      }
    } catch (e) {
      print('Error loading locales for filter: $e');
    }
  }

  void _refreshAssets() {
    setState(() {
      _assetsFuture = _assetsService.getAssets(localId: _selectedLocalFilter);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Inventario de Activos'),
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(60),
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
            child: DropdownButtonFormField<int>(
              value: _selectedLocalFilter,
              decoration: const InputDecoration(
                labelText: 'Filtrar por Local',
                border: OutlineInputBorder(),
                contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 0),
                fillColor: Colors.white,
                filled: true,
              ),
              items: [
                const DropdownMenuItem<int>(
                  value: null,
                  child: Text('Todos los Locales'),
                ),
                ..._availableLocales.map((l) => DropdownMenuItem(
                  value: l.id,
                  child: Text(l.name),
                )),
              ],
              onChanged: (value) {
                setState(() {
                  _selectedLocalFilter = value;
                  _refreshAssets();
                });
              },
            ),
          ),
        ),
      ),
      body: FutureBuilder<List<Asset>>(
        future: _assetsFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          } else if (snapshot.hasError) {
            return Center(child: Text('Error: ${snapshot.error}'));
          } else if (!snapshot.hasData || snapshot.data!.isEmpty) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.inventory_2_outlined, size: 64, color: Colors.grey),
                  const SizedBox(height: 16),
                  const Text('No assets found.', style: TextStyle(color: Colors.grey, fontSize: 18)),
                  if (_availableLocales.isEmpty)
                    const Padding(
                      padding: EdgeInsets.all(16.0),
                      child: Text('Create a Local first to add assets!', style: TextStyle(color: Colors.orange)),
                    ),
                ],
              ),
            );
          }

          final assets = snapshot.data!;
          return ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: assets.length,
            itemBuilder: (context, index) {
              final asset = assets[index];
              final localName = _availableLocales
                  .firstWhere((l) => l.id == asset.localId, orElse: () => Local(id: 0, name: 'Unknown', address: '', ownerId: 0, isActive: false))
                  .name;

              return Card(
                elevation: 2,
                margin: const EdgeInsets.only(bottom: 12),
                child: Padding(
                  padding: const EdgeInsets.all(12.0),
                  child: Row(
                    children: [
                      _buildHealthIndicator(asset.healthScore),
                      const SizedBox(width: 16),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(asset.name, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                            Text('$localName | ${asset.brand ?? "Genérico"}', style: TextStyle(color: Colors.grey[600])),
                            const SizedBox(height: 4),
                            Row(
                              children: [
                                Icon(Icons.circle, size: 10, color: _getStatusColor(asset.status)),
                                const SizedBox(width: 4),
                                Text(asset.status.toUpperCase(), style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold)),
                              ],
                            ),
                          ],
                        ),
                      ),
                      const Icon(Icons.chevron_right, color: Colors.grey),
                    ],
                  ),
                ),
              );
            },
          );
        },
      ),
      floatingActionButton: Column(
        mainAxisAlignment: MainAxisAlignment.end,
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          FloatingActionButton.extended(
            heroTag: 'scan',
            onPressed: _simulateAIScan,
            backgroundColor: Colors.indigo,
            icon: const Icon(Icons.qr_code_scanner),
            label: const Text('AI Scan'),
          ),
          const SizedBox(height: 16),
          FloatingActionButton(
            heroTag: 'add',
            onPressed: _showCreateAssetDialog,
            backgroundColor: Colors.orange,
            child: const Icon(Icons.add),
          ),
        ],
      ),
    );
  }

  Widget _buildHealthIndicator(int score) {
    Color color;
    if (score >= 80) color = Colors.green;
    else if (score >= 50) color = Colors.orange;
    else color = Colors.red;

    return Column(
      children: [
        Stack(
          alignment: Alignment.center,
          children: [
            CircularProgressIndicator(
              value: score / 100,
              backgroundColor: Colors.grey[200],
              color: color,
            ),
            Text(
              '$score',
              style: TextStyle(fontWeight: FontWeight.bold, color: color, fontSize: 12),
            ),
          ],
        ),
        const SizedBox(height: 4),
        const Text('Health', style: TextStyle(fontSize: 10, color: Colors.grey))
      ],
    );
  }

  Future<void> _simulateAIScan() async {
     if (_availableLocales.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Create a Local first!')));
      return;
    }

    // 1. Show scanning simulation
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => const AlertDialog(
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            CircularProgressIndicator(),
            SizedBox(height: 16),
            Text("AI analyzing image..."),
            Text("Detecting equipment type...", style: TextStyle(fontSize: 12, color: Colors.grey)),
          ],
        ),
      ),
    );

    await Future.delayed(const Duration(seconds: 2));
    if (mounted) Navigator.pop(context);

    // 2. Show result form pre-filled
    final nameController = TextEditingController(text: "Samsung Refrigerator");
    final brandController = TextEditingController(text: "Samsung / RF28");
    int? selectedLocalId = _selectedLocalFilter ?? _availableLocales.first.id;

    if (!mounted) return;
    
    await showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setStateDialog) => AlertDialog(
          title: const Row(children: [Icon(Icons.auto_awesome, color: Colors.purple), SizedBox(width: 8), Text('AI Detected Asset')]),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                height: 100,
                width: double.infinity,
                color: Colors.grey[200],
                child: const Icon(Icons.image, size: 50, color: Colors.grey),
              ),
              const SizedBox(height: 16),
              TextField(controller: nameController, decoration: const InputDecoration(labelText: 'Asset Name')),
              DropdownButtonFormField<int>(
                value: selectedLocalId,
                items: _availableLocales.map((l) => DropdownMenuItem(value: l.id, child: Text(l.name))).toList(),
                onChanged: (val) => setStateDialog(() => selectedLocalId = val),
              ),
              TextField(controller: brandController, decoration: const InputDecoration(labelText: 'Brand / Model')),
              const SizedBox(height: 8),
              const Text('Confidence Score: 98%', style: TextStyle(color: Colors.green, fontSize: 12, fontStyle: FontStyle.italic)),
            ],
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(context), child: const Text('Discard')),
            ElevatedButton(
              onPressed: () async {
                 try {
                  await _assetsService.createAsset(
                    nameController.text,
                    selectedLocalId!,
                    brand: brandController.text,
                  );
                  if (mounted) {
                    Navigator.pop(context);
                    _refreshAssets();
                  }
                } catch (e) {
                   // Error
                }
              },
              child: const Text('Save to Inventory'),
            ),
          ],
        ),
      ),
    );
  }

  Color _getStatusColor(String status) {
    switch (status.toLowerCase()) {
      case 'operational': return Colors.green;
      case 'maintenance': return Colors.orange;
      case 'down': return Colors.red;
      default: return Colors.grey;
    }
  }

  Future<void> _showCreateAssetDialog() async {
    if (_availableLocales.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please create a Local first!')),
      );
      return;
    }

    final nameController = TextEditingController();
    final brandController = TextEditingController();
    int? selectedLocalId = _selectedLocalFilter ?? _availableLocales.first.id;

    await showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setStateDialog) => AlertDialog(
          title: const Text('Add New Asset'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: nameController,
                decoration: const InputDecoration(labelText: 'Asset Name', hintText: 'e.g. Fridge 01'),
              ),
              const SizedBox(height: 12),
              DropdownButtonFormField<int>(
                value: selectedLocalId,
                decoration: const InputDecoration(labelText: 'Location'),
                items: _availableLocales.map((l) => DropdownMenuItem(
                  value: l.id,
                  child: Text(l.name),
                )).toList(),
                onChanged: (val) => setStateDialog(() => selectedLocalId = val),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: brandController,
                decoration: const InputDecoration(labelText: 'Brand / Model'),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              onPressed: () async {
                try {
                  if (nameController.text.isEmpty || selectedLocalId == null) return;
                  
                  await _assetsService.createAsset(
                    nameController.text,
                    selectedLocalId!,
                    brand: brandController.text,
                  );
                  
                  if (mounted) {
                    Navigator.pop(context);
                    _refreshAssets();
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Asset created successfully')),
                    );
                  }
                } catch (e) {
                   // Error handling
                }
              },
              child: const Text('Create'),
            ),
          ],
        ),
      ),
    );
  }
}
