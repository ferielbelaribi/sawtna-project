import 'package:flutter/material.dart';
import 'dart:io';
import 'dart:typed_data';
import 'package:image_picker/image_picker.dart';
import '../services/content_service.dart';
import 'package:flutter/foundation.dart' show kIsWeb;

enum ComplianceStatus { none, complies, mayBeFlagged, highlyLikelyCensored }

class CheckerScreen extends StatefulWidget {
  const CheckerScreen({super.key});

  @override
  State<CheckerScreen> createState() => _CheckerScreenState();
}

class _CheckerScreenState extends State<CheckerScreen> {
  File? _image;
  Uint8List? _imageBytes; // For web image data
  final ImagePicker _picker = ImagePicker();
  final TextEditingController _contentController = TextEditingController();
  ComplianceStatus _status = ComplianceStatus.none;
  bool _isLoading = false;
  String _resultMessage = '';
  double _confidence = 0.0;

  Future<void> _pickImage() async {
    try {
      final pickedFile = await _picker.pickImage(
        source: ImageSource.gallery,
        imageQuality: 85, // Reduce quality to avoid large files
        maxWidth: 1200, // Limit size
      );
      
      if (pickedFile != null) {
        setState(() {
          _contentController.clear();
          _status = ComplianceStatus.none;
          _resultMessage = '';
        });
        
        if (kIsWeb) {
          // Handle web platform
          final bytes = await pickedFile.readAsBytes();
          setState(() {
            _imageBytes = bytes;
          });
        } else {
          // Handle mobile platform
          setState(() {
            _image = File(pickedFile.path);
          });
        }
      }
    } catch (e) {
      setState(() {
        _resultMessage = 'Error picking image: $e';
        _status = ComplianceStatus.mayBeFlagged;
      });
    }
  }

  void _checkCompliance() async {
    // Validate text input
    if (_contentController.text.isNotEmpty) {
      if (_contentController.text.length > 5000) {
        setState(() {
          _resultMessage = 'Text is too long (max 5000 characters)';
          _status = ComplianceStatus.mayBeFlagged;
        });
        return;
      }
    }
    
    setState(() {
      _isLoading = true;
      _status = ComplianceStatus.none;
      _resultMessage = '';
    });

    try {
      if ((_image != null) || (_imageBytes != null)) {
        Map<String, dynamic> result;
        
        if (kIsWeb && _imageBytes != null) {
          // For web, we need to upload the bytes directly
          result = await ContentService.classifyImageFromBytes(_imageBytes!);
        } else if (_image != null) {
          // For mobile, use file path
          result = await ContentService.classifyImageFromPath(_image!.path);
        } else {
          setState(() {
            _isLoading = false;
            _resultMessage = 'No image selected';
            _status = ComplianceStatus.mayBeFlagged;
          });
          return;
        }
        
        _handleClassificationResult(result);
      } else if (_contentController.text.isNotEmpty) {
        final result = await ContentService.classifyText(_contentController.text);
        _handleClassificationResult(result);
      } else {
        setState(() {
          _isLoading = false;
          _resultMessage = 'Please enter text or select an image';
          _status = ComplianceStatus.mayBeFlagged;
        });
      }
    } catch (e) {
      setState(() {
        _isLoading = false;
        _resultMessage = 'Error: ${e.toString()}';
        _status = ComplianceStatus.mayBeFlagged;
      });
    }
  }

  void _handleClassificationResult(Map<String, dynamic> result) {
    setState(() {
      _isLoading = false;

      if (result['success'] == true) {
        final bool isAppropriate = result['isAppropriate'] ?? false;
        _confidence = (result['confidence'] ?? 0.0).toDouble();

        if (isAppropriate) {
          _status = ComplianceStatus.complies;
          _resultMessage = 'Content is appropriate ✅\nConfidence: ${(_confidence * 100).toStringAsFixed(1)}%';
        } else {
          _status = ComplianceStatus.highlyLikelyCensored;
          _resultMessage = 'Content may be inappropriate ❌\nConfidence: ${(_confidence * 100).toStringAsFixed(1)}%';
        }
      } else {
        _status = ComplianceStatus.mayBeFlagged;
        _resultMessage = result['message'] ?? 'Classification failed';
      }
    });
  }

  Widget _buildResultWidget() {
    switch (_status) {
      case ComplianceStatus.complies:
        return Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.check_circle, color: Colors.green, size: 60),
            const SizedBox(height: 8),
            Text(
              _resultMessage,
              style: const TextStyle(color: Colors.green, fontSize: 14),
              textAlign: TextAlign.center,
              maxLines: 3,
              overflow: TextOverflow.ellipsis,
            ),
          ],
        );
      case ComplianceStatus.mayBeFlagged:
        return Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.warning, color: Colors.orange, size: 60),
            const SizedBox(height: 8),
            Text(
              _resultMessage,
              style: const TextStyle(color: Colors.orange, fontSize: 14),
              textAlign: TextAlign.center,
              maxLines: 3,
              overflow: TextOverflow.ellipsis,
            ),
          ],
        );
      case ComplianceStatus.highlyLikelyCensored:
        return Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.cancel, color: Colors.red, size: 60),
            const SizedBox(height: 8),
            Text(
              _resultMessage,
              style: const TextStyle(color: Colors.red, fontSize: 14),
              textAlign: TextAlign.center,
              maxLines: 3,
              overflow: TextOverflow.ellipsis,
            ),
          ],
        );
      case ComplianceStatus.none:
      default:
        return _resultMessage.isNotEmpty
            ? Text(
                _resultMessage,
                style: const TextStyle(color: Colors.grey, fontSize: 14),
                textAlign: TextAlign.center,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              )
            : Container();
    }
  }

  // Helper method to display image based on platform
  Widget _buildImagePreview() {
    if (kIsWeb) {
      if (_imageBytes != null) {
        return Image.memory(_imageBytes!, height: 200, fit: BoxFit.cover);
      }
    } else {
      if (_image != null) {
        return Image.file(_image!, height: 200, fit: BoxFit.cover);
      }
    }
    
    return Container();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Compliance Checker',
            style: TextStyle(color: Colors.black)),
        backgroundColor: Colors.white,
        elevation: 0,
        iconTheme: const IconThemeData(color: Colors.black),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Compliance Check',
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 20),
            TextField(
              controller: _contentController,
              maxLines: 4,
              maxLength: 5000,
              decoration: const InputDecoration(
                hintText: 'Enter text to check',
                border: OutlineInputBorder(),
                counterText: '',
              ),
            ),
            const SizedBox(height: 20),
            _buildImagePreview(),
            const SizedBox(height: 20),
            Row(
              children: [
                ElevatedButton(
                  onPressed: _pickImage,
                  child: const Text('Pick Image'),
                ),
                const SizedBox(width: 10),
                ElevatedButton(
                  onPressed: _isLoading ? null : _checkCompliance,
                  child: _isLoading
                      ? const CircularProgressIndicator()
                      : const Text('Check'),
                ),
              ],
            ),
            const SizedBox(height: 30),
            Center(child: _buildResultWidget()),
          ],
        ),
      ),
    );
  }
}