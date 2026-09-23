import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';

class DashboardFirebaseService {
  static final FirebaseFirestore _firestore = FirebaseFirestore.instance;

  static Future<void> saveLatestDashboardSnapshot({
    required Map<String, dynamic> trafficData,
    required Map<String, dynamic> systemData,
    required bool apiOnline,
    required String apiError,
  }) async {
    try {
      final user = FirebaseAuth.instance.currentUser;
      final timestamp = DateTime.now().toUtc();
      final payload = {
        'userId': user?.uid ?? 'anonymous',
        'email': user?.email ?? 'demo@smarttrafficai.local',
        'timestamp': Timestamp.fromDate(timestamp),
        'apiOnline': apiOnline,
        'apiError': apiError,
        'system': systemData,
        'traffic': trafficData,
        'updatedAt': FieldValue.serverTimestamp(),
      };

      final latestRef = _firestore.collection('dashboard_snapshots').doc('latest');
      final historyRef = _firestore
          .collection('dashboard_snapshots')
          .doc('history')
          .collection('entries')
          .doc(timestamp.millisecondsSinceEpoch.toString());

      final batch = _firestore.batch();
      batch.set(latestRef, payload);
      batch.set(historyRef, payload);
      await batch.commit();
    } catch (e) {
      // Ignore storage failures so the app keeps running and the dashboard remains usable.
      // The Firebase console can be used to see the last successful write.
      print('Dashboard Firebase save failed: $e');
    }
  }
}
