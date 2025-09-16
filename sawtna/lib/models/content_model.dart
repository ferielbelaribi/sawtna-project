class GeneratedContent {
  final int id;
  final int userId;
  final String contentType;
  final String? title;
  final String? text;
  final String? imagePath;
  final DateTime createdAt;

  GeneratedContent({
    required this.id,
    required this.userId,
    required this.contentType,
    this.title,
    this.text,
    this.imagePath,
    required this.createdAt,
  });

  factory GeneratedContent.fromJson(Map<String, dynamic> json) {
    return GeneratedContent(
      id: json['id'],
      userId: json['user_id'],
      contentType: json['content_type'],
      title: json['title'],
      text: json['text'],
      imagePath: json['image_path'],
      createdAt: DateTime.parse(json['created_at']),
    );
  }

  String get preview {
    if (text != null && text!.isNotEmpty) {
      return text!.length > 50 ? '${text!.substring(0, 50)}...' : text!;
    } else if (imagePath != null) {
      return 'Image Content';
    }
    return 'No content preview';
  }

  String get typeIcon {
    switch (contentType) {
      case 'text':
        return '📝';
      case 'image':
        return '🖼️';
      case 'compliance_check':
        return '✅';
      default:
        return '📄';
    }
  }
}