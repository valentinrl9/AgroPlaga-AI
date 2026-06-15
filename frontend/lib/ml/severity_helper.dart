int severityFromConfidence(String plague, double confidence) {
  if (plague == "sana") return 1;
  if (confidence >= 0.88) return 3;
  if (confidence >= 0.72) return 2;
  return 1;
}
