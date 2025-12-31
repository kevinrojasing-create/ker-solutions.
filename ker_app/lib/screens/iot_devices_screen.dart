import 'dart:async';
import 'dart:math';
import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:ker_solutions/providers/auth_provider.dart';
import 'package:ker_solutions/widgets/energy_chart.dart';
import 'package:ker_solutions/screens/support_chat_screen.dart';

class IoTDevicesScreen extends StatefulWidget {
  const IoTDevicesScreen({super.key});

  @override
  State<IoTDevicesScreen> createState() => _IoTDevicesScreenState();
}

class _IoTDevicesScreenState extends State<IoTDevicesScreen> {
  // Simulation State
  Timer? _timer;
  double _currentPower = 4.2; // kW
  double _currentTemp = -18.5; // °C
  
  List<FlSpot> _energyHistory = [
    const FlSpot(0, 3.5),
    const FlSpot(1, 3.8),
    const FlSpot(2, 4.2),
    const FlSpot(3, 4.0),
    const FlSpot(4, 3.9),
    const FlSpot(5, 4.2),
  ];
  double _timeCounter = 5.0;

  @override
  void initState() {
    super.initState();
    _startSimulation();
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  void _startSimulation() {
    _timer = Timer.periodic(const Duration(seconds: 3), (timer) {
      setState(() {
        // Simulate random fluctuations
        final random = Random();
        
        // Power: 3.5 - 5.5 kW
        double powerChange = (random.nextDouble() - 0.5) * 0.5;
        _currentPower = (_currentPower + powerChange).clamp(3.5, 5.5);

        // Temp: -19.0 to -17.0 °C
        double tempChange = (random.nextDouble() - 0.5) * 0.2;
        _currentTemp = (_currentTemp + tempChange).clamp(-20.0, -15.0);

        // Update Chart
        _timeCounter += 1;
        if (_energyHistory.length > 10) {
          _energyHistory.removeAt(0); // Keep simulation sliding
        }
        
        // Re-map X to 0..10 for the chart window
        List<FlSpot> newHistory = [];
        for(int i = 0; i < _energyHistory.length; i++) {
           newHistory.add(FlSpot(i.toDouble(), _energyHistory[i].y));
        }
        newHistory.add(FlSpot(newHistory.length.toDouble(), _currentPower));
        _energyHistory = newHistory;
      });
    });
  }

  @override
  Widget build(BuildContext context) {
    final user = Provider.of<AuthProvider>(context).currentUser;
    final hasAccess = user?.hasIoTUsers ?? false;

    return Scaffold(
      appBar: AppBar(
        title: const Text('IoT Monitor 360'),
      ),
      body: hasAccess
          ? _buildIoTDashboard(context)
          : _buildAccessDenied(context),
    );
  }

  void _simulateCriticalFailure() {
    // 1. Force temperature spike
    setState(() {
      _currentTemp = -2.5; // CRITICAL! Should be -18
    });

    // 2. Show AI Alert Dialog
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        backgroundColor: Colors.red.shade50,
        title: const Row(
          children: [
            Icon(Icons.report_problem, color: Colors.red),
            SizedBox(width: 8),
            Text('CRITICAL ALERT', style: TextStyle(color: Colors.red, fontWeight: FontWeight.bold)),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              "Anomaly Detected in Cold Chain Sensor",
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
            ),
            const SizedBox(height: 8),
            const Text("Temperature spiked to -2.5°C (Threshold: -15°C)."),
            const SizedBox(height: 4),
            const Text("Potential Root Cause: Compressor Power Failure detected by POW Origin.", style: TextStyle(fontSize: 12)),
            const SizedBox(height: 16),
            const Divider(),
            const Text("AI Recommendation:", style: TextStyle(fontWeight: FontWeight.bold, color: Colors.indigo)),
            const Text("Initiate emergency protocol P-12."),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Dismiss'),
          ),
          ElevatedButton.icon(
            onPressed: () {
              Navigator.pop(context);
              _showGuidedSolution(context);
            },
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            icon: const Icon(Icons.health_and_safety),
            label: const Text('View Guided Solution'),
          ),
        ],
      ),
    );
  }

  void _showGuidedSolution(BuildContext context) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (context) => Container(
        height: MediaQuery.of(context).size.height * 0.8,
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text("Guided Solution Protocol", style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            Chip(
              avatar: const Icon(Icons.smart_toy, color: Colors.white, size: 16),
              label: const Text('AI Generated Diagnosis', style: TextStyle(color: Colors.white)),
              backgroundColor: Colors.indigo.shade400,
            ),
            const SizedBox(height: 24),
            _buildStep(1, "Verify power supply breaker for Unit A-12.", true),
            _buildStep(2, "Check physically if the door is sealed properly.", false),
            _buildStep(3, "Restart the control panel manually.", false),
            const Spacer(),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: () {
                   Navigator.pop(context); // Close bottom sheet
                   Navigator.push(
                     context,
                     MaterialPageRoute(builder: (context) => const SupportChatScreen()),
                   );
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.green,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                ),
                icon: const Icon(Icons.video_call),
                label: const Text('Connect with Remote Expert'),
              ),
            ),
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }

  Widget _buildStep(int number, String text, bool isChecked) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16.0),
      child: Row(
        children: [
          Container(
            width: 32,
            height: 32,
            decoration: BoxDecoration(
              color: isChecked ? Colors.green : Colors.grey[300],
              shape: BoxShape.circle,
            ),
            child: Center(child: Text(number.toString(), style: TextStyle(color: isChecked ? Colors.white : Colors.black, fontWeight: FontWeight.bold))),
          ),
          const SizedBox(width: 16),
          Expanded(child: Text(text, style: const TextStyle(fontSize: 16))),
          if (isChecked) const Icon(Icons.check_circle, color: Colors.green),
        ],
      ),
    );
  }

  Widget _buildAccessDenied(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.lock_outline, size: 80, color: Colors.grey),
            const SizedBox(height: 24),
            const Text(
              'Feature Locked',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            const Text(
              'Real-time IoT Monitoring is available only on the Monitor 360 Plan.',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 16, color: Colors.grey),
            ),
            const SizedBox(height: 32),
            ElevatedButton(
              onPressed: () {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Contact sales to upgrade!')),
                );
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.teal,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
              ),
              child: const Text('Upgrade Plan'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildIoTDashboard(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // SIMULATION CONTROLS
        Container(
          margin: const EdgeInsets.only(bottom: 24),
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.red.shade50,
            border: Border.all(color: Colors.red.shade200),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text("⚠️  DEMO CONTROLS", style: TextStyle(fontWeight: FontWeight.bold, color: Colors.red)),
              const SizedBox(height: 8),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: _simulateCriticalFailure,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.red,
                    foregroundColor: Colors.white,
                  ),
                  icon: const Icon(Icons.warning_amber_rounded),
                  label: const Text("TRIGGER CRITICAL FAILURE"),
                ),
              ),
            ],
          ),
        ),

        // Real-time Chart Section
        const Text(
          "Consumo Energético (Tiempo Real)",
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 16),
        EnergyChart(dataPoints: _energyHistory),
        const SizedBox(height: 24),
        
        const Text(
          "Dispositivos Conectados",
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 16),
        
        _buildDeviceCard(
          context,
          name: "Sensor Cadena Frío",
          model: "SNZB-02D",
          type: "Temperature",
          value: "${_currentTemp.toStringAsFixed(1)}°C",
          status: _currentTemp > -10 ? "CRITICAL" : "Online",
          lastUpdate: "Just now",
          isCritical: _currentTemp > -10,
        ),
        _buildDeviceCard(
          context,
          name: "Consumo General",
          model: "POW Origin",
          type: "Energy",
          value: "${_currentPower.toStringAsFixed(2)} kW",
          status: "Online",
          lastUpdate: "Just now",
        ),
        const SizedBox(height: 24),
        Card(
          color: Colors.blue.shade50,
          child: ListTile(
            leading: const Icon(Icons.add_circle, color: Colors.blue),
            title: const Text('Bind New Device'),
            subtitle: const Text('Zigbee Bridge Pro required'),
            onTap: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Scanning for Zigbee Bridge...')),
              );
            },
          ),
        )
      ],
    );
  }

  Widget _buildDeviceCard(
    BuildContext context, {
    required String name,
    required String model,
    required String type,
    required String value,
    required String status,
    required String lastUpdate,
    bool isCritical = false,
  }) {
    Color iconColor = type == 'Temperature' ? Colors.orange : Colors.blueAccent;
    IconData icon = type == 'Temperature' ? Icons.thermostat : Icons.bolt;
    Color statusColor = isCritical ? Colors.red.shade100 : Colors.green.shade100;
    Color statusTextColor = isCritical ? Colors.red.shade800 : Colors.green.shade800;

    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      elevation: isCritical ? 8 : 1,
      shadowColor: isCritical ? Colors.red : null,
      shape: isCritical ? RoundedRectangleBorder(side: const BorderSide(color: Colors.red, width: 2), borderRadius: BorderRadius.circular(12)) : null,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    CircleAvatar(
                      backgroundColor: iconColor.withOpacity(0.1),
                      child: Icon(icon, color: iconColor),
                    ),
                    const SizedBox(width: 12),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(name, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                        Text(model, style: const TextStyle(color: Colors.grey, fontSize: 12)),
                      ],
                    ),
                  ],
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: statusColor,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(status, style: TextStyle(color: statusTextColor, fontSize: 12, fontWeight: FontWeight.bold)),
                ),
              ],
            ),
            const Divider(height: 24),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('Current Reading', style: TextStyle(color: Colors.grey, fontSize: 12)),
                    Text(value, style: TextStyle(fontWeight: FontWeight.bold, fontSize: 24, color: isCritical ? Colors.red : Colors.black)),
                  ],
                ),
                Text(lastUpdate, style: const TextStyle(color: Colors.grey, fontSize: 12)),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
