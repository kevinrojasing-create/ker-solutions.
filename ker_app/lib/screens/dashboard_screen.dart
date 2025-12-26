import 'package:flutter/material.dart';
import '../services/api.dart';
import 'ticket_screen.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  final ApiService _api = ApiService();
  late Future<DashboardStatus> _statusFuture;

  @override
  void initState() {
    super.initState();
    _statusFuture = _api.getDashboardStatus();
  }

  Color _getColor(String code) {
    switch (code) {
      case 'red': return Colors.red;
      case 'yellow': return Colors.amber;
      case 'green': return Colors.green;
      default: return Colors.grey;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('KER Solutions Dashboard')),
      body: FutureBuilder<DashboardStatus>(
        future: _statusFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          } else if (snapshot.hasError) {
            return Center(child: Text('Error: ${snapshot.error}'));
          } else if (!snapshot.hasData) {
            return const Center(child: Text('No Data'));
          }

          final status = snapshot.data!;
          final mainColor = _getColor(status.overallColor);

          return SingleChildScrollView(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Traffic Light Hero Section
                Container(
                  padding: const EdgeInsets.all(24),
                  decoration: BoxDecoration(
                    color: mainColor.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: mainColor, width: 2),
                  ),
                  child: Column(
                    children: [
                      Icon(Icons.health_and_safety, size: 64, color: mainColor),
                      const SizedBox(height: 16),
                      Text(
                        status.message,
                        style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                          color: mainColor,
                          fontWeight: FontWeight.bold,
                        ),
                        textAlign: TextAlign.center,
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 24),
                
                Text('Desglose de Salud de Activos', style: Theme.of(context).textTheme.titleLarge),
                const SizedBox(height: 8),
                
                ...status.details.map((asset) => Card(
                  elevation: 2,
                  margin: const EdgeInsets.only(bottom: 8),
                  child: ListTile(
                    leading: CircleAvatar(
                      backgroundColor: _getColor(asset.colorCode),
                      child: Icon(Icons.build, color: Colors.white, size: 16),
                    ),
                    title: Text('ID Activo: ${asset.assetId}'),
                    subtitle: Text('Estado: ${asset.status} | Salud: ${asset.healthScore}%'),
                    trailing: Text('${asset.failureProb}% Riesgo'),
                  ),
                )),

                const SizedBox(height: 24),
                ElevatedButton.icon(
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(builder: (context) => const TicketScreen()),
                    );
                  },
                  icon: const Icon(Icons.add_a_photo),
                  label: const Text('Reportar Problema / Triage'),
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.all(16),
                    textStyle: const TextStyle(fontSize: 18),
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}
