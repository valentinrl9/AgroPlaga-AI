import "package:flutter/material.dart";

/// Design tokens NEXO Agro (NEXO_CONTEXT.md) — dark-first.
class NexoColors {
  NexoColors._();

  static const deepBlue = Color(0xFF0B192C);
  static const bioGreen = Color(0xFF00A86B);
  static const techCyan = Color(0xFF00D2C4);
  static const warningAmber = Color(0xFFFFB200);
  static const pureWhite = Color(0xFFFFFFFF);
  static const slateGray = Color(0xFFF4F6F9);
  static const darkText = Color(0xFF1E293B);
  static const lightText = Color(0xFF94A3B8);

  /// Superficies oscuras (UI principal).
  static const surfaceBase = Color(0xFF081422);
  static const surfaceCard = Color(0xFF12243A);
  static const surfaceElevated = Color(0xFF1A3048);
  static const borderSubtle = Color(0xFF2A4060);
  static const borderAccent = Color(0x3300D2C4);

  /// Texto sobre fondos oscuros.
  static const textPrimary = Color(0xFFF1F5F9);
  static const textSecondary = Color(0xFF94A3B8);

  /// Semánticos (Climate DPV, validación perito, severidad).
  static const errorRed = Color(0xFFEF4444);
  static const successGreen = Color(0xFF10B981);

  static const severityLow = bioGreen;
  static const severityModerate = warningAmber;
  static const severityHigh = errorRed;

  static Color bioGreenDisabled = bioGreen.withValues(alpha: 0.35);

  static const primaryGradient = LinearGradient(
    begin: Alignment.centerLeft,
    end: Alignment.centerRight,
    colors: [bioGreen, Color(0xFF00C49A)],
  );
}
