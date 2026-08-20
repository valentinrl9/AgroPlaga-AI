import "package:flutter/material.dart";

import "../data/repositories/user_repository.dart";
import "routes.dart";
import "session.dart";

/// Guard de rutas privilegiadas (perito/admin). Verifica rol en servidor.
class RouteGuard extends StatefulWidget {
  const RouteGuard({
    super.key,
    required this.allowedRoles,
    required this.child,
  });

  final Set<String> allowedRoles;
  final Widget child;

  @override
  State<RouteGuard> createState() => _RouteGuardState();
}

class _RouteGuardState extends State<RouteGuard> {
  bool _loading = true;
  bool _allowed = false;

  @override
  void initState() {
    super.initState();
    _check();
  }

  Future<void> _check() async {
    try {
      final profile = await UserRepository().fetchProfile();
      await Session.saveUserInfo(
        role: profile.role,
        name: profile.name,
        hasFieldPremium: profile.hasFieldPremium,
        hasClimateModule: profile.hasClimateModule,
        hasSiexModule: profile.hasSiexModule,
        hasSiexEnterprise: profile.hasSiexEnterprise,
      );
      if (mounted) {
        setState(() {
          _allowed = widget.allowedRoles.contains(profile.role);
          _loading = false;
        });
      }
    } catch (_) {
      if (mounted) {
        setState(() {
          _allowed = false;
          _loading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }
    if (!_allowed) {
      return Scaffold(
        appBar: AppBar(title: const Text("Acceso restringido")),
        body: Center(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Text("No tienes permisos para acceder a esta sección."),
                const SizedBox(height: 16),
                FilledButton(
                  onPressed: () => Navigator.of(context).pushReplacementNamed(Routes.home),
                  child: const Text("Volver al inicio"),
                ),
              ],
            ),
          ),
        ),
      );
    }
    return widget.child;
  }
}
