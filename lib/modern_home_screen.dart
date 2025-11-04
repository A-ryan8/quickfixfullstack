import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:firebase_auth/firebase_auth.dart';

class ModernHomeScreen extends StatefulWidget {
  const ModernHomeScreen({super.key});

  @override
  State<ModernHomeScreen> createState() => _ModernHomeScreenState();
}

class _ModernHomeScreenState extends State<ModernHomeScreen> {
  bool _isDarkMode = false;
  bool _isLoading = true;
  List<ComplaintItem> _complaints = [];
  String? _apiBase; // e.g. http://10.0.2.2:8000 or http://localhost:8000

  @override
  void initState() {
    super.initState();
    _fetchComplaints();
  }

  Future<void> _fetchComplaints() async {
    final urls = <String>[
      'http://10.45.233.189:8000/api/complaints/public',
      'http://10.0.2.2:8000/api/complaints/public',
      'http://localhost:8000/api/complaints/public',
      'http://127.0.0.1:8000/api/complaints/public',
    ];

    for (final url in urls) {
      try {
        final res = await http.get(Uri.parse(url));
        debugPrint('Fetch URL: $url');
        debugPrint('Status: ${res.statusCode}');
        debugPrint('Server Response: ${res.body}');
        if (res.statusCode == 200) {
          // Capture base from the successful URL (strip trailing /api/complaints)
          final idx = url.indexOf('/api/');
          _apiBase = idx > 0 ? url.substring(0, idx) : null;
          debugPrint('Selected API base: $_apiBase');

          final List<dynamic> data = jsonDecode(res.body) as List<dynamic>;
          debugPrint('Decoded list length: ${data.length}');
          if (data.isNotEmpty) {
            final sample = data.first;
            debugPrint('Sample item keys: ${sample is Map ? (sample as Map).keys.join(',') : sample.runtimeType}');
          }

          final mapped = data.map((raw) {
            final Map<String, dynamic> c = raw as Map<String, dynamic>;
            String? rawTitle = (c['title'] as String?) ?? (c['aiTitle'] as String?);
            final String title = (rawTitle?.trim().isNotEmpty == true) ? rawTitle! : 'Reported Issue';
            final String description = (c['description'] as String?) ?? (c['aiDescription'] as String?) ?? '';
            final String status = (c['status'] as String?) ?? 'New';
            final String rawImage = (c['imageUrl'] as String?)
                ?? (c['image_url'] as String?)
                ?? (c['imageURL'] as String?)
                ?? '';
            final String imageUrl = _resolveImageUrl(rawImage);
            final dynamic createdRaw = c.containsKey('created_at') ? c['created_at'] : c['createdAt'];
            final int votes = (c['upvote_count'] is int)
                ? c['upvote_count'] as int
                : (c['upvotes'] is int ? c['upvotes'] as int : 0);

            return ComplaintItem(
              id: (c['id'] ?? c['complaintId'] ?? '').toString(),
              title: title,
              description: description,
              status: status,
              imageUrl: imageUrl,
              timeAgo: _computeTimeAgo(createdRaw),
              reporterName: 'Citizen',
              location: (c['location'] as String?) ?? '',
              votes: votes,
            );
          }).toList();

          if (!mounted) return;
          setState(() {
            _complaints = mapped;
            _isLoading = false;
          });
          return;
        }
      } catch (e) {
        debugPrint('Error fetching complaints: $e');
      }
    }

    if (!mounted) return;
    setState(() {
      _complaints = [];
      _isLoading = false;
    });
  }

  String _resolveImageUrl(String raw) {
    if (raw.isEmpty) return '';
    if (raw.startsWith('http')) return raw;
    final cleaned = raw.replaceFirst(RegExp(r'^/'), '');
    final base = _apiBase ?? 'http://localhost:8000';
    final full = base + '/' + cleaned;
    debugPrint('Resolved image URL: $full');
    return full;
  }

  String _computeTimeAgo(dynamic createdAt) {
    try {
      if (createdAt == null) return '';
      final dt = DateTime.tryParse(createdAt.toString());
      if (dt == null) return '';
      final diff = DateTime.now().difference(dt);
      if (diff.inMinutes < 60) return '${diff.inMinutes}m ago';
      if (diff.inHours < 24) return '${diff.inHours}h ago';
      return '${diff.inDays}d ago';
    } catch (_) {
      return '';
    }
  }

