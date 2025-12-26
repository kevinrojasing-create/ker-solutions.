import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'screens/dashboard_screen.dart';

void main() {
  runApp(const KerApp());
}

class KerApp extends StatelessWidget {
  const KerApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'KER Solutions',
      debugShowCheckedModeBanner: false,
      theme: _buildTheme(Brightness.light),
      // darkTheme: _buildTheme(Brightness.dark), // Optional
      home: const DashboardScreen(),
    );
  }

  ThemeData _buildTheme(Brightness brightness) {
    var baseTheme = ThemeData(
      useMaterial3: true,
      brightness: brightness,
      colorScheme: ColorScheme.fromSeed(
        seedColor: const Color(0xFF00695C), // Professional Teal
        brightness: brightness,
      ),
    );

    return baseTheme.copyWith(
      textTheme: GoogleFonts.outfitTextTheme(baseTheme.textTheme),
      appBarTheme: baseTheme.appBarTheme.copyWith(
        centerTitle: true,
        elevation: 0,
      ),
    );
  }
}
