import "package:flutter/material.dart";

import "core/api_config.dart";
import "core/auth_redirect.dart";
import "core/routes.dart";
import "models/scan.dart";
import "core/theme.dart";
import "ui/screens/alerts_screen.dart";
import "ui/screens/analytics_screen.dart";
import "ui/screens/community_screen.dart";
import "ui/screens/contribute_screen.dart";
import "ui/screens/farms_screen.dart";
import "ui/screens/history_screen.dart";
import "ui/screens/nexo_shell_screen.dart";
import "ui/screens/register_treatment_screen.dart";
import "ui/screens/tech_scan_validation_screen.dart";
import "ui/screens/tech_validation_screen.dart";
import "ui/screens/login_screen.dart";
import "ui/screens/map_screen.dart";
import "ui/screens/map_screen_args.dart";
import "ui/screens/register_screen.dart";
import "ui/screens/result_screen.dart";
import "ui/screens/scan_screen.dart";
import "ui/screens/settings_screen.dart";
import "ui/screens/splash_screen.dart";

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await ApiConfig.load();
  runApp(const NexoAgroApp());
}

class NexoAgroApp extends StatelessWidget {
  const NexoAgroApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: "NEXO Agro",
      theme: appTheme(),
      navigatorKey: AuthRedirect.navigatorKey,
      initialRoute: Routes.splash,
      routes: {
        Routes.splash: (context) => const SplashScreen(),
        Routes.login: (context) => const LoginScreen(),
        Routes.register: (context) => const RegisterScreen(),
        Routes.home: (context) => const NexoShellScreen(),
        Routes.scan: (context) => const ScanScreen(),
        Routes.history: (context) => const HistoryScreen(),
        Routes.alerts: (context) => const AlertsScreen(),
        Routes.community: (context) => const CommunityScreen(),
        Routes.farms: (context) => const FarmsScreen(),
        Routes.techValidation: (context) => const TechValidationScreen(),
        Routes.techScanValidation: (context) => const TechScanValidationScreen(),
        Routes.analytics: (context) => const AnalyticsScreen(),
        Routes.settings: (context) => const SettingsScreen(),
      },
      onGenerateRoute: (settings) {
        if (settings.name == Routes.map) {
          final args = settings.arguments as MapScreenArgs?;
          return MaterialPageRoute(
            builder: (context) => MapScreen(
              initialZoneId: args?.zoneId,
              initialPlague: args?.plague,
            ),
          );
        }
        if (settings.name == Routes.result) {
          final scan = settings.arguments as Scan?;
          if (scan != null) {
            return MaterialPageRoute(builder: (context) => ResultScreen(scan: scan));
          }
        }
        if (settings.name == Routes.contribute) {
          final scan = settings.arguments as Scan?;
          if (scan != null) {
            return MaterialPageRoute(builder: (context) => ContributeScreen(scan: scan));
          }
        }
        if (settings.name == Routes.registerTreatment) {
          final scan = settings.arguments as Scan?;
          return MaterialPageRoute(builder: (context) => RegisterTreatmentScreen(scan: scan));
        }
        return null;
      },
    );
  }
}
