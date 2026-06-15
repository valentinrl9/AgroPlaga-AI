import "package:flutter/material.dart";

ThemeData appTheme() {
  const primaryGreen = Color(0xFF2E7D32);

  return ThemeData(
    useMaterial3: true,
    colorScheme: const ColorScheme.light(
      primary: primaryGreen,
      onPrimary: Colors.white,
      secondary: Color(0xFF1565C0),
      onSecondary: Colors.white,
      error: Color(0xFFC62828),
      onSurface: Color(0xFF424242),
    ),
    scaffoldBackgroundColor: const Color(0xFFE8F5E9),
    appBarTheme: const AppBarTheme(
      backgroundColor: primaryGreen,
      foregroundColor: Colors.white,
    ),
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: primaryGreen,
        foregroundColor: Colors.white,
      ),
    ),
    textTheme: const TextTheme(
      bodyLarge: TextStyle(color: Color(0xFF424242)),
      bodyMedium: TextStyle(color: Color(0xFF424242)),
    ),
  );
}
