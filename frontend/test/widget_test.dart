import "package:flutter_test/flutter_test.dart";

import "package:agro_plaga_ai/main.dart";

void main() {
  testWidgets("NexoAgroApp arranca", (WidgetTester tester) async {
    await tester.pumpWidget(const NexoAgroApp());
    expect(find.text("NEXO Agro"), findsNothing);
  });
}