  Future<void> _handleUpvote(String id) async {
    try {
      // Get the current user's ID from Firebase Authentication
      final user = FirebaseAuth.instance.currentUser;
      if (user == null) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Please log in to upvote complaints'),
              backgroundColor: Colors.red,
            ),
          );
        }
        return;
      }

      final userId = user.uid;
      
      // Try different API base URLs
      final bases = <String>[
        _apiBase ?? '',
        'http://10.45.233.189:8000',
        'http://10.0.2.2:8000',
        'http://localhost:8000',
        'http://127.0.0.1:8000',
      ].where((b) => b.isNotEmpty).toList();
      
      bool success = false;
      String? errorMessage;
      
      for (final base in bases) {
        final endpoint = base + '/api/complaints/' + id + '/upvote/public';
        try {
          final response = await http.post(
            Uri.parse(endpoint),
            headers: {
              'Content-Type': 'application/json',
            },
            body: jsonEncode({
              'user_id': userId,
            }),
          );
          
          if (response.statusCode == 200) {
            success = true;
            if (mounted) {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Upvoted successfully!'),
                  backgroundColor: Colors.green,
                ),
              );
            }
            break;
          } else if (response.statusCode == 409) {
            // User has already upvoted
            if (mounted) {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('You have already upvoted this complaint'),
                  backgroundColor: Colors.orange,
                ),
              );
            }
            success = true; // This is expected behavior, not an error
            break;
          } else {
            // Try to parse error message
            try {
              final errorData = jsonDecode(response.body);
              errorMessage = errorData['detail'] ?? 'Unknown error';
            } catch (_) {
              errorMessage = 'Server error: ${response.statusCode}';
            }
          }
        } catch (e) {
          errorMessage = 'Network error: $e';
          continue; // Try next base URL
        }
      }
      
      if (!success && errorMessage != null) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Failed to upvote: $errorMessage'),
              backgroundColor: Colors.red,
            ),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        await _fetchComplaints();
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = _isDarkMode ? ThemeData.dark() : ThemeData.light();

    return Theme(
      data: theme,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('QuickFix'),
          backgroundColor: _isDarkMode ? const Color(0xFF1E1E1E) : Colors.white,
          foregroundColor: _isDarkMode ? Colors.white : Colors.black,
          elevation: 0,
          actions: [
            IconButton(
              tooltip: _isDarkMode ? 'Light mode' : 'Dark mode',
              onPressed: () => setState(() => _isDarkMode = !_isDarkMode),
              icon: Icon(_isDarkMode ? Icons.sunny : Icons.nightlight_round),
            ),
            IconButton(
              tooltip: 'Settings',
              onPressed: () {},
              icon: const Icon(Icons.settings),
            ),
          ],
        ),
        body: ListView(
          padding: const EdgeInsets.only(bottom: 16),
          children: [
            if (_isLoading)
              const Padding(
                padding: EdgeInsets.only(top: 60),
                child: Center(child: CircularProgressIndicator()),
              )
            else if (_complaints.isEmpty)
              Padding(
                padding: const EdgeInsets.all(24),
                child: Column(
                  children: [
                    Icon(
                      Icons.inbox_outlined,
                      size: 48,
                      color: _isDarkMode ? Colors.white30 : Colors.grey,
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'No complaints yet',
                      style: TextStyle(
                        fontSize: 16,
                        color: _isDarkMode ? Colors.white70 : Colors.black54,
                      ),
                    ),
                  ],
                ),
              )
            else
              ListView.builder(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                itemCount: _complaints.length,
                itemBuilder: (context, index) {
                  final item = _complaints[index];
                  return ComplaintCard(
                    item: item,
                    isDarkMode: _isDarkMode,
                    onUpvote: () => _handleUpvote(item.id),
                  );
                },
              ),
          ],
        ),
      ),
    );
  }
}

class ComplaintItem {
  final String id;
  final String title;
  final String description;
  final String status;
  final String imageUrl; // full URL now
  final String timeAgo;
  final String reporterName;
  final String location;
  final int votes;

  ComplaintItem({
    required this.id,
    required this.title,
    required this.description,
    required this.status,
    required this.imageUrl,
    required this.timeAgo,
    required this.reporterName,
    required this.location,
    required this.votes,
  });
}

class ComplaintCard extends StatefulWidget {
  final ComplaintItem item;
  final bool isDarkMode;
  final Future<void> Function()? onUpvote;

  const ComplaintCard({super.key, required this.item, this.isDarkMode = false, this.onUpvote});

  @override
  State<ComplaintCard> createState() => _ComplaintCardState();
}

class _ComplaintCardState extends State<ComplaintCard> {
  bool _isExpanded = false;
  late int _voteCount;

