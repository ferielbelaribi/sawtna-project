import 'package:flutter/material.dart';
import 'dart:io';
import 'dart:convert';
import 'dart:typed_data';
import 'package:image_picker/image_picker.dart';
import 'package:http/http.dart' as http;
import 'package:flutter/foundation.dart' show kIsWeb;

class ImageGenerationScreen extends StatefulWidget {
  const ImageGenerationScreen({super.key});

  @override
  State<ImageGenerationScreen> createState() => _ImageGenerationScreenState();
}

class _ImageGenerationScreenState extends State<ImageGenerationScreen> {
  File? _image;
  Uint8List? _imageBytes;
  final ImagePicker _picker = ImagePicker();
  bool _isLoading = false;
  bool _isGeneratingFromPrompt = false;
  bool _isDetectingBlood = false;
  final TextEditingController _promptController = TextEditingController();
  Uint8List? _generatedImageBytes;
  Uint8List? _bloodDetectionImageBytes;
  int _bloodRegionsDetected = 0;
  String? _errorMessage;

  // Use localhost for development
  static const String API_BASE_URL = 'http://127.0.0.1:8000';

  Future<void> _pickImage() async {
    final pickedFile = await _picker.pickImage(source: ImageSource.gallery);
    
    if (pickedFile != null) {
      if (kIsWeb) {
        // For web: convert XFile to bytes
        final bytes = await pickedFile.readAsBytes();
        setState(() {
          _imageBytes = bytes;
          _image = null;
          _bloodDetectionImageBytes = null;
          _bloodRegionsDetected = 0;
          _errorMessage = null;
        });
      } else {
        // For mobile: use File
        setState(() {
          _image = File(pickedFile.path);
          _imageBytes = null;
          _bloodDetectionImageBytes = null;
          _bloodRegionsDetected = 0;
          _errorMessage = null;
        });
      }
    }
  }

  bool get _hasImage {
    return kIsWeb ? _imageBytes != null : _image != null;
  }

