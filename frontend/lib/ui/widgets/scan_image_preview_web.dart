import "dart:html" as html;
import "dart:typed_data";
import "dart:ui_web" as ui_web;

import "package:flutter/material.dart";

import "../../core/nexo_colors.dart";

class ScanImagePreview extends StatefulWidget {
  const ScanImagePreview({super.key, required this.bytes, this.height = 220});

  final Uint8List bytes;
  final double height;

  @override
  State<ScanImagePreview> createState() => _ScanImagePreviewState();
}

class _ScanImagePreviewState extends State<ScanImagePreview> {
  String? _viewType;
  bool _failed = false;

  @override
  void initState() {
    super.initState();
    _register();
  }

  @override
  void didUpdateWidget(covariant ScanImagePreview oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.bytes != widget.bytes) {
      _register();
    }
  }

  void _register() {
    if (widget.bytes.isEmpty) {
      setState(() {
        _viewType = null;
        _failed = false;
      });
      return;
    }

    final viewType = "scan-img-${widget.bytes.hashCode}";
    ui_web.platformViewRegistry.registerViewFactory(viewType, (int _) {
      final blob = html.Blob([widget.bytes]);
      final url = html.Url.createObjectUrlFromBlob(blob);
      final img = html.ImageElement()
        ..src = url
        ..style.width = "100%"
        ..style.height = "100%"
        ..style.objectFit = "cover";
      img.onError.listen((_) {
        if (mounted) setState(() => _failed = true);
      });
      return img;
    });
    setState(() {
      _viewType = viewType;
      _failed = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    if (widget.bytes.isEmpty) {
      return _placeholder("Sin imagen");
    }
    if (_failed || _viewType == null) {
      return _placeholder("No se pudo mostrar la imagen");
    }
    return SizedBox(
      height: widget.height,
      width: double.infinity,
      child: HtmlElementView(viewType: _viewType!),
    );
  }

  Widget _placeholder(String message) {
    return Container(
      height: widget.height,
      width: double.infinity,
      color: NexoColors.surfaceElevated,
      alignment: Alignment.center,
      child: Text(message, style: const TextStyle(color: NexoColors.textSecondary)),
    );
  }
}
