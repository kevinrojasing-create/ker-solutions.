import 'package:flutter/material.dart';
import 'package:ker_solutions/models/local.dart';
import 'package:ker_solutions/services/locales_service.dart';

class LocalesScreen extends StatefulWidget {
  const LocalesScreen({super.key});

  @override
  State<LocalesScreen> createState() => _LocalesScreenState();
}

class _LocalesScreenState extends State<LocalesScreen> {
  final LocalesService _localesService = LocalesService();
  late Future<List<Local>> _localesFuture;

  @override
  void initState() {
    super.initState();
    _refreshLocales();
  }

  void _refreshLocales() {
    setState(() {
      _localesFuture = _localesService.getLocales();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Mis Locales'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _refreshLocales,
          ),
        ],
      ),
      body: FutureBuilder<List<Local>>(
        future: _localesFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          } else if (snapshot.hasError) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                   const Icon(Icons.error_outline, size: 48, color: Colors.red),
                   const SizedBox(height: 16),
                   Text('Error: ${snapshot.error}'),
                   const SizedBox(height: 16),
                   ElevatedButton(onPressed: _refreshLocales, child: const Text('Retry'))
                ],
              ),
            );
          } else if (!snapshot.hasData || snapshot.data!.isEmpty) {
             return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.store_mall_directory_outlined, size: 64, color: Colors.grey),
                  const SizedBox(height: 16),
                  const Text('No locales found.', style: TextStyle(fontSize: 18, color: Colors.grey)),
                  const SizedBox(height: 24),
                  ElevatedButton.icon(
                    onPressed: _showCreateLocalDialog,
                    icon: const Icon(Icons.add),
                    label: const Text('Create First Local'),
                  )
                ],
              ),
            );
          }

          final locales = snapshot.data!;
          return ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: locales.length,
            itemBuilder: (context, index) {
              final local = locales[index];
              return Card(
                margin: const EdgeInsets.only(bottom: 12),
                child: ListTile(
                  leading: CircleAvatar(
                    backgroundColor: Colors.blue.shade100,
                    child: Text(local.name[0].toUpperCase()),
                  ),
                  title: Text(local.name, style: const TextStyle(fontWeight: FontWeight.bold)),
                  subtitle: Text(local.address),
                  trailing: IconButton(
                    icon: const Icon(Icons.delete_outline, color: Colors.red),
                    onPressed: () => _confirmDelete(local),
                  ),
                  onTap: () {
                    // Navigate to details or assets
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text('Selected: ${local.name}')),
                    );
                  },
                ),
              );
            },
          );
        },
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _showCreateLocalDialog,
        child: const Icon(Icons.add),
      ),
    );
  }

  Future<void> _showCreateLocalDialog() async {
    final nameController = TextEditingController();
    final addressController = TextEditingController();
    final descController = TextEditingController();
    
    await showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('New Local'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: nameController,
              decoration: const InputDecoration(labelText: 'Name', hintText: 'e.g. Main Branch'),
            ),
            TextField(
              controller: addressController,
              decoration: const InputDecoration(labelText: 'Address', hintText: '123 Main St'),
            ),
            TextField(
              controller: descController,
              decoration: const InputDecoration(labelText: 'Description'),
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
                if (nameController.text.isEmpty) return;
                
                await _localesService.createLocal(
                  nameController.text,
                  addressController.text,
                  descController.text,
                );
                
                if (mounted) {
                  Navigator.pop(context);
                  _refreshLocales();
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Local created successfully')),
                  );
                }
              } catch (e) {
                if (mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('Error: $e')),
                  );
                }
              }
            },
            child: const Text('Create'),
          ),
        ],
      ),
    );
  }

  Future<void> _confirmDelete(Local local) async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Local?'),
        content: Text('Are you sure you want to delete "${local.name}"?'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Cancel')),
          TextButton(onPressed: () => Navigator.pop(context, true), child: const Text('Delete', style: TextStyle(color: Colors.red))),
        ],
      ),
    );

    if (confirm == true) {
      try {
        await _localesService.deleteLocal(local.id);
        _refreshLocales();
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Delete failed: $e')));
        }
      }
    }
  }
}
