import "package:flutter/material.dart";

import "nexo_colors.dart";

ThemeData appTheme() {
  const colorScheme = ColorScheme.dark(
    primary: NexoColors.bioGreen,
    onPrimary: NexoColors.pureWhite,
    secondary: NexoColors.techCyan,
    onSecondary: NexoColors.deepBlue,
    surface: NexoColors.surfaceCard,
    onSurface: NexoColors.textPrimary,
    surfaceContainerHighest: NexoColors.surfaceElevated,
    error: NexoColors.errorRed,
    onError: NexoColors.pureWhite,
    outline: NexoColors.borderSubtle,
  );

  return ThemeData(
    useMaterial3: true,
    brightness: Brightness.dark,
    colorScheme: colorScheme,
    fontFamily: "Roboto",
    scaffoldBackgroundColor: NexoColors.surfaceBase,
    appBarTheme: const AppBarTheme(
      backgroundColor: NexoColors.deepBlue,
      foregroundColor: NexoColors.pureWhite,
      elevation: 0,
      centerTitle: false,
      surfaceTintColor: Colors.transparent,
    ),
    cardTheme: CardThemeData(
      color: NexoColors.surfaceCard,
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: const BorderSide(color: NexoColors.borderSubtle),
      ),
      margin: const EdgeInsets.symmetric(vertical: 6),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: NexoColors.surfaceElevated,
      border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: const BorderSide(color: NexoColors.borderSubtle),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: const BorderSide(color: NexoColors.techCyan, width: 1.5),
      ),
      labelStyle: const TextStyle(color: NexoColors.textSecondary),
      hintStyle: const TextStyle(color: NexoColors.textSecondary),
    ),
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: NexoColors.bioGreen,
        foregroundColor: NexoColors.pureWhite,
        elevation: 0,
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
    ),
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        foregroundColor: NexoColors.textPrimary,
        side: const BorderSide(color: NexoColors.borderSubtle),
        backgroundColor: NexoColors.surfaceElevated,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        padding: const EdgeInsets.symmetric(vertical: 14),
      ),
    ),
    floatingActionButtonTheme: const FloatingActionButtonThemeData(
      backgroundColor: NexoColors.bioGreen,
      foregroundColor: NexoColors.pureWhite,
    ),
    chipTheme: ChipThemeData(
      backgroundColor: NexoColors.surfaceElevated,
      selectedColor: NexoColors.bioGreen.withValues(alpha: 0.2),
      labelStyle: const TextStyle(color: NexoColors.textPrimary, fontSize: 13),
      side: const BorderSide(color: NexoColors.borderSubtle),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
    ),
    tabBarTheme: const TabBarThemeData(
      labelColor: NexoColors.pureWhite,
      unselectedLabelColor: Color(0x99FFFFFF),
      indicatorColor: NexoColors.techCyan,
      dividerColor: NexoColors.borderSubtle,
    ),
    navigationBarTheme: NavigationBarThemeData(
      backgroundColor: NexoColors.deepBlue,
      indicatorColor: NexoColors.bioGreen.withValues(alpha: 0.22),
      surfaceTintColor: Colors.transparent,
      height: 68,
      labelTextStyle: const WidgetStatePropertyAll(
        TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: NexoColors.textSecondary),
      ),
      iconTheme: WidgetStateProperty.resolveWith((states) {
        if (states.contains(WidgetState.selected)) {
          return const IconThemeData(color: NexoColors.techCyan);
        }
        return const IconThemeData(color: NexoColors.textSecondary);
      }),
    ),
    snackBarTheme: SnackBarThemeData(
      backgroundColor: NexoColors.surfaceElevated,
      contentTextStyle: const TextStyle(color: NexoColors.textPrimary),
      behavior: SnackBarBehavior.floating,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: const BorderSide(color: NexoColors.borderAccent),
      ),
    ),
    progressIndicatorTheme: const ProgressIndicatorThemeData(
      color: NexoColors.techCyan,
    ),
    dividerTheme: const DividerThemeData(
      color: NexoColors.borderSubtle,
    ),
    listTileTheme: const ListTileThemeData(
      iconColor: NexoColors.techCyan,
      textColor: NexoColors.textPrimary,
    ),
    textTheme: const TextTheme(
      headlineLarge: TextStyle(
        fontSize: 32,
        fontWeight: FontWeight.bold,
        color: NexoColors.textPrimary,
        letterSpacing: -0.5,
      ),
      headlineMedium: TextStyle(
        fontSize: 24,
        fontWeight: FontWeight.w600,
        color: NexoColors.textPrimary,
      ),
      titleLarge: TextStyle(
        fontSize: 20,
        fontWeight: FontWeight.w600,
        color: NexoColors.textPrimary,
      ),
      bodyLarge: TextStyle(fontSize: 16, color: NexoColors.textPrimary, height: 1.5),
      bodyMedium: TextStyle(fontSize: 14, color: NexoColors.textPrimary, height: 1.5),
      bodySmall: TextStyle(fontSize: 12, color: NexoColors.textSecondary),
    ),
  );
}
