import 'dart:io';
import 'dart:typed_data';
import 'dart:convert';
import 'package:pdf/pdf.dart';
import 'package:pdf/widgets.dart' as pw;

class PdfService {
  /// Generates a professional PDF report for civic complaints
  /// Returns the PDF bytes for saving or preview
  static Future<Uint8List> generateComplaintReport({
    required String username,
    required String location,
    required String description,
    required String? detailedAddress,
    required String? aiTitle,
    required String? aiDescription,
    File? imageFile,
  }) async {
    final pdf = pw.Document();
    
    // Prepare image data if available
    pw.MemoryImage? image;
    bool hasImage = false;
    
    if (imageFile != null) {
      try {
        final imageBytes = await imageFile.readAsBytes();
        if (imageBytes.isNotEmpty) {
          image = pw.MemoryImage(imageBytes);
          hasImage = true;
        }
      } catch (e) {
        print('Error loading image for PDF: $e');
      }
    }
    
    // AI title and description are now passed directly as parameters
    print('PDF Service - AI Title: $aiTitle');
    print('PDF Service - AI Description: $aiDescription');
    
    // Get current date and time
    final now = DateTime.now();
    final formattedDate = '${now.day}/${now.month}/${now.year} at ${now.hour.toString().padLeft(2, '0')}:${now.minute.toString().padLeft(2, '0')}';
    
    pdf.addPage(
      pw.MultiPage(
        pageFormat: PdfPageFormat.a4,
        margin: const pw.EdgeInsets.all(40),
        
        // Professional Header
        header: (pw.Context context) {
          return pw.Container(
            margin: const pw.EdgeInsets.only(bottom: 20),
            child: pw.Row(
              mainAxisAlignment: pw.MainAxisAlignment.spaceBetween,
              children: [
                pw.Text(
                  'Civic Issue Report',
                  style: pw.TextStyle(
                    fontWeight: pw.FontWeight.bold,
                    fontSize: 24,
                    color: PdfColors.blue800,
                  ),
                ),
                pw.Column(
                  crossAxisAlignment: pw.CrossAxisAlignment.end,
                  children: [
                    pw.Text(
                      'QuickFix App',
                      style: pw.TextStyle(
                        fontSize: 12,
                        color: PdfColors.grey600,
                      ),
                    ),
                    pw.Text(
                      'Generated: $formattedDate',
                      style: pw.TextStyle(
                        fontSize: 10,
                        color: PdfColors.grey500,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          );
        },
        
        // Main Content
        build: (pw.Context context) {
          return [
            // Report Summary Section
            pw.Text(
              'Report Summary',
              style: pw.TextStyle(
                fontSize: 18,
                fontWeight: pw.FontWeight.bold,
                color: PdfColors.blue700,
              ),
            ),
            pw.SizedBox(height: 10),
            
            // Summary table
            pw.Table(
              border: pw.TableBorder.all(color: PdfColors.grey300),
              children: [
                _buildTableRow('Date & Time', formattedDate),
                _buildTableRow('Location', detailedAddress ?? location),
                _buildTableRow('Coordinates', location),
                _buildTableRow('Submitted By', username),
              ],
            ),
            pw.SizedBox(height: 20),
            
            // Visual Evidence Section
            if (hasImage && image != null) ...[
              pw.Text(
                'Visual Evidence',
                style: pw.TextStyle(
                  fontSize: 18,
                  fontWeight: pw.FontWeight.bold,
                  color: PdfColors.blue700,
                ),
              ),
              pw.SizedBox(height: 10),
              pw.Center(
                child: pw.Container(
                  constraints: const pw.BoxConstraints(
                    maxWidth: 400,
                    maxHeight: 300,
                  ),
                  decoration: pw.BoxDecoration(
                    border: pw.Border.all(color: PdfColors.grey400),
                    borderRadius: pw.BorderRadius.circular(8),
                  ),
                  child: pw.Image(
                    image!,
                    fit: pw.BoxFit.contain,
                  ),
                ),
              ),
              pw.SizedBox(height: 20),
            ],
            
            // AI-Generated Title Section
            if (aiTitle != null && aiTitle.isNotEmpty) ...[
              pw.Text(
                'Issue Classification',
                style: pw.TextStyle(
                  fontSize: 18,
                  fontWeight: pw.FontWeight.bold,
                  color: PdfColors.blue700,
                ),
              ),
              pw.SizedBox(height: 10),
              pw.Container(
                padding: const pw.EdgeInsets.all(12),
                decoration: pw.BoxDecoration(
                  color: PdfColors.blue50,
                  border: pw.Border.all(color: PdfColors.blue200),
                  borderRadius: pw.BorderRadius.circular(8),
                ),
                child: pw.Text(
                  aiTitle,
                  style: pw.TextStyle(
                    fontSize: 14,
                    fontWeight: pw.FontWeight.bold,
                    color: PdfColors.blue800,
                  ),
                ),
              ),
              pw.SizedBox(height: 20),
            ],
            
            // Detailed Analysis Section
            pw.Text(
              'Detailed Analysis',
              style: pw.TextStyle(
                fontSize: 18,
                fontWeight: pw.FontWeight.bold,
                color: PdfColors.blue700,
              ),
            ),
            pw.SizedBox(height: 10),
            
            // AI-Generated Title (if available)
            if (aiTitle != null && aiTitle.isNotEmpty) ...[
              pw.Text(
                aiTitle,
                style: pw.TextStyle(
                  fontSize: 18,
                  fontWeight: pw.FontWeight.bold,
                  color: PdfColors.blue800,
                ),
              ),
              pw.SizedBox(height: 10),
            ],
            
            // AI-Generated Description or fallback to original description
            pw.Paragraph(
              text: (aiDescription != null && aiDescription.isNotEmpty)
                  ? aiDescription
                  : (description.isNotEmpty 
                      ? description 
                      : 'No detailed description provided.'),
              style: pw.TextStyle(
                fontSize: 12,
                lineSpacing: 1.5,
              ),
            ),
          ];
        },
        
        // Clean Footer
        footer: (pw.Context context) {
          return pw.Container(
            margin: const pw.EdgeInsets.only(top: 20),
            padding: const pw.EdgeInsets.symmetric(vertical: 10),
            decoration: const pw.BoxDecoration(
              border: pw.Border(
                top: pw.BorderSide(color: PdfColors.grey300),
              ),
            ),
            child: pw.Row(
              mainAxisAlignment: pw.MainAxisAlignment.spaceBetween,
              children: [
                pw.Text(
                  'Generated by QuickFix App',
                  style: pw.TextStyle(
                    fontSize: 10,
                    color: PdfColors.grey600,
                  ),
                ),
                pw.Text(
                  'Page ${context.pageNumber} of ${context.pagesCount}',
                  style: pw.TextStyle(
                    fontSize: 10,
                    color: PdfColors.grey600,
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
    
    return await pdf.save();
  }
  
  /// Helper method to build table rows with proper styling
  static pw.TableRow _buildTableRow(String label, String value) {
    return pw.TableRow(
      decoration: const pw.BoxDecoration(
        color: PdfColors.grey50,
      ),
      children: [
        pw.Padding(
          padding: const pw.EdgeInsets.all(8),
          child: pw.Text(
            label,
            style: pw.TextStyle(
              fontWeight: pw.FontWeight.bold,
              fontSize: 12,
            ),
          ),
        ),
        pw.Padding(
          padding: const pw.EdgeInsets.all(8),
          child: pw.Text(
            value,
            style: const pw.TextStyle(fontSize: 12),
          ),
        ),
      ],
    );
  }
}