  Widget _buildImagePreview() {
    if (kIsWeb && _imageBytes != null) {
      return Image.memory(_imageBytes!, fit: BoxFit.cover);
    } else if (!kIsWeb && _image != null) {
      return Image.file(_image!, fit: BoxFit.cover);
    } else {
      return Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: const [
          Icon(Icons.cloud_upload, size: 40, color: Colors.grey),
          SizedBox(height: 10),
          Text('Upload Image'),
          Text('or drag & drop'),
        ],
      );
    }
  }

  Future<void> _detectBlood() async {
    if (!_hasImage) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select an image first')),
      );
      return;
    }

    setState(() {
      _isLoading = true;
      _isDetectingBlood = true;
      _errorMessage = null;
    });

    try {
      var request = http.MultipartRequest(
        'POST',
        Uri.parse('$API_BASE_URL/content/check-blood'),
      );

      // Add image file
      if (kIsWeb) {
        request.files.add(
          http.MultipartFile.fromBytes(
            'file',
            _imageBytes!,
            filename: 'blood_detection_image.jpg',
          ),
        );
      } else {
        request.files.add(
          await http.MultipartFile.fromPath(
            'file',
            _image!.path,
            filename: 'blood_detection_image.jpg',
          ),
        );
      }

      // Send request
      var response = await request.send();
      var responseData = await response.stream.toBytes();
      var responseString = String.fromCharCodes(responseData);
      var jsonResponse = jsonDecode(responseString);

      if (response.statusCode == 200) {
        // Download the processed image
        final processedImageUrl = '$API_BASE_URL/content/${jsonResponse["processed_file"]}';
        final imageResponse = await http.get(Uri.parse(processedImageUrl));
        
        if (imageResponse.statusCode == 200 && imageResponse.bodyBytes.isNotEmpty) {
          setState(() {
            _bloodDetectionImageBytes = imageResponse.bodyBytes;
            _bloodRegionsDetected = jsonResponse["blood_regions_detected"] ?? 0;
          });

          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Blood detection completed: $_bloodRegionsDetected regions found')),
          );
        } else {
          setState(() {
            _errorMessage = 'Failed to load processed image. Status: ${imageResponse.statusCode}';
          });
        }
      } else {
        setState(() {
          _errorMessage = jsonResponse["detail"] ?? 'Blood detection failed with status ${response.statusCode}';
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Error during blood detection: $e';
      });
    } finally {
      setState(() {
        _isLoading = false;
        _isDetectingBlood = false;
      });
    }
  }

  Future<void> _generateImageFromPrompt() async {
    if (_promptController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter a prompt')),
      );
      return;
    }

    setState(() {
      _isLoading = true;
      _isGeneratingFromPrompt = true;
      _errorMessage = null;
      _generatedImageBytes = null;
    });

    try {
      final response = await http.post(
        Uri.parse('$API_BASE_URL/content/generate-image'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'prompt': _promptController.text,
        }),
      );

      final Map<String, dynamic> data = jsonDecode(response.body);

      if (response.statusCode == 200) {
        if (data['status'] == 'success' && data['image_data'] != null) {
          try {
            final Uint8List imageBytes = base64Decode(data['image_data']);
            
            if (imageBytes.isNotEmpty) {
              setState(() {
                _generatedImageBytes = imageBytes;
              });
              
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Image generated successfully!')),
              );
            } else {
              setState(() {
                _errorMessage = 'Received empty image data';
              });
            }
          } catch (e) {
            setState(() {
              _errorMessage = 'Failed to decode image: $e';
            });
          }
        } else {
          setState(() {
            _errorMessage = data['detail'] ?? 'Failed to generate image';
          });
        }
      } else {
        setState(() {
          _errorMessage = data['detail'] ?? 'Server error: ${response.statusCode}';
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Connection error: $e';
      });
    } finally {
      setState(() {
        _isLoading = false;
        _isGeneratingFromPrompt = false;
      });
    }
  }

  void _showBloodDetectionDialog() {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: Text('Blood Detection Result ($_bloodRegionsDetected regions)'),
          content: _bloodDetectionImageBytes != null
              ? Image.memory(_bloodDetectionImageBytes!)
              : const Text('No detection result available'),
          actions: <Widget>[
            TextButton(
              onPressed: () {
                Navigator.of(context).pop();
              },
              child: const Text('Close'),
            ),
          ],
        );
      },
    );
  }

  Future<void> _downloadImage() async {
    if (_generatedImageBytes != null) {
      try {
        // For web
        if (kIsWeb) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Right-click on the image and select "Save Image" to download')),
          );
        } 
        // For mobile
        else {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Image is displayed on screen. Take a screenshot to save it.')),
          );
        }
      } catch (e) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to download image: $e')),
        );
      }
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('No image to download')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Image Generation & Blood Detection', style: TextStyle(color: Colors.black)),
        backgroundColor: Colors.white,
        elevation: 0,
        iconTheme: const IconThemeData(color: Colors.black),
      ),
      body: Padding(
        padding: const EdgeInsets.all(20.0),
        child: ListView(
          children: [
            // Error message display
            if (_errorMessage != null) ...[
              Container(
                padding: const EdgeInsets.all(12),
                margin: const EdgeInsets.only(bottom: 16),
                decoration: BoxDecoration(
                  color: Colors.red[100],
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.red),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.error, color: Colors.red),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        _errorMessage!,
                        style: const TextStyle(color: Colors.red),
                      ),
                    ),
                    IconButton(
                      icon: const Icon(Icons.close, size: 16),
                      onPressed: () {
                        setState(() {
                          _errorMessage = null;
                        });
                      },
                    ),
                  ],
                ),
              ),
            ],

            // Upload Image Section
            const Text(
              'Upload Image',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 10),
            const Text(
              'Upload an image for blood detection or generation',
              style: TextStyle(color: Colors.grey),
            ),
            const SizedBox(height: 15),
            GestureDetector(
              onTap: _pickImage,
              child: Container(
                width: double.infinity,
                height: 150,
                decoration: BoxDecoration(
                  color: Colors.grey[200],
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: Colors.grey),
                ),
                child: _buildImagePreview(),
              ),
            ),
            const SizedBox(height: 20),
            
            // Blood Detection Button
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _isLoading ? null : _detectBlood,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.red,
                  padding: const EdgeInsets.symmetric(vertical: 15),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(30),
                  ),
                ),
                child: _isLoading && _isDetectingBlood
                    ? const CircularProgressIndicator(color: Colors.white)
                    : const Text(
                        'Detect Blood',
                        style: TextStyle(fontSize: 16, color: Colors.white),
                      ),
              ),
            ),
            
            // Show blood detection result if available
            if (_bloodDetectionImageBytes != null) ...[
              const SizedBox(height: 20),
              const Text(
                'Blood Detection Result',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 10),
              Text(
                'Blood regions detected: $_bloodRegionsDetected',
                style: TextStyle(
                  color: _bloodRegionsDetected > 0 ? Colors.red : Colors.green,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 10),
              GestureDetector(
                onTap: _showBloodDetectionDialog,
                child: Container(
                  height: 150,
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(color: Colors.grey),
                  ),
                  child: Image.memory(_bloodDetectionImageBytes!, fit: BoxFit.cover),
                ),
              ),
            ],

            const SizedBox(height: 40),
            const Divider(),
            const SizedBox(height: 20),

            // Generate from Prompt Section
            const Text(
              'Generate from Text',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 10),
            const Text(
              'Describe the image you want to generate',
              style: TextStyle(color: Colors.grey),
            ),
            const SizedBox(height: 15),
            TextField(
              controller: _promptController,
              decoration: InputDecoration(
                hintText: 'Enter a detailed description...',
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(10),
                ),
                filled: true,
                fillColor: Colors.grey[100],
                contentPadding: const EdgeInsets.symmetric(
                  horizontal: 16,
                  vertical: 14,
                ),
              ),
              maxLines: 3,
            ),
            const SizedBox(height: 20),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _isLoading ? null : _generateImageFromPrompt,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.red,
                  padding: const EdgeInsets.symmetric(vertical: 15),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(30),
                  ),
                ),
                child: _isLoading && _isGeneratingFromPrompt
                    ? const CircularProgressIndicator(color: Colors.white)
                    : const Text(
                        'Generate from Text',
                        style: TextStyle(fontSize: 16, color: Colors.white),
                      ),
              ),
            ),

            const SizedBox(height: 30),
            const Text(
              'Generated Image Results',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 10),
            Container(
              height: 200,
              width: double.infinity,
              decoration: BoxDecoration(
                color: Colors.grey[100],
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: Colors.grey),
              ),
              child: _generatedImageBytes != null
                  ? Image.memory(_generatedImageBytes!, fit: BoxFit.cover)
                  : const Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.image, size: 40, color: Colors.grey),
                          SizedBox(height: 10),
                          Text('Generated image will appear here'),
                        ],
                      ),
                    ),
            ),
            const SizedBox(height: 20),
            Center(
              child: TextButton.icon(
                onPressed: _downloadImage,
                icon: const Icon(Icons.download, color: Colors.red),
                label: const Text(
                  'Download Image',
                  style: TextStyle(color: Colors.red),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  @override
  void dispose() {
    _promptController.dispose();
    super.dispose();
  }
}