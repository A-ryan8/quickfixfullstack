import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;

class ApiService {
  static const String _geminiApiKey = 'AIzaSyCb74HkJN1_r62gpWSf0PGRQm_bErvH_zE';
  // Configurable model name; can be overridden via --dart-define=GEMINI_MODEL=gemini-1.5-flash
  static const String _geminiModel = String.fromEnvironment('GEMINI_MODEL', defaultValue: 'gemini-2.0-flash');
  static const String _geminiApiUrl = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent';
  

  /// Analyzes an image using Gemini API and returns both title and description
  /// Returns null if the API call fails or if no content is generated
  static Future<Map<String, String>?> analyzeImageWithGemini({
    required File imageFile,
    String? locationContext,
  }) async {
    try {
      // Check if API key is set
      if (_geminiApiKey.isEmpty) {
        throw Exception('Gemini API key not configured');
      }

      // Read and encode image
      final imageBytes = await imageFile.readAsBytes();
      final base64Image = base64Encode(imageBytes);
      
      // Determine MIME type
      final mimeType = imageFile.path.toLowerCase().endsWith('.png') ? 'image/png' : 'image/jpeg';
      
      // Build location context
      final locationText = locationContext ?? 'unknown location';
      
      // Prepare request body for Gemini API
      final requestBody = {
        'contents': [
          {
            'parts': [
              {
                'text': 'You are a highly perceptive civic issue analyst and a professional report writer. Your task is to examine the user-provided image and generate both a title and description.\n\n'
                    'IMPORTANT: Return ONLY a valid JSON object with exactly this structure (no markdown, no code blocks, no extra text):\n'
                    '{"title": "A short 3-5 word summary of the main issue", "description": "A detailed paragraph describing the problem"}\n\n'
                    'For the title: Use 3-5 words that clearly identify the main issue (e.g., "Road Pothole Issue", "Broken Street Light", "Garbage Overflow Problem").\n\n'
                    'For the description: Write a single, detailed, and comprehensive paragraph that MUST analyze the situation, not just identify objects. In your analysis, you must seamlessly integrate the following points:\n\n'
                    '1. **Detailed Observation:** What is the issue? Describe its physical characteristics in detail (e.g., the approximate size and depth of a pothole, the extent of garbage overflow).\n'
                    '2. **Contextual Analysis:** Where is the issue located? Describe the immediate surroundings visible in the image (e.g., "on a busy residential street," "in a public park near a playground," "obstructing a sidewalk").\n'
                    '3. **Problem & Impact Analysis:** Explain precisely *why* this is a problem. What is the impact? (e.g., "This poses a significant safety hazard to cyclists and could cause vehicle damage," "This presents a public health risk due to pests and odor," "This illegally obstructs pedestrian access.").\n\n'
                    'Location context for this image: ' + locationText + '\n\n'
                    'CRITICAL: Your response must be ONLY the JSON object, nothing else. No explanations, no markdown formatting, no code blocks.'
              },
              {
                'inline_data': {
                  'mime_type': mimeType,
                  'data': base64Image,
                }
              }
            ]
          }
        ],
        'generationConfig': {
          'temperature': 0.3,
          'maxOutputTokens': 300,
        }
      };

      // Make API call to Gemini with robust fallbacks across endpoints and model aliases
      Future<http.Response> _callModelV1(String model) {
        final url = 'https://generativelanguage.googleapis.com/v1/models/' + model + ':generateContent?key=' + _geminiApiKey;
        print('Gemini call v1 model=' + model);
        return http.post(
          Uri.parse(url),
          headers: { 'Content-Type': 'application/json' },
          body: jsonEncode(requestBody),
        );
      }

      Future<http.Response> _callModelV1Beta(String model) {
        final url = 'https://generativelanguage.googleapis.com/v1beta/models/' + model + ':generateContent?key=' + _geminiApiKey;
        print('Gemini call v1beta model=' + model);
        return http.post(
          Uri.parse(url),
          headers: { 'Content-Type': 'application/json' },
          body: jsonEncode(requestBody),
        );
      }

      // Try preferred model on v1
      http.Response response = await _callModelV1(_geminiModel);
      if (response.statusCode == 404 && response.body.contains('NOT_FOUND')) {
        // Try stable alias on v1
        response = await _callModelV1('gemini-1.5-flash');
      }
      if (response.statusCode == 404 && response.body.contains('NOT_FOUND')) {
        // Try v1beta with stable alias
        response = await _callModelV1Beta('gemini-1.5-flash');
      }

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        
        // Extract the generated text from Gemini response
        if (data['candidates'] != null && (data['candidates'] as List).isNotEmpty) {
          final candidate = (data['candidates'] as List).first;
          if (candidate['content'] != null && candidate['content']['parts'] != null) {
            final parts = candidate['content']['parts'] as List;
            // Collect all text parts (Gemini may split content across multiple parts)
            final buffer = StringBuffer();
            for (final p in parts) {
              final partMap = p as Map<String, dynamic>;
              if (partMap['text'] != null) {
                buffer.write(partMap['text']);
              }
            }
            final responseText = buffer.toString().trim();
            if (responseText.isNotEmpty) {
              // Debug: Print the raw response from Gemini
              print('Raw Gemini Response: ' + responseText);

              // Try direct JSON parse
              try {
                final jsonResponse = jsonDecode(responseText) as Map<String, dynamic>;
                print('Parsed JSON: ' + jsonResponse.toString());
                return {
                  'title': jsonResponse['title'] as String? ?? 'Municipal Issue',
                  'description': jsonResponse['description'] as String? ?? responseText,
                };
              } catch (_) {}

              // Try to strip code fences and parse
              try {
                String cleanText = responseText;
                if (cleanText.startsWith('```json')) {
                  cleanText = cleanText.substring(7);
                } else if (cleanText.startsWith('```')) {
                  cleanText = cleanText.substring(3);
                }
                if (cleanText.endsWith('```')) {
                  cleanText = cleanText.substring(0, cleanText.length - 3);
                }
                cleanText = cleanText.trim();
                final jsonResponse = jsonDecode(cleanText) as Map<String, dynamic>;
                return {
                  'title': jsonResponse['title'] as String? ?? 'Municipal Issue',
                  'description': jsonResponse['description'] as String? ?? responseText,
                };
              } catch (_) {}

              // Fallback: try to extract the first JSON object using a simple brace match
              try {
                final start = responseText.indexOf('{');
                final end = responseText.lastIndexOf('}');
                if (start != -1 && end != -1 && end > start) {
                  final maybeJson = responseText.substring(start, end + 1);
                  final jsonResponse = jsonDecode(maybeJson) as Map<String, dynamic>;
                  return {
                    'title': jsonResponse['title'] as String? ?? 'Municipal Issue',
                    'description': jsonResponse['description'] as String? ?? responseText,
                  };
                }
              } catch (_) {}

              // Last resort: return raw text as description
              return {
                'title': 'Municipal Issue',
                'description': responseText,
              };
            }
          }
        }
        throw Exception('Invalid response format from Gemini API: ' + response.body);
      } else {
        // Include response body to help diagnose (e.g., API key errors, quota, safety blocks)
        throw Exception('Gemini API request failed: ${response.statusCode} ${response.reasonPhrase} - ${response.body}');
      }
    } catch (e) {
      // Print error to debug console for reference
      print('Gemini API error: $e');
      return null;
    }
  }
}