  @override
  void initState() {
    super.initState();
    _voteCount = widget.item.votes;
  }

  Color _urgencyColor(String status) {
    switch (status) {
      case 'In Progress':
        return Colors.orange;
      case 'Resolved':
        return Colors.green;
      case 'New':
        return Colors.red;
      default:
        return Colors.blueGrey;
    }
  }

  String _urgencyLabel(String status) {
    switch (status) {
      case 'In Progress':
        return 'Medium';
      case 'Resolved':
        return 'Low';
      case 'New':
        return 'High';
      default:
        return status.isEmpty ? 'Info' : status;
    }
  }

  @override
  Widget build(BuildContext context) {
    final Color textColor = widget.isDarkMode ? Colors.white : Colors.black;
    final Color secondaryText = widget.isDarkMode ? Colors.white70 : Colors.black87;

    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      elevation: 3,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.all(12),
            child: Row(
              children: [
                CircleAvatar(
                  radius: 20,
                  backgroundColor: const Color(0xFF1976D2).withOpacity(0.1),
                  child: Text(
                    widget.item.reporterName.isNotEmpty ? widget.item.reporterName[0].toUpperCase() : 'U',
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF1976D2),
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        widget.item.reporterName,
                        style: TextStyle(
                          fontWeight: FontWeight.w600,
                          fontSize: 14,
                          color: textColor,
                        ),
                      ),
                      Row(
                        children: [
                          Icon(Icons.access_time, size: 12, color: Colors.grey.shade600),
                          const SizedBox(width: 4),
                          Text(
                            widget.item.timeAgo,
                            style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
                IconButton(
                  onPressed: () {},
                  icon: Icon(Icons.more_vert, color: Colors.grey.shade700),
                ),
              ],
            ),
          ),
          AspectRatio(
            aspectRatio: 16 / 9,
            child: widget.item.imageUrl.isNotEmpty
                ? Image.network(
                    widget.item.imageUrl,
                    fit: BoxFit.cover,
                    errorBuilder: (context, error, stack) {
                      return Container(
                        color: widget.isDarkMode ? Colors.grey.shade800 : Colors.grey.shade200,
                        child: const Center(
                          child: Icon(Icons.broken_image, size: 40, color: Colors.grey),
                        ),
                      );
                    },
                  )
                : Container(
                    color: widget.isDarkMode ? Colors.grey.shade800 : Colors.grey.shade200,
                    child: const Center(
                      child: Icon(Icons.image, size: 40, color: Colors.grey),
                    ),
                  ),
          ),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            child: Row(
              children: [
                IconButton(
                  onPressed: () async {
                    setState(() => _voteCount += 1);
                    try {
                      if (widget.onUpvote != null) await widget.onUpvote!();
                    } catch (_) {}
                  },
                  icon: Icon(Icons.thumb_up_alt_outlined, color: Colors.grey.shade700),
                ),
                Text('$_voteCount', style: TextStyle(color: Colors.grey.shade700)),
                const SizedBox(width: 8),
                IconButton(
                  onPressed: () {},
                  icon: Icon(Icons.mode_comment_outlined, color: Colors.grey.shade700),
                ),
                const SizedBox(width: 4),
                IconButton(
                  onPressed: () {},
                  icon: Icon(Icons.share_outlined, color: Colors.grey.shade700),
                ),
                const Spacer(),
                Chip(
                  label: Text(
                    _urgencyLabel(widget.item.status),
                    style: TextStyle(color: _urgencyColor(widget.item.status)),
                  ),
                  backgroundColor: _urgencyColor(widget.item.status).withOpacity(0.12),
                  shape: StadiumBorder(side: BorderSide(color: _urgencyColor(widget.item.status).withOpacity(0.3))),
                ),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.fromLTRB(12, 0, 12, 14),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (widget.item.title.isNotEmpty) ...[
                  Text(
                    widget.item.title,
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                      color: textColor,
                    ),
                  ),
                  const SizedBox(height: 6),
                ],
                Text(
                  widget.item.description.isNotEmpty ? widget.item.description : widget.item.title,
                  style: TextStyle(color: secondaryText, fontSize: 14, height: 1.35),
                  maxLines: _isExpanded ? null : 2,
                  overflow: _isExpanded ? TextOverflow.visible : TextOverflow.ellipsis,
                ),
                const SizedBox(height: 4),
                Align(
                  alignment: Alignment.centerLeft,
                  child: TextButton(
                    onPressed: () => setState(() => _isExpanded = !_isExpanded),
                    child: Text(_isExpanded ? 'Read Less' : 'Read More'),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

