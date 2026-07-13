import "dart:typed_data";

import "package:flutter/material.dart";

import "../../core/nexo_colors.dart";

class ScanImagePreview extends StatelessWidget {
  const ScanImagePreview({super.key, required this.bytes, this.height = 220});

  final Uint8List bytes;
  final double height;

  @override
  Widget build(BuildContext context) {
    if (bytes.isEmpty) {
      return _placeholder("Sin imagen");
    }
    return Image.memory(
      bytes,
      height: height,
      width: double.infinity,
      fit: BoxFit.cover,
      errorBuilder: (_, __, ___) => _placeholder("No se pudo mostrar la imagen"),
    );
  }

  Widget _placeholder(String message) {
    return Container(
      height: height,
      width: double.infinity,
      color: NexoColors.surfaceElevated,
      alignment: Alignment.center,
      child: Text(message, style: const TextStyle(color: NexoColors.textSecondary)),
    );
  }
}
