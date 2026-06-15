import "package:flutter/material.dart";

import "routes.dart";

void goHome(BuildContext context) {
  Navigator.of(context).pushNamedAndRemoveUntil(Routes.home, (route) => false);
}
