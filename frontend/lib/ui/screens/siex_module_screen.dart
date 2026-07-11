import "package:flutter/material.dart";

import "../../core/session.dart";
import "../widgets/nexo_lock_screen.dart";

class SiexModuleScreen extends StatefulWidget {
  const SiexModuleScreen({super.key});

  @override
  State<SiexModuleScreen> createState() => _SiexModuleScreenState();
}

class _SiexModuleScreenState extends State<SiexModuleScreen> {
  bool _unlocked = false;

  @override
  void initState() {
    super.initState();
    _loadAccess();
  }

  Future<void> _loadAccess() async {
    final unlocked = await Session.hasSiexEnterprise;
    if (mounted) setState(() => _unlocked = unlocked);
  }

  @override
  Widget build(BuildContext context) {
    if (!_unlocked) {
      return const Scaffold(
        body: NexoLockScreen(moduleName: "NEXO SIEX", isB2C: false),
      );
    }

    return Scaffold(
      appBar: AppBar(title: const Text("NEXO SIEX")),
      body: const Center(
        child: Text("Cuaderno de campo digital — próximamente"),
      ),
    );
  }
}
