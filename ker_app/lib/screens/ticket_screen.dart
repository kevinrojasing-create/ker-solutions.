import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../services/api.dart';

class TicketScreen extends StatefulWidget {
  const TicketScreen({super.key});

  @override
  State<TicketScreen> createState() => _TicketScreenState();
}

class _TicketScreenState extends State<TicketScreen> {
  final _formKey = GlobalKey<FormState>();
  final _descriptionController = TextEditingController();
  final ApiService _api = ApiService();
  
  XFile? _image;
  bool _isSubmitting = false;

  Future<void> _pickImage() async {
    final ImagePicker picker = ImagePicker();
    
    // Show dialog to choose camera or gallery
    final source = await showDialog<ImageSource>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Seleccionar imagen'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: const Icon(Icons.camera_alt),
              title: const Text('Tomar foto'),
              onTap: () => Navigator.pop(context, ImageSource.camera),
            ),
            ListTile(
              leading: const Icon(Icons.photo_library),
              title: const Text('Elegir de galería'),
              onTap: () => Navigator.pop(context, ImageSource.gallery),
            ),
          ],
        ),
      ),
    );
    
    if (source == null) return;
    
    try {
      final XFile? image = await picker.pickImage(source: source);
      setState(() {
        _image = image;
      });
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e')),
        );
      }
    }
  }


  Future<void> _submit() async {
    if (_formKey.currentState!.validate()) {
      if (_image == null) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('⚠️ Por favor selecciona una imagen')),
        );
        return;
      }

      setState(() => _isSubmitting = true);
      
      try {
        // Step 1: Analyze image with AI
        String? imageBase64;
        final bytes = await _image!.readAsBytes();
        imageBase64 = base64Encode(bytes);
        
        final aiDiagnosis = await _api.analyzeImage(_image!);
        
        // Step 2: Show AI diagnosis to user
        if (mounted) {
          final confirmed = await showDialog<bool>(
            context: context,
            builder: (context) => AlertDialog(
              title: const Text('🤖 Diagnóstico IA'),
              content: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Diagnóstico:', style: TextStyle(fontWeight: FontWeight.bold)),
                  Text(aiDiagnosis['diagnosis'] ?? 'N/A'),
                  SizedBox(height: 12),
                  Text('Severidad:', style: TextStyle(fontWeight: FontWeight.bold)),
                  Text(aiDiagnosis['severity'] ?? 'N/A'),
                  SizedBox(height: 12),
                  Text('Acción Recomendada:', style: TextStyle(fontWeight: FontWeight.bold)),
                  Text(aiDiagnosis['recommended_action'] ?? 'N/A'),
                  SizedBox(height: 12),
                  Text('Confianza: ${((aiDiagnosis['confidence'] ?? 0) * 100).toStringAsFixed(0)}%'),
                ],
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(context, false),
                  child: const Text('Cancelar'),
                ),
                ElevatedButton(
                  onPressed: () => Navigator.pop(context, true),
                  child: const Text('Crear Ticket'),
                ),
              ],
            ),
          );
          
          if (confirmed != true) {
            setState(() => _isSubmitting = false);
            return;
          }
        }
        
        // Step 3: Create ticket with AI diagnosis
        await _api.createTicket(
          description: _descriptionController.text,
          priority: "Alta",
          imageBase64: imageBase64,
          aiDiagnosis: aiDiagnosis['diagnosis'],
        );
        
        if (mounted) {
           ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('✅ Ticket creado exitosamente')),
          );
          Navigator.pop(context);
        }
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('❌ Error: $e')),
          );
        }
      } finally {
        if (mounted) setState(() => _isSubmitting = false);
      }
    }
  }


  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Nuevo Ticket de Mantenimiento')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: Column(
            children: [
              Text(
                'Análisis IA & Triage',
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              const SizedBox(height: 16),
              GestureDetector(
                onTap: _pickImage,
                child: Container(
                  height: 200,
                  width: double.infinity,
                  decoration: BoxDecoration(
                    color: Colors.grey[200],
                    border: Border.all(color: Colors.grey),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: _image == null
                      ? const Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(Icons.camera_alt, size: 50, color: Colors.grey),
                            Text('Toca para tomar foto de la falla'),
                          ],
                        )
                      : const Center(child: Text('Imagen Seleccionada (Previsualización)')),
                ),
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _descriptionController,
                decoration: const InputDecoration(
                  labelText: 'Descripción del problema',
                  border: OutlineInputBorder(),
                ),
                maxLines: 3,
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Por favor ingrese una descripción';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 24),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: _isSubmitting ? null : _submit,
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    backgroundColor: Theme.of(context).colorScheme.primary,
                    foregroundColor: Colors.white,
                  ),
                  child: _isSubmitting 
                    ? const CircularProgressIndicator(color: Colors.white)
                    : const Text('ENVIAR PARA DIAGNÓSTICO'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
