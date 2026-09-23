import 'dart:convert';
import 'package:http/http.dart' as http;

class TrafficApi {
  static const String baseUrl = "http://127.0.0.1:8000";

  // Converts every nested JSON map into Map<String, dynamic>
  static dynamic convertJson(dynamic value) {
    if (value is Map) {
      return Map<String, dynamic>.from(
        value.map(
          (key, val) => MapEntry(
            key.toString(),
            convertJson(val),
          ),
        ),
      );
    }

    if (value is List) {
      return value.map(convertJson).toList();
    }

    return value;
  }

  static Future<Map<String, dynamic>> getTrafficStatus() async {
    final response = await http
        .get(
          Uri.parse("$baseUrl/traffic-status"),
        )
        .timeout(
          const Duration(seconds: 5),
        );

    if (response.statusCode == 200) {
      final decoded = jsonDecode(response.body);

      return convertJson(decoded) as Map<String, dynamic>;
    }

    throw Exception(
      "Traffic API returned ${response.statusCode}",
    );
  }

  static Future<Map<String, dynamic>> getSystemStatus() async {
    final response = await http
        .get(
          Uri.parse("$baseUrl/system-status"),
        )
        .timeout(
          const Duration(seconds: 5),
        );

    if (response.statusCode == 200) {
      final decoded = jsonDecode(response.body);

      return convertJson(decoded) as Map<String, dynamic>;
    }

    throw Exception(
      "System status API error",
    );
  }
  static Future<Map<String, dynamic>> getCameraStatus() async {
  final response = await http
      .get(
        Uri.parse("$baseUrl/camera-status"),
      )
      .timeout(
        const Duration(seconds: 5),
      );

  if (response.statusCode == 200) {
    final decoded = jsonDecode(response.body);

    return convertJson(decoded) as Map<String, dynamic>;
  }

  throw Exception(
    "Camera API returned ${response.statusCode}",
  );
}
}