import "package:flutter/material.dart";

import "nexo_colors.dart";

ThemeData appTheme() {
  return ThemeData(
    useMaterial3: true,
    colorScheme: const ColorScheme.light(
      primary: NexoColors.bioGreen,
      onPrimary: NexoColors.pureWhite,
      secondary: NexoColors.techCyan,
      onSecondary: NexoColors.deepBlue,
      surface: NexoColors.slateGray,
      onSurface: NexoColors.darkText,
      error: Color(0xFFEF4444),
    ),
    scaffoldBackgroundColor: NexoColors.slateGray,
    appBarTheme: const AppBarTheme(
      backgroundColor: NexoColors.deepBlue,
      foregroundColor: NexoColors.pureWhite,
    ),
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: NexoColors.bioGreen,
        foregroundColor: NexoColors.pureWhite,
      ),
    ),
    navigationBarTheme: const NavigationBarThemeData(
      backgroundColor: NexoColors.pureWhite,
      indicatorColor: Color(0x332E7D32),
      labelTextStyle: WidgetStatePropertyAll(TextStyle(fontSize: 12, fontWeight: FontWeight.w600)),
    ),
    textTheme: const TextTheme(
      bodyLarge: TextStyle(color: NexoColors.darkText),
      bodyMedium: TextStyle(color: NexoColors.darkText),
    ),
  );
}
