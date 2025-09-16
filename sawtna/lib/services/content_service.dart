
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';
import 'package:shared_preferences/shared_preferences.dart';
import 'auth_service.dart';

class ContentService {
  static const String baseUrl = 'http://127.0.0.1:8000';

  // Classify text content
  static Future<Map<String, dynamic>> classifyText(String text) async {
    try {
      final headers = await AuthService.getAuthHeaders();
      
      final response = await http.post(
        Uri.parse('$baseUrl/content/classify-text'),
        headers: headers,
        body: json.encode({
          'text': text,
        }),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return {
          'success': true,
          'isAppropriate': data['isAppropriate'] ?? false,
          'confidence': data['confidence'] ?? 0.0,
          'message': data['message'] ?? 'Text classification successful'
        };
      } else {
        final errorData = json.decode(response.body);
        return {
          'success': false,
          'message': errorData['detail'] ?? 'Failed to classify text',
          'isAppropriate': false
        };
      }
    } catch (e) {
      return {
        'success': false,
        'message': 'Connection error: $e',
        'isAppropriate': false
      };
    }
  }

  // Classify image content from file path (for mobile)
  static Future<Map<String, dynamic>> classifyImageFromPath(String imagePath) async {
    try {
      final token = await AuthService.getToken();
      if (token == null) {
        return {
          'success': false,
          'message': 'Not authenticated',
          'isAppropriate': false
        };
      }

      var request = http.MultipartRequest(
        'POST',
        Uri.parse('$baseUrl/content/classify-image')
      );
      
      request.headers['Authorization'] = 'Bearer $token';
      request.files.add(await http.MultipartFile.fromPath('file', imagePath));

      var response = await request.send();
      final responseBody = await response.stream.bytesToString();
      final data = json.decode(responseBody);

      if (response.statusCode == 200) {
        return {
          'success': true,
          'isAppropriate': data['isAppropriate'] ?? false,
          'confidence': data['confidence'] ?? 0.0,
          'message': data['message'] ?? 'Image classification successful'
        };
      } else {
        return {
          'success': false,
          'message': data['detail'] ?? 'Failed to classify image',
          'isAppropriate': false
        };
      }
    } catch (e) {
      return {
        'success': false,
        'message': 'Connection error: $e',
        'isAppropriate': false
      };
    }
  }

  // Classify image content from bytes (for web)
  static Future<Map<String, dynamic>> classifyImageFromBytes(Uint8List imageBytes) async {
    try {
      final token = await AuthService.getToken();
      if (token == null) {
        return {
          'success': false,
          'message': 'Not authenticated',
          'isAppropriate': false
        };
      }

      var request = http.MultipartRequest(
        'POST',
        Uri.parse('$baseUrl/content/classify-image')
      );
      
      request.headers['Authorization'] = 'Bearer $token';
      
      // Create a multipart file from bytes
      request.files.add(http.MultipartFile.fromBytes(
        'file',
        imageBytes,
        filename: 'image.jpg',
      ));

      var response = await request.send();
      final responseBody = await response.stream.bytesToString();
      final data = json.decode(responseBody);

      if (response.statusCode == 200) {
        return {
          'success': true,
          'isAppropriate': data['isAppropriate'] ?? false,
          'confidence': data['confidence'] ?? 0.0,
          'message': data['message'] ?? 'Image classification successful'
        };
      } else {
        return {
          'success': false,
          'message': data['detail'] ?? 'Failed to classify image',
          'isAppropriate': false
        };
      }
    } catch (e) {
      return {
        'success': false,
        'message': 'Connection error: $e',
        'isAppropriate': false
      };
    }
  }

  // Generate image from text prompt
  static Future<Map<String, dynamic>> generateImage(String prompt) async {
    try {
      final headers = await AuthService.getAuthHeaders();
      
      final response = await http.post(
        Uri.parse('$baseUrl/content/generate-image'),
        headers: headers,
        body: json.encode({
          'prompt': prompt,
        }),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return {
          'success': true,
          'prompt': data['prompt'],
          'filename': data['filename'],
          'image_data': data['image_data'],
          'message': 'Image generated successfully'
        };
      } else {
        final errorData = json.decode(response.body);
        return {
          'success': false,
          'message': errorData['detail'] ?? 'Failed to generate image',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'message': 'Connection error: $e',
      };
    }
  }

  // Generate image and return as base64
  static Future<Map<String, dynamic>> generateImageBase64(String prompt) async {
    try {
      final headers = await AuthService.getAuthHeaders();
      
      final response = await http.post(
        Uri.parse('$baseUrl/content/generate-image-base64'),
        headers: headers,
        body: json.encode({
          'prompt': prompt,
        }),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return {
          'success': true,
          'prompt': data['prompt'],
          'filename': data['filename'],
          'image_data': data['image_data'],
          'message': 'Image generated successfully'
        };
      } else {
        final errorData = json.decode(response.body);
        return {
          'success': false,
          'message': errorData['detail'] ?? 'Failed to generate image',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'message': 'Connection error: $e',
      };
    }
  }

  // Get user's generated content
  static Future<Map<String, dynamic>> getUserContent({int skip = 0, int limit = 20}) async {
    try {
      final headers = await AuthService.getAuthHeaders();
      
      final response = await http.get(
        Uri.parse('$baseUrl/content/user-content?skip=$skip&limit=$limit'),
        headers: headers,
      );

      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body);
        return {
          'success': true,
          'content': data,
        };
      } else {
        return {
          'success': false,
          'message': 'Failed to fetch user content',
          'content': []
        };
      }
    } catch (e) {
      return {
        'success': false,
        'message': 'Connection error: $e',
        'content': []
      };
    }
  }

  // Save content to user's history
  static Future<Map<String, dynamic>> saveContent({
    required String contentType,
    String? title,
    String? text,
    String? imagePath,
    Map<String, dynamic>? metadata,
  }) async {
    try {
      final headers = await AuthService.getAuthHeaders();
      
      final response = await http.post(
        Uri.parse('$baseUrl/content/'),
        headers: headers,
        body: json.encode({
          'content_type': contentType,
          'title': title,
          'text': text,
          'image_path': imagePath,
          'content_metadata': metadata,
        }),
      );

      if (response.statusCode == 200) {
        return {'success': true, 'message': 'Content saved successfully'};
      } else {
        return {'success': false, 'message': 'Failed to save content'};
      }
    } catch (e) {
      return {'success': false, 'message': 'Connection error: $e'};
    }
  }
}