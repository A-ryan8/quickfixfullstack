import 'dart:async';
import 'dart:io';
import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:image_picker/image_picker.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:geolocator/geolocator.dart';
import 'package:geocoding/geocoding.dart' as geocoding;
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:video_player/video_player.dart';
import 'package:path_provider/path_provider.dart';
import 'package:pdf/pdf.dart';
import 'package:pdf/widgets.dart' as pw;
import 'package:open_file/open_file.dart';
import 'services/api_service.dart';
import 'services/pdf_service.dart';

class UploadComplaintScreen extends StatefulWidget {
  const UploadComplaintScreen({super.key});

  @override
  State<UploadComplaintScreen> createState() => _UploadComplaintScreenState();
}

class _UploadComplaintScreenState extends State<UploadComplaintScreen> {
  final ImagePicker _picker = ImagePicker();
  XFile? _media;
  bool get _isVideo => _media != null && _media!.path.toLowerCase().endsWith('.mp4');

  VideoPlayerController? _videoController;
  final TextEditingController _desc = TextEditingController();
  final TextEditingController _locationManual = TextEditingController();
  String? _aiGeneratedTitle;

  bool _isUploading = false;
  bool _isProcessingImage = false;
  bool _permissionsDenied = false;
  bool _isGeneratingDescription = false;
  bool _isHoveringAutoGenerate = false;
  Position? _currentPosition;
  String _locationString = 'Getting location...';
  String? _address;
  static const String _openAiKey = String.fromEnvironment('OPENAI_API_KEY');
  String _username = 'Current User';
  String _status = 'Ready to submit';

  @override
  void initState() {
    super.initState();
    _getCurrentLocation();
  }

  @override
  void dispose() {
    _videoController?.dispose();
    _desc.dispose();
    _locationManual.dispose();
    super.dispose();
  }

  Future<void> _ensurePermissions() async {
    // Generic permission request used for non-camera flows (e.g., gallery/location)
    final statuses = await [
      Permission.photos, 
      Permission.storage, 
      Permission.locationWhenInUse
    ].request();
    final denied = statuses.values.any((s) => s.isDenied || s.isPermanentlyDenied || s.isRestricted);
    setState(() => _permissionsDenied = denied);
  }

