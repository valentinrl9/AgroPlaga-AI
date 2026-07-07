import "package:flutter/material.dart";

import "../../core/routes.dart";
import "../../core/session.dart";
import "../../data/repositories/user_repository.dart";
import "../widgets/app_logo.dart";

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    super.initState();
    _bootstrap();
  }

  Future<void> _bootstrap() async {
    var goHome = false;

    if (await Session.restore()) {
      try {
        final profile = await UserRepository().fetchProfile();
        await Session.saveUserInfo(role: profile.role, name: profile.name);
        goHome = await Session.hasToken();
      } catch (_) {
        await Session.clear();
      }
    }

    if (!mounted) return;
    Navigator.pushReplacementNamed(context, goHome ? Routes.home : Routes.login);
  }

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            AppLogo(size: 96, borderRadius: 20),
            SizedBox(height: 16),
            Text(
              "AgroPlaga AI",
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Color(0xFF424242)),
            ),
            SizedBox(height: 8),
            Text(
              "Diagnóstico y red colaborativa",
              style: TextStyle(fontSize: 14, color: Color(0xFF757575)),
            ),
            SizedBox(height: 32),
            CircularProgressIndicator(color: Color(0xFF2E7D32)),
          ],
        ),
      ),
    );
  }
}
