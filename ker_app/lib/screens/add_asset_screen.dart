import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../services/api.dart';

class AddAssetScreen extends StatefulWidget {
  const AddAssetScreen({super.key});

  @override
  State<AddAssetScreen> createState() => _AddAssetScreenState();
}

class _AddAssetScreenState extends State<AddAssetScreen> {
  final _formKey = GlobalKey<FormState>();
  final ApiService _api = ApiService();
  
  final _idController = TextEditingController();
  final _nameController = TextEditingController();
  final _categoryController = TextEditingController();
  final _usageHoursController = TextEditingController(text: '8.0');
  final _maintenanceIntervalController = TextEditingController(text: '180');
  
  DateTime _installDate = DateTime.now().subtract(const Duration(days: 365));
  DateTime _lastMaintenance = DateTime.now().subtract(const Duration(days: 30));
  
  bool _isLoading = false;

  Future<void> _selectDate(BuildContext context, bool isInstallDate) async {
    final DateTime? picked = await showDatePicker(
      context: context,
      initialDate: isInstallDate ? _installDate : _lastMaintenance,
      firstDate: DateTime(2000),
      lastDate: DateTime.now(),
    );
    if (picked != null) {
      setState(() {
        if (isInstallDate) {
          _installDate = picked;
        } else {
          _lastMaintenance = picked;
        }
      });
    }
  }

  Future<void> _submitAsset() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);

    try {
      await _api.createAsset(
        id: _idController.text.trim(),
        name: _nameController.text.trim(),
        category: _categoryController.text.trim(),
        installDate: _installDate,
        lastMaintenance: _lastMaintenance,
        usageHoursPerDay: double.parse(_usageHoursController.text),
        maintenanceIntervalDays: int.parse(_maintenanceIntervalController.text),
      );

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('✅ Activo creado exitosamente')),
        );
        Navigator.pop(context, true); // Return true to indicate success
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('❌ Error: $e')),
        );
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final dateFormat = DateFormat('dd/MM/yyyy');

    return Scaffold(
      appBar: AppBar(
        title: const Text('Registrar Nuevo Activo'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              TextFormField(
                controller: _idController,
                decoration: const InputDecoration(
                  labelText: 'ID del Activo',
                  hintText: 'Ej: A004',
                  border: OutlineInputBorder(),
                ),
                validator: (v) => v == null || v.isEmpty ? 'Requerido' : null,
              ),
              const SizedBox(height: 16),
              
              TextFormField(
                controller: _nameController,
                decoration: const InputDecoration(
                  labelText: 'Nombre del Activo',
                  hintText: 'Ej: Caldera - Gimnasio Principal',
                  border: OutlineInputBorder(),
                ),
                validator: (v) => v == null || v.isEmpty ? 'Requerido' : null,
              ),
              const SizedBox(height: 16),
              
              TextFormField(
                controller: _categoryController,
                decoration: const InputDecoration(
                  labelText: 'Categoría',
                  hintText: 'Ej: HVAC, Seguridad, Gas',
                  border: OutlineInputBorder(),
                ),
                validator: (v) => v == null || v.isEmpty ? 'Requerido' : null,
              ),
              const SizedBox(height: 16),
              
              ListTile(
                title: const Text('Fecha de Instalación'),
                subtitle: Text(dateFormat.format(_installDate)),
                trailing: const Icon(Icons.calendar_today),
                onTap: () => _selectDate(context, true),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                  side: BorderSide(color: Colors.grey.shade400),
                ),
              ),
              const SizedBox(height: 16),
              
              ListTile(
                title: const Text('Última Mantención'),
                subtitle: Text(dateFormat.format(_lastMaintenance)),
                trailing: const Icon(Icons.calendar_today),
                onTap: () => _selectDate(context, false),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                  side: BorderSide(color: Colors.grey.shade400),
                ),
              ),
              const SizedBox(height: 16),
              
              TextFormField(
                controller: _usageHoursController,
                decoration: const InputDecoration(
                  labelText: 'Horas de Uso Diario',
                  border: OutlineInputBorder(),
                ),
                keyboardType: TextInputType.number,
                validator: (v) {
                  if (v == null || v.isEmpty) return 'Requerido';
                  if (double.tryParse(v) == null) return 'Debe ser un número';
                  return null;
                },
              ),
              const SizedBox(height: 16),
              
              TextFormField(
                controller: _maintenanceIntervalController,
                decoration: const InputDecoration(
                  labelText: 'Intervalo de Mantención (días)',
                  border: OutlineInputBorder(),
                ),
                keyboardType: TextInputType.number,
                validator: (v) {
                  if (v == null || v.isEmpty) return 'Requerido';
                  if (int.tryParse(v) == null) return 'Debe ser un número entero';
                  return null;
                },
              ),
              const SizedBox(height: 24),
              
              ElevatedButton(
                onPressed: _isLoading ? null : _submitAsset,
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.all(16),
                ),
                child: _isLoading
                    ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Text('Crear Activo', style: TextStyle(fontSize: 18)),
              ),
            ],
          ),
        ),
      ),
    );
  }

  @override
  void dispose() {
    _idController.dispose();
    _nameController.dispose();
    _categoryController.dispose();
    _usageHoursController.dispose();
    _maintenanceIntervalController.dispose();
    super.dispose();
  }
}
