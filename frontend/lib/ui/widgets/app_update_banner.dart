import "package:flutter/material.dart";
import "package:url_launcher/url_launcher.dart";

import "../../core/app_update.dart";
import "../../core/nexo_colors.dart";

class AppUpdateBanner extends StatefulWidget {
  const AppUpdateBanner({super.key});

  @override
  State<AppUpdateBanner> createState() => _AppUpdateBannerState();
}

class _AppUpdateBannerState extends State<AppUpdateBanner> {
  AppUpdateOffer? _offer;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final offer = await AppUpdate.check();
    if (!mounted || offer == null) return;
    setState(() => _offer = offer);
  }

  Future<void> _open() async {
    final offer = _offer;
    if (offer == null) return;
    final uri = Uri.parse(offer.apkUrl);
    final opened = await launchUrl(uri, mode: LaunchMode.externalApplication);
    if (!opened && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Abre este enlace en el navegador: ${offer.apkUrl}")),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final offer = _offer;
    if (offer == null) return const SizedBox.shrink();
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 0),
      child: Material(
        color: NexoColors.warningAmber.withValues(alpha: 0.14),
        borderRadius: BorderRadius.circular(12),
        child: InkWell(
          onTap: _open,
          borderRadius: BorderRadius.circular(12),
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: NexoColors.warningAmber.withValues(alpha: 0.55)),
            ),
            child: Row(
              children: [
                const Icon(Icons.system_update_alt, color: NexoColors.warningAmber),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    "Hay una versión nueva (${offer.versionName}). Pulsa para actualizar.",
                    style: const TextStyle(fontSize: 13, height: 1.3),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