  Future<bool> _ensureCameraPermission() async {
    final status = await Permission.camera.request();
    if (status.isGranted) return true;
    if (status.isPermanentlyDenied) {
      // Guide user to settings
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Camera permission permanently denied. Please enable it in Settings.')),
      );
    }
    return false;
  }

  Future<void> _pickFromCamera() async {
    final ok = await _ensureCameraPermission();
    if (!ok) return;
    setState(() => _isProcessingImage = true);
    try {
      final file = await _picker.pickImage(
        source: ImageSource.camera,
        maxWidth: 1080.0,
        maxHeight: 1920.0,
        imageQuality: 85,
      );
      if (file != null) {
        await _setMedia(file);
      }
    } finally {
      if (mounted) setState(() => _isProcessingImage = false);
    }
  }

  Future<void> _pickFromGallery() async {
    await _ensurePermissions();
    if (_permissionsDenied) return;
    setState(() => _isProcessingImage = true);
    try {
      // Prefer image selection with constraints when possible
      final file = await _picker.pickImage(
        source: ImageSource.gallery,
        maxWidth: 1080.0,
        maxHeight: 1920.0,
        imageQuality: 85,
      );
      if (file != null) {
        await _setMedia(file);
      }
    } finally {
      if (mounted) setState(() => _isProcessingImage = false);
    }
  }

  Future<void> _setMedia(XFile file) async {
    _videoController?.dispose();
    _videoController = null;
    setState(() => _media = file);
    if (file.path.toLowerCase().endsWith('.mp4')) {
      final controller = VideoPlayerController.file(File(file.path));
      await controller.initialize();
      controller.setLooping(true);
      setState(() => _videoController = controller);
      unawaited(controller.play());
    }
  }

  Future<void> _getCurrentLocation() async {
    try {
      final has = await Geolocator.isLocationServiceEnabled();
      if (!has) {
        setState(() => _locationString = 'Location services disabled');
        return;
      }
      
      final perm = await Geolocator.checkPermission();
      if (perm == LocationPermission.denied) {
        await Geolocator.requestPermission();
      }
      
      _currentPosition = await Geolocator.getCurrentPosition(desiredAccuracy: LocationAccuracy.high);
      setState(() {
        _locationString = 'Lat: ${_currentPosition!.latitude.toStringAsFixed(4)}, Lng: ${_currentPosition!.longitude.toStringAsFixed(4)}';
      });

      // Reverse geocode to human-readable address
      try {
        final placemarks = await geocoding.placemarkFromCoordinates(
          _currentPosition!.latitude,
          _currentPosition!.longitude,
        );
        if (placemarks.isNotEmpty) {
          final p = placemarks.first;
          final parts = [
            p.name,
            p.street,
            p.locality,
            p.administrativeArea,
            p.postalCode,
            p.country,
          ].where((e) => (e ?? '').toString().trim().isNotEmpty).toList();
          setState(() {
            _address = parts.join(', ');
          });
        }
      } catch (_) {}
    } catch (e) {
      setState(() => _locationString = 'Unable to get location');
    }
  }

  Future<void> _generateDescription() async {
    setState(() => _isGeneratingDescription = true);
    try {
      // Require an image for visual analysis
      if (_media == null) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Please capture or select a photo first.')),
        );
        return;
      }
      
      // Use Gemini API service for image analysis
      final aiResponse = await ApiService.analyzeImageWithGemini(
        imageFile: File(_media!.path),
        locationContext: _address ?? _locationString,
      );
      
      if (aiResponse != null) {
        setState(() {
          _aiGeneratedTitle = aiResponse['title'];
          _desc.text = aiResponse['description'] ?? '';
        });
      } else {
        _desc.text = _buildLocalAIFallback();
        setState(() {
          _aiGeneratedTitle = 'Municipal Issue';
        });
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Failed to generate description. Please try again.')),
        );
      }
    } catch (e) {
      _desc.text = _buildLocalAIFallback();
      setState(() {
        _aiGeneratedTitle = 'Municipal Issue';
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('AI error: $e')),
      );
    } finally {
      if (mounted) setState(() => _isGeneratingDescription = false);
    }
  }


  String _buildPromptForOpenAI() {
    final coords = _currentPosition != null
        ? '(${_currentPosition!.latitude.toStringAsFixed(5)}, ${_currentPosition!.longitude.toStringAsFixed(5)})'
        : '(unknown coordinates)';
    final address = _address ?? 'unknown address';
    return 'Generate a short, user-friendly municipal complaint description based on the attached photo '
        'and location $coords ($address). Keep it under 3 sentences.';
  }

  String _buildLocalAIFallback() {
    final address = _address ?? _locationString;
    return 'Issue reported near $address. The attached photo indicates a municipal problem that may affect public safety '
        'or infrastructure. Please review and take appropriate action.';
  }

  Future<void> _generatePDF() async {
    if (_isUploading) return;
    setState(() {
      _isUploading = true;
      _status = 'Uploading complaint...';
    });

    try {
      // Resolve location text
      final String locationText = _locationManual.text.isNotEmpty ? _locationManual.text : _locationString;

      // Prepare image file
      File? imageFile;
      if (_media != null) {
        imageFile = File(_media!.path);
      }

      // Generate AI title for the complaint (local heuristic fallback)
      String? aiTitle;
      try {
        if (_desc.text.isNotEmpty) {
          final description = _desc.text.toLowerCase();
          if (description.contains('pothole') || description.contains('road')) {
            aiTitle = 'Road Infrastructure Issue';
          } else if (description.contains('light') || description.contains('streetlight')) {
            aiTitle = 'Street Lighting Problem';
          } else if (description.contains('water') || description.contains('leak')) {
            aiTitle = 'Water Infrastructure Issue';
          } else if (description.contains('garbage') || description.contains('trash')) {
            aiTitle = 'Waste Management Issue';
          } else if (description.contains('traffic') || description.contains('signal')) {
            aiTitle = 'Traffic Management Issue';
          } else {
            aiTitle = 'Municipal Service Request';
          }
        }
      } catch (e) {
        print('Error generating AI title: $e');
      }

      // Generate PDF locally BEFORE making the request so we can send both in one POST
      final pdfBytes = await PdfService.generateComplaintReport(
        username: _username,
        location: locationText,
        description: _desc.text,
        detailedAddress: _address,
        aiTitle: aiTitle,
        aiDescription: _desc.text,
        imageFile: imageFile,
      );

      // Save PDF to temporary directory
      final tempDir = await getTemporaryDirectory();
      final timestamp = DateTime.now().millisecondsSinceEpoch;
      final tempFile = File('${tempDir.path}/complaint_$timestamp.pdf');
      await tempFile.writeAsBytes(pdfBytes);

      // Submit complaint to FastAPI backend in ONE request (with both image and pdf)
      // Use only localhost to prevent duplicate submissions
      String url = 'http://localhost:8000/api/complaints/submit';
      
      setState(() => _status = 'Submitting complaint...');

      try {
        var request = http.MultipartRequest('POST', Uri.parse(url));

        request.fields['title'] = _aiGeneratedTitle ?? aiTitle ?? 'Municipal Issue';
        request.fields['description'] = _desc.text.isNotEmpty ? _desc.text : 'No description provided';
        request.fields['location'] = locationText;

        // Add files
        request.files.add(await http.MultipartFile.fromPath('pdf', tempFile.path));
        if (imageFile != null) {
          request.files.add(await http.MultipartFile.fromPath('image', imageFile.path));
        }

        final streamedResponse = await request.send().timeout(
          const Duration(seconds: 15),
          onTimeout: () {
            throw Exception('Connection timeout');
          },
        );
        var response = await http.Response.fromStream(streamedResponse);

        if (response.statusCode == 200) {
          setState(() => _status = 'Complaint submitted successfully!');
          print('Complaint submitted successfully');
        } else {
          throw Exception('Server error: ${response.statusCode} - ${response.body}');
        }
      } catch (e) {
        setState(() => _status = 'Error: $e');
        print('Error submitting complaint: $e');
        throw e;
      }

      if (mounted) {
        // Open the PDF
        await OpenFile.open(tempFile.path);

          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: const Text('Complaint submitted and PDF generated successfully!'),
              duration: const Duration(seconds: 4),
              action: SnackBarAction(
                label: 'Download PDF',
                onPressed: () async {
                  try {
                    final docs = await getApplicationDocumentsDirectory();
                    final downloadPath = '${docs.path}/complaint_$timestamp.pdf';
                    await tempFile.copy(downloadPath);
                    if (!mounted) return;
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text('PDF saved to: $downloadPath')),
                    );
                  } catch (e) {
                    if (!mounted) return;
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text('Download failed: $e')),
                    );
                  }
                },
              ),
            ),
          );
        }
      } else {
        setState(() => _status = 'Error: Failed to submit. Status code: ${response!.statusCode}');
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Error: Failed to submit complaint. Status: ${response!.statusCode}')),
          );
        }
      }
    } catch (e) {
      setState(() => _status = 'Error: Could not connect to the server.');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: Could not connect to the server. $e')),
        );
      }
    } finally {
      setState(() => _isUploading = false);
    }
  }

  void _removeMedia() {
    setState(() {
      _media = null;
      _videoController?.dispose();
      _videoController = null;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5F5F5),
      appBar: AppBar(
        title: const Text('Upload Complaint'),
        backgroundColor: const Color(0xFF1976D2),
        foregroundColor: Colors.white,
        elevation: 0,
      ),
      body: Stack(
        children: [
          SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Top Section - Camera and Gallery Boxes
                _buildMediaSelectionBoxes(),
                const SizedBox(height: 24),
                
                // Middle Section - Description
                _buildDescriptionSection(),
                const SizedBox(height: 20),
                
                // Location Section
                _buildLocationSection(),
                const SizedBox(height: 100), // Space for bottom button
              ],
            ),
          ),
          
          // Bottom Button
          Positioned(
            left: 16,
            right: 16,
            bottom: 16,
            child: _buildNextButton(),
          ),
          
          // Processing overlay for image pick
          if (_isProcessingImage)
            Positioned.fill(
              child: Container(
                color: Colors.black54,
                child: const Center(
                  child: SizedBox(
                    width: 48,
                    height: 48,
                    child: CircularProgressIndicator(
                      strokeWidth: 4,
                      valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                    ),
                  ),
                ),
              ),
            ),

          // Permissions Overlay
          if (_permissionsDenied)
            Positioned.fill(
              child: Container(
                color: Colors.black.withOpacity(0.5),
                child: Center(
                  child: Container(
                    margin: const EdgeInsets.all(20),
                    padding: const EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Icon(Icons.privacy_tip, color: Colors.red, size: 48),
                        const SizedBox(height: 16),
                        const Text(
                          'Permissions Required',
                          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                        ),
                        const SizedBox(height: 8),
                        const Text(
                          'Camera and location permissions are needed to upload complaints.',
                          textAlign: TextAlign.center,
                        ),
                        const SizedBox(height: 20),
                        ElevatedButton(
                          onPressed: () async {
                            await openAppSettings();
                            setState(() => _permissionsDenied = false);
                          },
                          child: const Text('Open Settings'),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildMediaSelectionBoxes() {
    if (_media != null) {
      // Show media preview when selected
      return Column(
        children: [
          Container(
            height: 200,
            width: double.infinity,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: const Color(0xFF1976D2), width: 2),
              boxShadow: [
                BoxShadow(
                  color: const Color(0xFF1976D2).withOpacity(0.3),
                  blurRadius: 8,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(14),
              child: _isVideo && _videoController != null
                  ? VideoPlayer(_videoController!)
                  : Image.file(File(_media!.path), fit: BoxFit.cover),
            ),
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: _pickFromCamera,
                  icon: const Icon(Icons.camera_alt),
                  label: const Text('Camera'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF1976D2),
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 12),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: _pickFromGallery,
                  icon: const Icon(Icons.photo_library),
                  label: const Text('Gallery'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF1976D2),
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 12),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 12),
              ElevatedButton.icon(
                onPressed: _removeMedia,
                icon: const Icon(Icons.delete),
                label: const Text('Remove'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.red,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
              ),
            ],
          ),
        ],
      );
    }
    
    // Show selection boxes when no media selected
    return Row(
      children: [
        // Camera Box
        Expanded(
          child: GestureDetector(
            onTap: _pickFromCamera,
            child: Container(
              height: 160,
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [Color(0xFF64B5F6), Color(0xFF1976D2)],
                ),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: const Color(0xFF1976D2), width: 2),
                boxShadow: [
                  BoxShadow(
                    color: const Color(0xFF1976D2).withOpacity(0.3),
                    blurRadius: 8,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              child: const Center(
                child: Icon(
                  Icons.camera_alt,
                  size: 48,
                  color: Colors.white,
                ),
              ),
            ),
          ),
        ),
        const SizedBox(width: 16),
        
        // Gallery Box
        Expanded(
          child: GestureDetector(
            onTap: _pickFromGallery,
            child: Container(
              height: 160,
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [Color(0xFF80DEEA), Color(0xFFE91E63)],
                ),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: const Color(0xFF1976D2), width: 2),
                boxShadow: [
                  BoxShadow(
                    color: const Color(0xFF1976D2).withOpacity(0.3),
                    blurRadius: 8,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              child: const Center(
                child: Icon(
                  Icons.photo_library,
                  size: 48,
                  color: Colors.white,
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildDescriptionSection() {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Description (Optional)',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: Colors.black,
              ),
            ),
            const SizedBox(height: 16),
            
            // AI Generated Title Display
            if (_aiGeneratedTitle != null) ...[
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: const Color(0xFFE3F2FD),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: const Color(0xFF1976D2), width: 1),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        const Icon(Icons.auto_awesome, size: 16, color: Color(0xFF1976D2)),
                        const SizedBox(width: 8),
                        const Text(
                          'AI Generated Title:',
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w600,
                            color: Color(0xFF1976D2),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    Text(
                      _aiGeneratedTitle!,
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFF1976D2),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),
            ],
            // Enhanced ChatGPT-style text field
            Container(
              decoration: BoxDecoration(
                border: Border.all(color: Colors.grey.shade300),
                borderRadius: BorderRadius.circular(12),
                color: Colors.white,
              ),
              child: Column(
                children: [
                  // Text input area
                  TextField(
                    controller: _desc,
                    maxLines: 6,
                    decoration: const InputDecoration(
                      hintText: 'Describe the issue in detail...',
                      border: InputBorder.none,
                      contentPadding: EdgeInsets.fromLTRB(16, 16, 16, 8),
                    ),
                  ),
                  // Bottom row with buttons and icons
                  Container(
                    padding: const EdgeInsets.fromLTRB(12, 8, 12, 12),
                    child: Row(
                      children: [
                        // Auto Generate button
                        MouseRegion(
                            onEnter: (_) => setState(() => _isHoveringAutoGenerate = true),
                            onExit: (_) => setState(() => _isHoveringAutoGenerate = false),
                            child: AnimatedContainer(
                              duration: const Duration(milliseconds: 200),
                              transform: Matrix4.identity()..scale(_isHoveringAutoGenerate ? 1.05 : 1.0),
                              child: ElevatedButton(
                                onPressed: _isGeneratingDescription ? null : _generateDescription,
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: Colors.transparent,
                                  foregroundColor: Colors.white,
                                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                                  shape: RoundedRectangleBorder(
                                    borderRadius: BorderRadius.circular(20),
                                  ),
                                  elevation: 0,
                                  shadowColor: Colors.transparent,
                                ),
                                child: Container(
                                  decoration: BoxDecoration(
                                    gradient: LinearGradient(
                                      begin: Alignment.bottomRight,
                                      end: Alignment.topLeft,
                                      colors: _isHoveringAutoGenerate
                                          ? [const Color(0xFFDC2626), const Color(0xFFF87171)]
                                          : [const Color(0xFFE53E3E), const Color(0xFFFC8181)],
                                    ),
                                    borderRadius: BorderRadius.circular(20),
                                    boxShadow: _isHoveringAutoGenerate
                                        ? [
                                            BoxShadow(
                                              color: const Color(0xFFE53E3E).withOpacity(0.3),
                                              blurRadius: 8,
                                              offset: const Offset(0, 2),
                                            ),
                                          ]
                                        : null,
                                  ),
                                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                                  child: Row(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      if (_isGeneratingDescription)
                                        const SizedBox(
                                          width: 16,
                                          height: 16,
                                          child: CircularProgressIndicator(
                                            strokeWidth: 2,
                                            color: Colors.white,
                                          ),
                                        )
                                      else
                                        const Icon(Icons.auto_awesome, size: 16),
                                      const SizedBox(width: 6),
                                      Text(
                                        _isGeneratingDescription ? 'Generating...' : 'Auto Generate',
                                        style: const TextStyle(
                                          fontSize: 12,
                                          fontWeight: FontWeight.w500,
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              ),
                            ),
                          ),
                        const Spacer(),
                        // Mic icon
                        Container(
                          decoration: BoxDecoration(
                            color: Colors.grey.shade100,
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: IconButton(
                            onPressed: () {
                              // TODO: Implement voice recording functionality
                              ScaffoldMessenger.of(context).showSnackBar(
                                const SnackBar(content: Text('Voice recording feature coming soon!')),
                              );
                            },
                            icon: const Icon(Icons.mic, size: 20, color: Colors.grey),
                            padding: const EdgeInsets.all(8),
                            constraints: const BoxConstraints(
                              minWidth: 36,
                              minHeight: 36,
                            ),
                          ),
                        ),
                        const SizedBox(width: 8),
                        // Upload/Send icon
                        Container(
                          decoration: BoxDecoration(
                            color: const Color(0xFF1976D2),
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: IconButton(
                            onPressed: () {
                              // TODO: Implement send/upload functionality
                              ScaffoldMessenger.of(context).showSnackBar(
                                const SnackBar(content: Text('Send functionality coming soon!')),
                              );
                            },
                            icon: const Icon(Icons.send, size: 20, color: Colors.white),
                            padding: const EdgeInsets.all(8),
                            constraints: const BoxConstraints(
                              minWidth: 36,
                              minHeight: 36,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildLocationSection() {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.location_on, color: Color(0xFF1976D2), size: 24),
                const SizedBox(width: 8),
                const Text(
                  'Location (Optional)',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Colors.black,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            // GPS Location Display
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.grey.shade50,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.grey.shade200),
              ),
              child: Row(
                children: [
                  const Icon(Icons.gps_fixed, size: 20, color: Colors.grey),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      _address != null ? '$_address\n($_locationString)' : _locationString,
                      style: const TextStyle(fontSize: 16),
                    ),
                  ),
                  IconButton(
                    onPressed: _getCurrentLocation,
                    icon: const Icon(Icons.refresh, size: 20, color: Color(0xFF1976D2)),
                    tooltip: 'Refresh location',
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),
            // Manual Location Input
            Container(
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.grey.shade200),
              ),
              padding: const EdgeInsets.all(12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Manual Location (Optional)',
                    style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600),
                  ),
                  const SizedBox(height: 8),
                  TextField(
                    controller: _locationManual,
                    decoration: InputDecoration(
                      hintText: 'Enter location or landmark...',
                      filled: true,
                      fillColor: Colors.grey.shade50,
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(8),
                        borderSide: BorderSide(color: Colors.grey.shade300),
                      ),
                      enabledBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(8),
                        borderSide: BorderSide(color: Colors.grey.shade300),
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(8),
                        borderSide: const BorderSide(color: Color(0xFF1976D2)),
                      ),
                      contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildNextButton() {
    return Container(
      width: double.infinity,
      height: 56,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF1976D2).withOpacity(0.3),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: ElevatedButton(
        onPressed: _isUploading ? null : _generatePDF,
        style: ElevatedButton.styleFrom(
          backgroundColor: const Color(0xFF1976D2),
          foregroundColor: Colors.white,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          elevation: 0,
        ),
        child: _isUploading
            ? Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      color: Colors.white,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Text(_status, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                ],
              )
            : const Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.arrow_forward, size: 24),
                  SizedBox(width: 8),
                  Text('Submit Complaint', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                ],
              ),
      ),
    );
  }
}