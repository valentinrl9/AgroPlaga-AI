import "package:flutter/material.dart";

import "../../core/nexo_colors.dart";
import "../../core/routes.dart";
import "../../core/session.dart";
import "../../data/repositories/user_repository.dart";
import "../widgets/app_logo.dart";
import "../widgets/nexo_wordmark.dart";

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
        await Session.saveUserInfo(
          role: profile.role,
          name: profile.name,
          hasFieldPremium: profile.hasFieldPremium,
          hasClimateModule: profile.hasClimateModule,
          hasSiexEnterprise: profile.hasSiexEnterprise,
        );
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
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [NexoColors.deepBlue, NexoColors.surfaceBase],
          ),
        ),
        child: const Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              AppLogo(size: 96, borderRadius: 20),
              SizedBox(height: 16),
              NexoWordmark(fontSize: 32, onDark: true),
              SizedBox(height: 8),
              Text(
                "Ecosistema de inteligencia agrícola",
                style: TextStyle(fontSize: 14, color: NexoColors.textSecondary),
              ),
              SizedBox(height: 32),
              CircularProgressIndicator(),
            ],
          ),
        ),
      ),
    );
  }
}
