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
import 'package:provider/provider.dart';
import 'l10n/app_localizations.dart';
import 'services/api_service.dart';
import 'services/pdf_service.dart';
import 'providers/locale_provider.dart';

class UploadComplaintScreen extends StatefulWidget {
  const UploadComplaintScreen({super.key});

  @override
  State<UploadComplaintScreen> createState() => _UploadComplaintScreenState();
}

class _UploadComplaintScreenState extends State<UploadComplaintScreen>
    with TickerProviderStateMixin {
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

  // Animation controllers
  late AnimationController _fadeController;
  late AnimationController _slideController;
  late AnimationController _scaleController;
  late Animation<double> _fadeAnimation;
  late Animation<Offset> _slideAnimation;
  late Animation<double> _scaleAnimation;

  @override
  void initState() {
    super.initState();
    _initializeAnimations();
    _getCurrentLocation();
  }

  void _initializeAnimations() {
    _fadeController = AnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
    );
    _slideController = AnimationController(
      duration: const Duration(milliseconds: 600),
      vsync: this,
    );
    _scaleController = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );

    _fadeAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _fadeController,
      curve: Curves.easeInOut,
    ));

    _slideAnimation = Tween<Offset>(
      begin: const Offset(0, 0.3),
      end: Offset.zero,
    ).animate(CurvedAnimation(
      parent: _slideController,
      curve: Curves.easeOutCubic,
    ));

    _scaleAnimation = Tween<double>(
      begin: 0.8,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _scaleController,
      curve: Curves.elasticOut,
    ));

    // Start animations
    _fadeController.forward();
    _slideController.forward();
    _scaleController.forward();
  }

  @override
  void dispose() {
    _videoController?.dispose();
    _desc.dispose();
    _locationManual.dispose();
    _fadeController.dispose();
    _slideController.dispose();
    _scaleController.dispose();
    super.dispose();
  }

  Future<void> _ensurePermissions() async {
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
      final l10n = AppLocalizations.of(context)!;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(l10n.cameraPermissionDenied)),
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
        final l10n = AppLocalizations.of(context)!;
        setState(() => _locationString = l10n.locationServicesDisabled);
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
      final l10n = AppLocalizations.of(context)!;
      setState(() => _locationString = l10n.unableToGetLocation);
    }
  }

  Future<void> _generateDescription() async {
    setState(() => _isGeneratingDescription = true);
    
    // Get current language from provider
    final localeProvider = Provider.of<LocaleProvider>(context, listen: false);
    final currentLanguage = localeProvider.languageCode;
    
    try {
      if (_media == null) {
        final l10n = AppLocalizations.of(context)!;
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(l10n.pleaseCapturePhotoFirst)),
        );
        return;
      }
      
      final aiResponse = await ApiService.analyzeImageWithGemini(
        imageFile: File(_media!.path),
        locationContext: _address ?? _locationString,
        language: currentLanguage,
      );
      
      if (aiResponse != null) {
        setState(() {
          _aiGeneratedTitle = aiResponse['title'];
          _desc.text = aiResponse['description'] ?? '';
        });
      } else {
        _desc.text = _buildLocalAIFallback();
        setState(() {
          _aiGeneratedTitle = _getLocalizedTitle(currentLanguage);
        });
        final l10n = AppLocalizations.of(context)!;
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(l10n.failedToGenerateDescription)),
        );
      }
    } catch (e) {
      _desc.text = _buildLocalAIFallback();
      setState(() {
        _aiGeneratedTitle = _getLocalizedTitle(currentLanguage);
      });
      final l10n = AppLocalizations.of(context)!;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('${l10n.aiError} $e')),
      );
    } finally {
      if (mounted) setState(() => _isGeneratingDescription = false);
    }
  }

  String _getLocalizedTitle(String languageCode) {
    switch (languageCode) {
      case 'hi':
        return 'नगरपालिका समस्या';
      case 'mr':
        return 'नगरपालिका समस्या';
      case 'en':
      default:
        return 'Municipal Issue';
    }
  }

  String _buildLocalAIFallback() {
    final address = _address ?? _locationString;
    final localeProvider = Provider.of<LocaleProvider>(context, listen: false);
    final currentLanguage = localeProvider.languageCode;
    
    switch (currentLanguage) {
      case 'hi':
        return '$address के पास समस्या की रिपोर्ट। संलग्न फोटो एक नगरपालिका समस्या को इंगित करता है जो सार्वजनिक सुरक्षा या बुनियादी ढांचे को प्रभावित कर सकती है। कृपया समीक्षा करें और उचित कार्रवाई करें।';
      case 'mr':
        return '$address जवळ समस्या अहवाल दिला. संलग्न फोटो एक नगरपालिका समस्या दर्शवतो जी सार्वजनिक सुरक्षा किंवा पायाभूत सुविधांना प्रभावित करू शकते. कृपया समीक्षा करा आणि योग्य कारवाई करा.';
      case 'en':
      default:
        return 'Issue reported near $address. The attached photo indicates a municipal problem that may affect public safety '
            'or infrastructure. Please review and take appropriate action.';
    }
  }

  Future<void> _generatePDF() async {
    if (_isUploading) return;
    final l10n = AppLocalizations.of(context)!;
    setState(() {
      _isUploading = true;
      _status = l10n.uploadingComplaint;
    });

    try {
      final String locationText = _locationManual.text.isNotEmpty ? _locationManual.text : _locationString;
      File? imageFile;
      if (_media != null) {
        imageFile = File(_media!.path);
      }

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

      final pdfBytes = await PdfService.generateComplaintReport(
        username: _username,
        location: locationText,
        description: _desc.text,
        detailedAddress: _address,
        aiTitle: aiTitle,
        aiDescription: _desc.text,
        imageFile: imageFile,
      );

      final tempDir = await getTemporaryDirectory();
      final timestamp = DateTime.now().millisecondsSinceEpoch;
      final tempFile = File('${tempDir.path}/complaint_$timestamp.pdf');
      await tempFile.writeAsBytes(pdfBytes);

      List<String> urls = [
        'http://10.45.233.189:8000/api/complaints/submit',
        'http://10.0.2.2:8000/api/complaints/submit',
        'http://localhost:8000/api/complaints/submit',
        'http://127.0.0.1:8000/api/complaints/submit',
      ];

      http.Response? response;
      String? lastError;

      for (String url in urls) {
        try {
          setState(() => _status = 'Trying to connect to: $url');

          var request = http.MultipartRequest('POST', Uri.parse(url));

          request.fields['title'] = _aiGeneratedTitle ?? aiTitle ?? 'Municipal Issue';
          request.fields['description'] = _desc.text.isNotEmpty ? _desc.text : 'No description provided';
          request.fields['location'] = locationText;

          request.files.add(await http.MultipartFile.fromPath('pdf', tempFile.path));
          if (imageFile != null) {
            request.files.add(await http.MultipartFile.fromPath('image', imageFile.path));
          }

          final streamedResponse = await request.send().timeout(
            const Duration(seconds: 10),
            onTimeout: () {
              throw Exception('Connection timeout');
            },
          );
          response = await http.Response.fromStream(streamedResponse);
          break;
        } catch (e) {
          lastError = e.toString();
          print('Failed to connect to $url: $e');
          continue;
        }
      }

      if (response == null) {
        throw Exception('Could not connect to any server. Last error: $lastError');
      }

      if (response!.statusCode == 200 || response!.statusCode == 201) {
        setState(() => _status = l10n.complaintSubmittedSuccessfully);

        if (mounted) {
          await OpenFile.open(tempFile.path);

          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(l10n.complaintSubmittedPdfGenerated),
              duration: const Duration(seconds: 4),
              action: SnackBarAction(
                label: l10n.downloadPdf,
                onPressed: () async {
                  try {
                    final docs = await getApplicationDocumentsDirectory();
                    final downloadPath = '${docs.path}/complaint_$timestamp.pdf';
                    await tempFile.copy(downloadPath);
                    if (!mounted) return;
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text('${l10n.pdfSavedTo} $downloadPath')),
                    );
                  } catch (e) {
                    if (!mounted) return;
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text('${l10n.downloadFailed} $e')),
                    );
                  }
                },
              ),
            ),
          );
        }
      } else {
        setState(() => _status = '${l10n.errorFailedSubmit} ${response!.statusCode}');
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('${l10n.errorFailedSubmit} ${response!.statusCode}')),
          );
        }
      }
    } catch (e) {
      setState(() => _status = l10n.errorCouldNotConnect);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('${l10n.errorCouldNotConnect} $e')),
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
    final l10n = AppLocalizations.of(context)!;
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        title: Text(
          l10n.reportIssue,
          style: const TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 20,
          ),
        ),
        backgroundColor: Colors.white,
        foregroundColor: const Color(0xFF1E293B),
        elevation: 0,
        centerTitle: true,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios, size: 20),
          onPressed: () => Navigator.pop(context),
        ),
        actions: [
          _buildLanguageSwitcher(),
          IconButton(
            icon: const Icon(Icons.help_outline, size: 24),
            onPressed: () {
              _showHelpDialog();
            },
          ),
        ],
      ),
      body: Stack(
        children: [
          FadeTransition(
            opacity: _fadeAnimation,
            child: SlideTransition(
              position: _slideAnimation,
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Header Section
                    _buildHeaderSection(),
                    const SizedBox(height: 24),
                    
                    // Media Selection Section
                    _buildMediaSelectionSection(),
                    const SizedBox(height: 24),
                    
                    // Description Section
                    _buildDescriptionSection(),
                    const SizedBox(height: 24),
                    
                    // Location Section
                    _buildLocationSection(),
                    const SizedBox(height: 100), // Space for bottom button
                  ],
                ),
              ),
            ),
          ),
          
          // Bottom Submit Button
          Positioned(
            left: 20,
            right: 20,
            bottom: 20,
            child: ScaleTransition(
              scale: _scaleAnimation,
              child: _buildSubmitButton(),
            ),
          ),
          
          // Processing Overlays
          if (_isProcessingImage) _buildProcessingOverlay(),
          if (_permissionsDenied) _buildPermissionsOverlay(),
        ],
      ),
    );
  }

  Widget _buildHeaderSection() {
    final l10n = AppLocalizations.of(context)!;
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xFF3B82F6), Color(0xFF1D4ED8)],
        ),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF3B82F6).withOpacity(0.3),
            blurRadius: 20,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Icon(
                  Icons.report_problem,
                  color: Colors.white,
                  size: 28,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      l10n.reportMunicipalIssue,
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      l10n.helpImproveCommunity,
                      style: const TextStyle(
                        color: Colors.white70,
                        fontSize: 14,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildMediaSelectionSection() {
    final l10n = AppLocalizations.of(context)!;
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 20,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: const Color(0xFF3B82F6).withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Icon(
                    Icons.camera_alt,
                    color: Color(0xFF3B82F6),
                    size: 20,
                  ),
                ),
                const SizedBox(width: 12),
                Text(
                  l10n.addPhotoVideo,
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF1E293B),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            if (_media != null) _buildMediaPreview() else _buildMediaSelectionButtons(),
          ],
        ),
      ),
    );
  }

  Widget _buildMediaPreview() {
    final l10n = AppLocalizations.of(context)!;
    return Column(
      children: [
        Container(
          height: 200,
          width: double.infinity,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: const Color(0xFF3B82F6), width: 2),
            boxShadow: [
              BoxShadow(
                color: const Color(0xFF3B82F6).withOpacity(0.2),
                blurRadius: 12,
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
              child: _buildActionButton(
                icon: Icons.camera_alt,
                label: l10n.camera,
                onPressed: _pickFromCamera,
                color: const Color(0xFF3B82F6),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _buildActionButton(
                icon: Icons.photo_library,
                label: l10n.gallery,
                onPressed: _pickFromGallery,
                color: const Color(0xFF10B981),
              ),
            ),
            const SizedBox(width: 12),
            _buildActionButton(
              icon: Icons.delete,
              label: l10n.remove,
              onPressed: _removeMedia,
              color: const Color(0xFFEF4444),
              isCompact: true,
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildMediaSelectionButtons() {
    final l10n = AppLocalizations.of(context)!;
    return Row(
      children: [
        Expanded(
          child: _buildMediaSelectionCard(
            icon: Icons.camera_alt,
            title: l10n.camera,
            subtitle: l10n.takePhoto,
            gradient: const LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [Color(0xFF3B82F6), Color(0xFF1D4ED8)],
            ),
            onTap: _pickFromCamera,
          ),
        ),
        const SizedBox(width: 16),
        Expanded(
          child: _buildMediaSelectionCard(
            icon: Icons.photo_library,
            title: l10n.gallery,
            subtitle: l10n.chooseExisting,
            gradient: const LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [Color(0xFF10B981), Color(0xFF059669)],
            ),
            onTap: _pickFromGallery,
          ),
        ),
      ],
    );
  }

  Widget _buildMediaSelectionCard({
    required IconData icon,
    required String title,
    required String subtitle,
    required Gradient gradient,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        height: 120,
        decoration: BoxDecoration(
          gradient: gradient,
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(
              color: gradient.colors.first.withOpacity(0.3),
              blurRadius: 12,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, color: Colors.white, size: 32),
            const SizedBox(height: 8),
            Text(
              title,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            Text(
              subtitle,
              style: const TextStyle(
                color: Colors.white70,
                fontSize: 12,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDescriptionSection() {
    final l10n = AppLocalizations.of(context)!;
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 20,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: const Color(0xFF8B5CF6).withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Icon(
                    Icons.description,
                    color: Color(0xFF8B5CF6),
                    size: 20,
                  ),
                ),
                const SizedBox(width: 12),
                Text(
                  l10n.description,
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF1E293B),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            
            // AI Generated Title Display
            if (_aiGeneratedTitle != null) ...[
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: [Color(0xFFE0E7FF), Color(0xFFC7D2FE)],
                  ),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: const Color(0xFF8B5CF6), width: 1),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        const Icon(Icons.auto_awesome, size: 16, color: Color(0xFF8B5CF6)),
                        const SizedBox(width: 8),
                        Text(
                          l10n.aiGeneratedTitle,
                          style: const TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w600,
                            color: Color(0xFF8B5CF6),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Text(
                      _aiGeneratedTitle!,
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFF8B5CF6),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),
            ],
            
            // Description Input
            Container(
              decoration: BoxDecoration(
                border: Border.all(color: const Color(0xFFE2E8F0)),
                borderRadius: BorderRadius.circular(16),
                color: const Color(0xFFF8FAFC),
              ),
              child: Column(
                children: [
                  TextField(
                    controller: _desc,
                    maxLines: 6,
                    decoration: InputDecoration(
                      hintText: l10n.describeIssueDetail,
                      border: InputBorder.none,
                      contentPadding: const EdgeInsets.all(20),
                    ),
                    style: const TextStyle(fontSize: 16),
                  ),
                  Container(
                    padding: const EdgeInsets.fromLTRB(16, 8, 16, 16),
                    child: Row(
                      children: [
                        _buildAutoGenerateButton(),
                        const Spacer(),
                        _buildActionIcon(Icons.mic, () {
                          final l10n = AppLocalizations.of(context)!;
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(content: Text(l10n.voiceRecordingComingSoon)),
                          );
                        }),
                        const SizedBox(width: 8),
                        _buildActionIcon(Icons.send, () {
                          final l10n = AppLocalizations.of(context)!;
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(content: Text(l10n.sendFunctionalityComingSoon)),
                          );
                        }),
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

  Widget _buildAutoGenerateButton() {
    final l10n = AppLocalizations.of(context)!;
    return MouseRegion(
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
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
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
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
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
                  _isGeneratingDescription ? l10n.generating : l10n.autoGenerate,
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
    );
  }

  Widget _buildActionIcon(IconData icon, VoidCallback onPressed) {
    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFFF1F5F9),
        borderRadius: BorderRadius.circular(20),
      ),
      child: IconButton(
        onPressed: onPressed,
        icon: Icon(icon, size: 20, color: const Color(0xFF64748B)),
        padding: const EdgeInsets.all(8),
        constraints: const BoxConstraints(
          minWidth: 36,
          minHeight: 36,
        ),
      ),
    );
  }

  Widget _buildLocationSection() {
    final l10n = AppLocalizations.of(context)!;
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 20,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: const Color(0xFF10B981).withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Icon(
                    Icons.location_on,
                    color: Color(0xFF10B981),
                    size: 20,
                  ),
                ),
                const SizedBox(width: 12),
                Text(
                  l10n.location,
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF1E293B),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            
            // GPS Location Display
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: const Color(0xFFF8FAFC),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: const Color(0xFFE2E8F0)),
              ),
              child: Row(
                children: [
                  const Icon(Icons.gps_fixed, size: 20, color: Color(0xFF64748B)),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      _address != null ? '$_address\n($_locationString)' : _locationString,
                      style: const TextStyle(fontSize: 16, color: Color(0xFF475569)),
                    ),
                  ),
                  IconButton(
                    onPressed: _getCurrentLocation,
                    icon: const Icon(Icons.refresh, size: 20, color: Color(0xFF10B981)),
                    tooltip: l10n.refreshLocation,
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),
            
            // Manual Location Input
            TextField(
              controller: _locationManual,
              decoration: InputDecoration(
                labelText: l10n.manualLocation,
                hintText: l10n.enterSpecificAddress,
                filled: true,
                fillColor: const Color(0xFFF8FAFC),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: const BorderSide(color: Color(0xFFE2E8F0)),
                ),
                enabledBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: const BorderSide(color: Color(0xFFE2E8F0)),
                ),
                focusedBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: const BorderSide(color: Color(0xFF10B981)),
                ),
                contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSubmitButton() {
    final l10n = AppLocalizations.of(context)!;
    return Container(
      width: double.infinity,
      height: 56,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF3B82F6).withOpacity(0.3),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: ElevatedButton(
        onPressed: _isUploading ? null : _generatePDF,
        style: ElevatedButton.styleFrom(
          backgroundColor: const Color(0xFF3B82F6),
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
            : Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.send, size: 24),
                  const SizedBox(width: 8),
                  Text(l10n.submitComplaintButton, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                ],
              ),
      ),
    );
  }

  Widget _buildActionButton({
    required IconData icon,
    required String label,
    required VoidCallback onPressed,
    required Color color,
    bool isCompact = false,
  }) {
    return ElevatedButton.icon(
      onPressed: onPressed,
      icon: Icon(icon, size: isCompact ? 16 : 20),
      label: Text(
        label,
        style: TextStyle(fontSize: isCompact ? 12 : 14, fontWeight: FontWeight.w600),
      ),
      style: ElevatedButton.styleFrom(
        backgroundColor: color,
        foregroundColor: Colors.white,
        padding: EdgeInsets.symmetric(
          vertical: isCompact ? 8 : 12,
          horizontal: isCompact ? 12 : 16,
        ),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        elevation: 0,
      ),
    );
  }

  Widget _buildProcessingOverlay() {
    final l10n = AppLocalizations.of(context)!;
    return Positioned.fill(
      child: Container(
        color: Colors.black.withOpacity(0.5),
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const SizedBox(
                width: 48,
                height: 48,
                child: CircularProgressIndicator(
                  strokeWidth: 4,
                  valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                ),
              ),
              const SizedBox(height: 16),
              Text(
                l10n.processing,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 16,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildPermissionsOverlay() {
    final l10n = AppLocalizations.of(context)!;
    return Positioned.fill(
      child: Container(
        color: Colors.black.withOpacity(0.5),
        child: Center(
          child: Container(
            margin: const EdgeInsets.all(20),
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(20),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.1),
                  blurRadius: 20,
                  offset: const Offset(0, 8),
                ),
              ],
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: const Color(0xFFEF4444).withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Icon(
                    Icons.privacy_tip,
                    color: Color(0xFFEF4444),
                    size: 48,
                  ),
                ),
                const SizedBox(height: 20),
                Text(
                  l10n.permissionsRequired,
                  style: const TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF1E293B),
                  ),
                ),
                const SizedBox(height: 12),
                Text(
                  l10n.cameraLocationPermissionsNeeded,
                  textAlign: TextAlign.center,
                  style: const TextStyle(
                    fontSize: 16,
                    color: Color(0xFF64748B),
                  ),
                ),
                const SizedBox(height: 24),
                Row(
                  children: [
                    Expanded(
                      child: OutlinedButton(
                        onPressed: () => Navigator.pop(context),
                        style: OutlinedButton.styleFrom(
                          side: const BorderSide(color: Color(0xFFE2E8F0)),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                          padding: const EdgeInsets.symmetric(vertical: 12),
                        ),
                        child: Text(
                          l10n.cancel,
                          style: const TextStyle(color: Color(0xFF64748B)),
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: ElevatedButton(
                        onPressed: () async {
                          await openAppSettings();
                          setState(() => _permissionsDenied = false);
                        },
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF3B82F6),
                          foregroundColor: Colors.white,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                          padding: const EdgeInsets.symmetric(vertical: 12),
                        ),
                        child: Text(l10n.openSettings),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildLanguageSwitcher() {
    return Consumer<LocaleProvider>(
      builder: (context, localeProvider, child) {
        return PopupMenuButton<String>(
          icon: const Icon(Icons.language, size: 24),
          tooltip: 'Change Language',
          onSelected: (String languageCode) {
            localeProvider.setLocale(Locale(languageCode));
          },
          itemBuilder: (BuildContext context) => [
            PopupMenuItem<String>(
              value: 'en',
              child: Row(
                children: [
                  const Icon(Icons.language, size: 16),
                  const SizedBox(width: 8),
                  Text(localeProvider.languageCode == 'en' ? 'English ✓' : 'English'),
                ],
              ),
            ),
            PopupMenuItem<String>(
              value: 'hi',
              child: Row(
                children: [
                  const Icon(Icons.language, size: 16),
                  const SizedBox(width: 8),
                  Text(localeProvider.languageCode == 'hi' ? 'हिंदी ✓' : 'हिंदी'),
                ],
              ),
            ),
            PopupMenuItem<String>(
              value: 'mr',
              child: Row(
                children: [
                  const Icon(Icons.language, size: 16),
                  const SizedBox(width: 8),
                  Text(localeProvider.languageCode == 'mr' ? 'मराठी ✓' : 'मराठी'),
                ],
              ),
            ),
          ],
        );
      },
    );
  }

  void _showHelpDialog() {
    final l10n = AppLocalizations.of(context)!;
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: Text(l10n.howToReportIssue),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(l10n.step1),
            const SizedBox(height: 8),
            Text(l10n.step2),
            const SizedBox(height: 8),
            Text(l10n.step3),
            const SizedBox(height: 8),
            Text(l10n.step4),
            const SizedBox(height: 16),
            Text(
              l10n.reportForwarded,
              style: const TextStyle(fontStyle: FontStyle.italic),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text(l10n.gotIt),
          ),
        ],
      ),
    );
  }
}