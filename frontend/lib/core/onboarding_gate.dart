import "routes.dart";
import "session.dart";
import "../data/repositories/farm_repository.dart";

class OnboardingGate {
  static Future<String> postAuthRoute() async {
    final role = await Session.role;
    if (role == "tech" || role == "admin") {
      return Routes.home;
    }

    try {
      final farms = await FarmRepository().fetchFarms();
      if (farms.isEmpty) {
        return Routes.onboarding;
      }
    } catch (_) {
      return Routes.home;
    }

    return Routes.home;
  }
}
